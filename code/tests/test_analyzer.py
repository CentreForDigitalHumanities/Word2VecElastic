from analyzer import Analyzer
from corpus_config import CORPUS_CONFIGURATIONS

test_corpus_config = CORPUS_CONFIGURATIONS.get('parliament-uk')

def test_data_analyzer():
    test_corpus_config['lemmatize'] = True
    analyzer = Analyzer(test_corpus_config).preprocess
    test_sentence = "What I'm saying is -- the U.K. have a neo-liberalist government!"
    output = analyzer(test_sentence)
    assert "neo-liberalist" in output
    assert "--" not in output
    assert "u.k." in output
    assert None not in output

def test_hyphen_merge():
    test_corpus_config['lemmatize'] = True
    analyzer = Analyzer(test_corpus_config).preprocess
    test_sentence = 'The UK government are on the non-exciting but dangerous road of e-democracy.'
    output = analyzer(test_sentence)
    assert "non-exciting" in output
    assert "e-democracy" in output
    assert len(output) == 6

def test_hyphen_exception():
    analyzer = Analyzer(test_corpus_config).preprocess
    test_sentence = 'Our post offices are always open.'
    output = analyzer(test_sentence)
    assert len(output) == 3
    test_sentence = 'Post-war London was grim.'
    output = analyzer(test_sentence)
    assert 'post-war' in output
    test_sentence = 'We only accept anti anti-war sentiments'
    output = analyzer(test_sentence)
    assert 'anti' in output
    assert 'anti-war' in output


def test_double_hyphen_exception():
    analyzer = Analyzer(test_corpus_config).preprocess
    test_sentence = 'These policies are ultra-neo-liberal.'
    output = analyzer(test_sentence)
    assert 'ultra-neo-liberal' in output

    test_sentence = "In fact, this agreement is a kind of 'pre-pre-agreement'."
    output = analyzer(test_sentence)
    assert 'pre-pre-agreement' in output


def test_end_of_string():
    analyzer = Analyzer(test_corpus_config).preprocess
    test_sentence = 'Most commerce is currently e'
    output = analyzer(test_sentence)
    assert 'e' in output
    test_sentence = 'I am anti war'
    output = analyzer(test_sentence)
    assert 'anti' in output
    test_sentence = 'I was non-plussed.'
    output = analyzer(test_sentence)
    assert 'non-plussed' in output
