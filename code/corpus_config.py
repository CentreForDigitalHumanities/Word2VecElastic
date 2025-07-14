def dutchnewspapers_filter_article(es_body: dict):
    """Select only those items from the dutchnewspapers corpus which don't fall into the `article` category"""
    es_body["query"]["bool"]["filter"].append({"term": {"category": "artikel"}})


CORPUS_CONFIGURATIONS = {
    'dutch-newspapers': {
        'language': 'dutch',
        'text_field': 'content',
        'update_query': dutchnewspapers_filter_article,
        'max_final_vocab': 30000,
    },
    'guardian-observer': {
        'language': 'english',
        'min_count': 150,
        'max_vocab': 20000,
        'text_field': 'content',
    },
    'times': {
        'language': 'english',
        'max_final_vocab': 30000,
        'text_field': 'content',
    },
    'parliament-canada': {
        'language': 'english',
        'text_field': 'speech',
        'min_count': 80,
    },
    'parliament-finland': {
        'language': 'finnish',
        'lemmatize': True,
        'text_field': 'speech',
        'min_count': 80,
    },
    'parliament-france': {
        'language': 'french',
        'text_field': 'speech',
        'min_count': 80,
    },
    'parliament-germany': {
        'language': 'german',
        'text_field': 'speech',
        'min_count': 80,
    },
    'parliament-ireland': {
        'language': 'english',
        'text_field': 'speech',
        'min_count': 80,
    },
    'parliament_netherlands': {
        'language': 'dutch',
        'text_field': 'speech',
        'min_count': 80,
    },
    'parliament-sweden': {
        'language': 'swedish',
        'text_field': 'speech',
        'min_count': 80,
    },
    'parliament-uk': {'language': 'english', 'text_field': 'speech', 'min_count': 80},
    'troonredes': {
        'algorithm': 'ppmi',
        'language': 'dutch',
        'text_field': 'content',
        'min_count': 80,
    },
}
