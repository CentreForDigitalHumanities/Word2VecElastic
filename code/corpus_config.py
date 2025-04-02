def dutchnewspapers_filter_article(es_body: dict):
    """ Select only those items from the dutchnewspapers corpus which don't fall into the `article` category"""
    es_body["query"]["bool"]["filter"].append({"term": {"category": "artikel"}})


CORPUS_CONFIGURATIONS = {
    'dutch-newspapers': {
        'index': 'ianalyzer-dutchnewspapers-public',
        'language': 'dutch',
        'text_field': 'content',
        'update_query': dutchnewspapers_filter_article
    },
    'guardian-observer': {
        'index': 'ianalyzer-guardianobserver',
        'language': 'english',
        'min_count': 150,
        'max_vocab': 20000,
        'text_field': 'content'
    },
    'parliament-canada': {
        'index': 'parliament-canada',
        'language': 'english',
        'text_field': 'speech'
    },
    'parliament-finland': {
        'index': 'parliament-finland', # old data not included because it is largely in Swedish
        'language': 'finnish',
        'lemmatize': True,
        'text_field': 'speech'
    },
    'parliament-france': {
        'index': 'parliament-france',
        'language': 'french',
        'text_field': 'speech'
    },
    'parliament-germany': {
        'index': 'parliament-germany-new',
        'language': 'german',
        'text_field': 'speech'
    },
    'parliament-ireland': {
        'index': 'parliament-ireland',
        'language': 'english',
        'text_field': 'speech'
    },
    'parliament_netherlands': {
        'index': 'parliament-netherlands',
        'language': 'dutch',
        'text_field': 'speech'
    },
    'parliament-sweden': {
        'index': 'parliament-sweden-combined',
        'language': 'swedish',
        'text_field': 'speech'
    },
    'parliament-uk': {
        'index': 'parliament-uk',
        'language': 'english',
        'text_field': 'speech'
    },
    'troonredes': {
        'algorithm': 'ppmi',
        'index': 'ianalyzer-troonredes',
        'language': 'dutch',
        'text_field': 'content'
    },
}