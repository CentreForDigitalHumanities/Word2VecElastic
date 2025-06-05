[![DOI](https://zenodo.org/badge/171899269.svg)](https://zenodo.org/badge/latestdoi/171899269)

# Word2VecElastic
This repository includes utility functions to build diachronic Word2Vec models in gensim, using an Elasticsearch index to collect the data, and SpaCy and NLTK to preprocess it.

It can also be used to train word models for small datasets using the positive pointwise mutual information (PPMI) metric to retain matrices of word similarity, following [this paper](https://aclanthology.org/C18-2003/).

The data is read in year batches from Elasticsearch and preprocessed. Every year's preprocessed data is saved to hard disk (as a pickled list of lists of words), so that for multiple passes (e.g., one to build the vocabulary, one to train the model), the data is available more readily.

For the whole time period, a full model will be generated, which will be used as pre-training data for the individual models. Alternatively, independent models can be trained by setting the `-in` flag (see #Usage)

# Prerequisites

## Elasticsearch
The data is fetched from Elasticsearch. By default, this will attempt to fetch from a local instance (i.e., `localhost:9200`) For local development, install [Elasticsearch](https://www.elastic.co/guide/en/elasticsearch/reference/current/install-elasticsearch.html).

In order to fetch data from a remote Elasticsearch cluster and/or on a different port, set environment variables through an `.env` file. The `.env-dist` file can be copied as a starting point.

For instance, to fetch from `http://url-of-your-cluster:9900`, you would set:
```bash
ES_HOST=http://url-of-your-cluster
ES_PORT=9900
```
If not set, `ES_HOST` will fall back to `localhost`, and `ES_PORT` to `9200`, respectively.

To connect to a remote cluster through SSL(recommended), you will also need to set the following variables: `ES_API_ID`, `ES_API_KEY`, `CERTS_LOCATION`.

Finally, if you would like to read from an index with a different name than the corpus, you can do this by setting `INDEX`. Once your `.env` file is set correctly, you can load the variables into your environment like so:
```bash
source .env
```

## Python
The code was tested in Python 3.11. Create a virtualenv (`python -m venv your_env_name`), activate it (`source your_env_name/bin/activate`) and then run
```
pip install -r requirements.txt
```

## SpaCy language models
With activated environment, download the SpaCy language models required for preprocessing as follows:
```
python -m spacy download en_core_web_sm
```
See (the SpaCy documentation)[https://spacy.io/usage/models].

# Corpus configurations
To train word models for a corpus, update (the `CORPUS_CONFIGURATIONS` dictionary)[code/corpus_config.py]. The required settings are:
- index: the name of the Elasticsearch index
- language: the language of the corpus
- text_field: in which field of the index text data for training can be found

Optional settings are:
- algorithm: set 'ppmi' or leave unset (will default to 'word2vec')
- date_field: the field to filter for specific years. Raises a warning if not set to inform that `date` will be used as default.
- independent: if `False`, the `generate_models` script will first train a large corpus for all data, and then proceed to retrain for time slices of the data. Defaults to `True` (i.e., each model is trained independently of data from other time slices). Note that limiting the size of the vocabulary with `max_vocab_size` and `min_count` may not be as effective when training with `independent=False`.
- max_vocab_size: can be used to prune the vocabulary during training, so that the memory size does not explode. Defaults to `None`.
- min_count: the number of times a word must appear in the data in order to be included in the model. Defaults to `None`.
- max_final_vocab: can be used to choose the `min_count` automatically to limit the final vocabulary to this size. Defaults to `None`.
- vector_size: the number of dimensions of the resulting word vectors. Defaults to 100.
- window_size: the size of the window around a target word for the word2vec algorithm. Defaults to 5.

# Usage
To train models, with activated environment, use the command
```
python generate_models.py -i your-index-name -s 1960 -e 2000 -md /path/to/output/models
```
Meaning of the flags:
- c: name of the corpus
- s: start year of training
- e: end year of training
- md: set the output directory where models will be written
Optional flags:
- n: number of years per model (default: 10)
- sh: shift between models (default: 5)
- sd: path to output preprocessed training data (default: 'source_data')

You can also run
`python generate_models.py -h` to see this documentation.

# Output
The training script generates three kinds of output:
- preprocessing output, the result of tokenizing, stop word removal and (optional) lemmatization of the source data from Elasticsearch, saved as Python binary `.pkl` files, named after index and year, in `source_directory` (set through `-sd` flag).
- word2vec output, the result of traning on the preprocessed data, saved as KeyedVectors, named after the index and time window, with the extension `.wv` in the `model_directory` (set through `-md` flag).
- statistics about the number of tokens (all words in the model not discarded during stopword removal) and number of terms (all distinct tokens), named after the index and time window, and saved as a comma-separated table (`.csv`) in the `model_directory`.

## Preprocessing output
To inspect the preprocessing output, install the dependecies of this repository (see (Prerequesites)[#Prerequesites]), then open a Python terminal.
To get a list of sentences (each a list of words), use the following workflow:
```python
from util import inspect_source_data
sentences = inspect_source_data('/{filepath}/{index_name}-{year}.pkl')
```

To write the source data to a text file, use the following workflow:
```python
from util import source_data_to_file
source_data_to_file('/{filepath}/{index_name}-{year}.pkl')
```