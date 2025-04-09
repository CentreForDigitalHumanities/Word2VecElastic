def dutchnewspapers_filter_article(es_body: dict):
    """ Select only those items from the dutchnewspapers corpus which don't fall into the `article` category"""
    es_body["query"]["bool"]["filter"].append({"term": {"category": "artikel"}})


CORPUS_CONFIGURATIONS = {
    'dutch-newspapers': {
        'language': 'dutch',
        'text_field': 'content',
        'update_query': dutchnewspapers_filter_article
    },
    'guardian-observer': {
        'language': 'english',
        'min_count': 150,
        'max_vocab': 20000,
        'text_field': 'content'
    },
    'parliament-canada': {
        'language': 'english',
        'text_field': 'speech'
    },
    'parliament-finland': {
        'language': 'finnish',
        'lemmatize': True,
        'text_field': 'speech'
    },
    'parliament-france': {
        'language': 'french',
        'text_field': 'speech'
    },
    'parliament-germany': {
        'language': 'german',
        'text_field': 'speech'
    },
    'parliament-ireland': {
        'language': 'english',
        'text_field': 'speech'
    },
    'parliament_netherlands': {
        'language': 'dutch',
        'text_field': 'speech'
    },
    'parliament-sweden': {
        'language': 'swedish',
        'text_field': 'speech'
    },
    'parliament-uk': {
        'language': 'english',
        'text_field': 'speech'
    },
    'troonredes': {
        'algorithm': 'ppmi',
        'language': 'dutch',
        'text_field': 'content'
    },
}