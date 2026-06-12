import logging
import spacy
from typing import Iterable, Tuple

from util import CorpusConfigurationException

logger = logging.getLogger(__name__)

spacy_models = {
    'english': "en_core_web_sm",
    'german': "de_core_news_sm",
    'french': "fr_core_news_sm",
    'swedish': "sv_core_news_sm",
    'dutch': "nl_core_news_sm",
    'finnish': "fi_core_news_lg"
}

class Analyzer(object):

    def __init__(self, corpus_config: dict):
        self.lemmatize = corpus_config.get('lemmatize', False)
        self.language = corpus_config.get('language')
        if not self.language:
            raise CorpusConfigurationException(
                'The corpus configuration should specify the language of the corpus'
            )
        model = spacy_models.get(self.language)
        self.nlp = spacy.load(model)

    def preprocess(self, input_string):
        # apply analysis pipeline
        doc = self.nlp(input_string)
        self._merge_prefixes(doc)
        output = [self.select_token(token).lower() for token in doc if self.select_token(token)]
        return output


    def _merge_prefixes(self, doc):
        '''
        Merge some prefixes where we do not want hyphen splitting
        '''
        spans = list(self._spans_to_merge(doc))
        if spans:
            with doc.retokenize() as retokenizer:
                for start, end in spans:
                    try:
                        retokenizer.merge(doc[start:end])
                    except Exception as e:
                        logger.error('Could not merge %s (Sentence: %s)', doc[start:end], doc, exc_info=True)
                        logger.info(str(spans))
                        continue


    def _spans_to_merge(self, doc) -> Iterable[Tuple[int, int]]:
        exceptions = ['anti', 'e', 'extra', 'inter', 'neo', 'non', 'post', 'pre', 'pro', 'ultra']
        is_prefix = lambda token: \
            token.i < len(doc) - 3 and \
            token.lower_ in exceptions and \
            doc[token.i + 1].lower_ == '-'

        for token in doc:
            if is_prefix(token):
                next = doc[token.i + 2]
                while is_prefix(next):
                    next = doc[next.i + 2]
                yield token.i, next.i + 1


    def select_token(self, token):
        exclude_conditions = [
            token.is_punct,
            token.is_currency,
            token.is_stop,
            token.is_digit
        ]
        if any(exclude_conditions):
            pass
        elif self.lemmatize:
            return token.lemma_
        else:
            return token.text
