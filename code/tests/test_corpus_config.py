import os.path as op
import pytest

from analyzer import Analyzer
from corpus_config import CORPUS_CONFIGURATIONS, dutchnewspapers_filter_article
from collect_sentences import DataCollector, es
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


def mock_index_exists(index: str) -> bool:
    return True


def test_invalid_configuration_parameter():
    CORPUS_CONFIGURATIONS.update({'test-corpus': {'typo': 'blabla', 'gibberish': 42}})
    with pytest.raises(CorpusConfigurationException) as exception:
        DataCollector('test-corpus', 1980, 1990, mockAnalyzer(), here)
        assert str(exception.value).contains('gibberish')


def test_text_field_not_configured():
    CORPUS_CONFIGURATIONS.update({'test-corpus': {}})
    with pytest.raises(CorpusConfigurationException) as exception:
        DataCollector('test-corpus', 1980, 1990, mockAnalyzer(), here)
        assert str(exception.value).contains('text data')

def test_language_not_configured():
    CORPUS_CONFIGURATIONS.update({'test-corpus': {}})
    corpus_config = CORPUS_CONFIGURATIONS.get('test-corpus')
    with pytest.raises(CorpusConfigurationException) as exception:
        Analyzer(corpus_config)
        assert str(exception.value).contains('language')


def test_update_query(monkeypatch):

    CORPUS_CONFIGURATIONS.update(
        {
            'test-corpus': {
                'language': 'english',
                'text_field': 'content',
                'update_query': dutchnewspapers_filter_article,
            }
        }
    )
    monkeypatch.setattr(es.indices, 'exists', mock_index_exists)
    data_collector = DataCollector('test-corpus', 1980, 1990, mockAnalyzer, here)
    es_body = data_collector.get_es_body('1980-01-01', '1980-12-31')
    assert(es_body == expected_es_body)
