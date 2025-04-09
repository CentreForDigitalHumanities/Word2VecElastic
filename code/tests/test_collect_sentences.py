from shutil import rmtree
import tempfile

import pytest

from collect_sentences import es, DataCollector
from corpus_config import CORPUS_CONFIGURATIONS
from analyzer import Analyzer
from .test_corpus_config import mock_index_exists

n_years = 5
end_year = 1986
start_year = end_year - n_years

@pytest.fixture
def analyzer():
    corpus_config = CORPUS_CONFIGURATIONS.get('guardian-observer')
    return Analyzer(corpus_config).preprocess


@pytest.fixture
def collector(analyzer, monkeypatch):
    monkeypatch.setattr(es.indices, 'exists', mock_index_exists)
    with tempfile.TemporaryDirectory() as temp_dir:
        return DataCollector(
            'guardian-observer',
            start_year=start_year,
            end_year=end_year,
            analyzer=analyzer,
            source_directory=temp_dir,
        )


def mock_data_collector(monkeypatch, collector):
    def mock_search(index, body, size, scroll, track_total_hits):
        return {
            "_scroll_id": 42,
            "hits": {"total": {"value": 4},
            "hits": [
                {'_source': {"test_field": "This is a wonderful sentence. Here, have another."}},
                {'_source': {"test_field": "Nothing but GREAT sentences!"}},
                {'_source': {"test_field": "Creativity never ends!"}},
                {'_source': {"test_field": "I will not buy this record. It is scratched."}}
            ]}
        }

    def mock_clear_scroll(scroll_id):
        return {'acknowledged': True}

    monkeypatch.setattr(es, 'search', mock_search)
    monkeypatch.setattr(es, 'clear_scroll', mock_clear_scroll)

    # check_path('test')

    sentences = collector
    assert len(list(sentences)) == 6 * n_years

def some_sentences(year):
    if year == 1985:
        return None
    return ['some scrumptious sentence', 'and another fantastic great sentence']

def test_get_sentences(monkeypatch, collector):
    data_collector = collector
    monkeypatch.setattr(data_collector, "get_sentences_for_year", some_sentences)
    sentences = data_collector.get_sentences()
    assert len(list(sentences)) == 2 * (n_years - 1)
