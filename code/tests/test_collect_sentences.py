import tempfile
import pytest

from collect_sentences import es, DataCollector, ESCollector, time
from .test_corpus_config import mock_index_exists

n_years = 5
end_year = 1986
start_year = end_year - n_years


@pytest.fixture
def collector(monkeypatch):
    monkeypatch.setattr(es.indices, 'exists', mock_index_exists)
    with tempfile.TemporaryDirectory() as temp_dir:
        return DataCollector(
            'guardian-observer',
            start_year=start_year,
            end_year=end_year,
            source_directory=temp_dir,
        )

@pytest.fixture
def search_result():
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

def mock_search(*args, **kwargs):
    return search_result

def mock_clear_scroll(scroll_id):
    return {'acknowledged': True}

def mock_data_collector(monkeypatch, collector, search_result):
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


def test_get_content(monkeypatch, search_result):
    monkeypatch.setattr(es.indices, 'exists', mock_index_exists)
    collector = ESCollector('guardian-observer', 1980, 1990)
    collector.text_field = 'test_field'
    docs = collector._get_content(search_result)
    assert len(docs) == 4
    assert docs[0] == "This is a wonderful sentence. Here, have another."


def test_get_content_missing_values(monkeypatch, search_result):
    monkeypatch.setattr(es.indices, 'exists', mock_index_exists)
    collector = ESCollector('guardian-observer', 1980, 1990)
    collector.text_field = 'test_field'
    search_result['hits']['hits'][1]['_source'].pop('test_field')
    docs = collector._get_content(search_result)
    assert len(docs) == 4
    assert docs[1] == ""



class ExceptionFaker():
    def __init__(self, times, output):
        self.times = times
        self.count = 0
        self.output = output

    def run(self):
        if self.count < self.times:
            self.count += 1
            raise Exception('Test exception')
        else:
            self.count += 1
            return self.output


def test_retry(monkeypatch, search_result):
    monkeypatch.setattr(es.indices, 'exists', mock_index_exists)
    monkeypatch.setattr(es, 'clear_scroll', mock_clear_scroll)
    monkeypatch.setattr(time, 'sleep', lambda t: None) # skip sleep time
    collector = ESCollector('guardian-observer', start_year, end_year)
    collector.text_field = 'test_field'
    faker = ExceptionFaker(3, search_result)
    monkeypatch.setattr(collector, '_search', faker.run)
    docs = collector.get_documents()
    assert len(docs) == 4
