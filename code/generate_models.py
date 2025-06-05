#!/usr/bin/env python
"""Generate a set of time shifting models from the given period of years. Each
one of the models spans a given number of years.
"""
import csv
from os.path import join
import os

import click
from gensim.models.word2vec import Word2Vec
from gensim.models import KeyedVectors
from gensim.scripts.glove2word2vec import glove2word2vec
from gensim.test.utils import get_tmpfile
from sklearn.feature_extraction.text import CountVectorizer

from collect_sentences import DataCollector
from corpus_config import CORPUS_CONFIGURATIONS
from analyzer import Analyzer
from util import check_path, CorpusConfigurationException
import ppmi

import logging
logging.basicConfig(filename='models.log', level=logging.WARNING, filemode='a', datefmt='%Y-%m-%d %H:%M:%S', 
    format='%(asctime)s %(levelname)-8s %(message)s')
logger = logging.getLogger(__name__)

MIN_COUNT = 80
N_DIMS = 100
WINDOW_SIZE = 5


@click.command()
@click.option(
    '-c', '--corpus', help="Name of the corpus configuration object", required=True
)
@click.option(
    '-s',
    '--start_year',
    help="Year from which to start training",
    type=int,
    required=True,
)
@click.option(
    '-e',
    '--end_year',
    help="Year until which to continue training",
    type=int,
    required=True,
)
@click.option(
    '-n',
    '--n_years',
    help="Number of years each model should span",
    type=int,
    default=10,
)
@click.option('-sh', '--shift_years', help="Shift between models", type=int, default=5)
@click.option(
    '-md',
    '--model_directory',
    help="Directory in which the models should be saved",
    required=True,
)
@click.option(
    '-sd',
    '--source_directory',
    help="Directory in which the source data should be saved",
    default='source_data',
)
def generate_models(
    corpus,
    start_year,
    end_year,
    n_years,
    shift_years,
    model_directory,
    source_directory,
):
    """Generate time shifting w2v models on the given time range (start_year - end_year).
    Each model contains the specified number of years (years_in_model). The start
    year of each new model is set to be shift_years after the previous model.
    Resulting models are saved in the specified output directory.
    Generates the following files:
    - a full model file ('*full.model')
    - the word vectors (gensim KeyedVectors) of the full model ('*full.wv')
    - a file of statistics on each time slice ('*stats.csv'):
        - the number of tokens (after preprocessing such as stopword removal)
        - the number of terms (i.e., distinct words)
    - for each time bin:
        - its word vectors (gensim KeyedVectors) ('*start-end.wv')
    The statistics are saved to the model folder as a .csv
    """
    check_path(model_directory)
    corpus_config = CORPUS_CONFIGURATIONS.get(corpus)
    if not corpus_config:
        raise CorpusConfigurationException(
            "CORPUS_CONFIGURATIONS does not contain specs for this corpus."
        )
    valid_keys = [
        'algorithm',
        'date_field',
        'independent',
        'language',
        'lemmatize',
        'min_count',
        'max_vocab',
        'max_final_vocab',
        'text_field',
        'vector_size',
        'window_size',
    ]
    invalid_keys = set(corpus_config.keys()).issubset(set(valid_keys))
    if invalid_keys:
        raise CorpusConfigurationException(
            f"The following keys are invalid: {', '.join(invalid_keys)}"
        )
    analyzer = Analyzer(corpus_config).preprocess
    algorithm = corpus_config.get('algorithm', 'word2vec')
    independent = corpus_config.get('independent', True)
    sentences = DataCollector(corpus, start_year, end_year, analyzer, source_directory)
    full_model_name = '{}_{}_{}_full'.format(corpus, start_year, end_year)
    full_model_file = '{}.model'.format(full_model_name)
    if not os.path.exists(join(model_directory, full_model_file)) and not independent:
        # skip this step when training independent models
        if algorithm == 'word2vec':
            model = get_model(
                sentences,
                corpus_config.get('min_count'),
                corpus_config.get('window_size', WINDOW_SIZE),
                corpus_config.get('vector_size', N_DIMS),
                corpus_config.get('max_vocab_size'),
                corpus_config.get('max_final_vocab')
            )
            model.train(sentences, total_examples=model.corpus_count,
                        epochs=model.epochs)
            model.save(join(model_directory, full_model_file))
        elif algorithm == 'ppmi':
            model = train_ppmi(
                list(sentences), corpus_config.get('vector_size', N_DIMS)
            )
        else:
            logger.error(
                'unknown training algorithm specified, choose `word2vec` or `ppmi`')
            return
        model.wv.save(
            join(model_directory, '{}.wv'.format(full_model_name))
        )

    stats = []
    for year in range(start_year, end_year - n_years + 1, shift_years):
        start = year
        end = year + n_years
        model_name = '{}_{}_{}.wv'.format(corpus, start, end)
        logger.info('Building model: '+ model_name)
        sentences = DataCollector(corpus, start, end, analyzer, source_directory)
        if algorithm == 'word2vec':
            if independent:
                model = get_model(
                    sentences,
                    corpus_config.get('min_count', MIN_COUNT),
                    corpus_config.get('window_size', WINDOW_SIZE),
                    corpus_config.get('vector_size', N_DIMS),
                    corpus_config.get('max_vocab_size'),
                    corpus_config.get('max_final_vocab')
                )
            else:
                model = Word2Vec.load(join(model_directory, full_model_file))
            _output, n_tokens = model.train(sentences, start_alpha=.05,
                        total_examples=len(list(sentences)), epochs=model.epochs)
        elif algorithm == 'ppmi':
            model, n_tokens = train_ppmi(
                list(sentences), corpus_config.get('vector_size', N_DIMS)
            )
        else:
            logger.error(
                'unknown training algorithm specified, choose `word2vec` or `ppmi`')
            return
        saved_vectors, n_terms, n_tokens = get_vectors_and_stats(
            model, sentences, n_tokens, independent
        )
        stats.append({
            'time': '{}-{}'.format(start, end),
            'n_tokens': n_tokens,
            'n_terms': n_terms})
        saved_vectors.save(join(model_directory, model_name))

    with open(join(model_directory, '{}_stats.csv'.format(full_model_name)), 'w+') as f:
        writer = csv.DictWriter(f, fieldnames=('time', 'n_tokens', 'n_terms'))
        writer.writeheader()
        writer.writerows(stats)


def get_model(sentences, min_count: int, window_size: int, vector_size: int, max_vocab_size: int, max_final_vocab: int):
    ''' prepare a Word2Vec model and build its vocabulary '''
    model = Word2Vec(
        min_count=min_count,
        window=window_size,
        vector_size=vector_size,
        max_vocab_size=max_vocab_size,
        max_final_vocab=max_final_vocab
    )
    model.build_vocab(sentences)
    return model


def get_vectors_and_stats(model, sentences, n_tokens, independent: bool):
    ''' return the word vectors of a model, and statistics on the number of terms and tokens '''
    if independent:
        vocab = model.wv.index_to_key
        n_terms = len(vocab)
        output_vectors = model.wv
    else:
        cv = CountVectorizer(analyzer=lambda x: x)
        doc_term = cv.fit_transform(sentences)
        cv_vocab = cv.get_feature_names_out()
        n_terms = len(cv_vocab)
        n_tokens = doc_term.sum()
        vectors = model.wv
        vocab = list(set(vectors.index_to_key).intersection(set(cv_vocab)))
        # restrict the KeyedVectors to only those in the vocab of this time slice
        output_vectors = KeyedVectors(model.vector_size)
        output_vectors.add_vectors(
            vocab, [vectors[word] for word in vocab])
    return output_vectors, n_terms, n_tokens


def train_ppmi(docs, vector_size):
    transformer, counts = ppmi.count_words(docs)
    ppmi_counts = ppmi.ppmi(counts)
    weights = ppmi.svd_ppmi(ppmi_counts, n_features=vector_size)
    vocab = transformer.get_feature_names()
    n_tokens = counts.sum()
    # the following two methods convert the weights from ppmi into a gensim model
    converted_vectors = convert_vectors(weights, vocab)
    model = converted_vectors_to_model(converted_vectors)
    return model, n_tokens


def convert_vectors(vectors, vocab):
    ''' given vectors (numpy array) and vocab,
    return a white-space delimited string of each vocab word,
    followed by weights in str format and a newline character
    '''
    vector_as_list = [list(map(str, list(v))) for v in vectors.T]
    for i, v in enumerate(vector_as_list):
        v.insert(0, vocab[i])
        v.append('\n')
    return [' '.join(v) for v in vector_as_list]


def converted_vectors_to_model(converted_vectors):
    ''' given vectors converted to a list of strings,
    save as temporary .txt file, and convert this to a gensim KeyedVector
    '''
    tmp_glove = get_tmpfile('fake_glove.txt')
    tmp_word2vec = get_tmpfile('fake_word2vec.txt')
    with open(tmp_glove, 'w+') as f:
        f.writelines(converted_vectors)
    _ = glove2word2vec(tmp_glove, tmp_word2vec)
    model = KeyedVectors.load_word2vec_format(tmp_word2vec)
    return model

if __name__ == '__main__':
    generate_models()
