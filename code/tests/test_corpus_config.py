import os.path as op
import pytest

from analyzer import Analyzer
from corpus_config import CORPUS_CONFIGURATIONS, dutchnewspapers_filter_article
from collect_sentences import DataCollector
from util import CorpusConfigurationException

here = op.dirname(op.abspath(__file__))

expected_es_body = {
    "query": {
        "bool": {
            "filter": [
                {"range": {"date": {"gte": "1980-01-01", "lte": "1980-12-31"}}},
                {"term": {"category": "artikel"}}
            ]
        }
    }
}

class mockAnalyzer(object):
    pass

def test_index_not_configured():
    CORPUS_CONFIGURATIONS.update({'test-corpus': {}})
    corpus_config = CORPUS_CONFIGURATIONS.get('test-corpus')
    with pytest.raises(CorpusConfigurationException) as exception:
        DataCollector(corpus_config, 1980, 1990, mockAnalyzer(), here)
        assert str(exception.value).contains('index')

def test_text_field_not_configured():
    CORPUS_CONFIGURATIONS.update({'test-corpus': {'index': 'test-index'}})
    corpus_config = CORPUS_CONFIGURATIONS.get('test-corpus')
    with pytest.raises(CorpusConfigurationException) as exception:
        DataCollector(corpus_config, 1980, 1990, mockAnalyzer(), here)
        assert str(exception.value).contains('text data')

def test_language_not_configured():
    CORPUS_CONFIGURATIONS.update({'test-corpus': {'index': 'test-index'}})
    corpus_config = CORPUS_CONFIGURATIONS.get('test-corpus')
    with pytest.raises(CorpusConfigurationException) as exception:
        Analyzer(corpus_config)
        assert str(exception.value).contains('language')

def test_update_query():
    CORPUS_CONFIGURATIONS.update({'test-corpus': {'index': 'test-index', 'language': 'english', 'text_field': 'content', 'update_query': dutchnewspapers_filter_article}})
    corpus_config = CORPUS_CONFIGURATIONS.get('test-corpus')
    data_collector = DataCollector(corpus_config, 1980, 1990, mockAnalyzer, here)
    es_body = data_collector.get_es_body('1980-01-01', '1980-12-31')
    assert(es_body == expected_es_body)