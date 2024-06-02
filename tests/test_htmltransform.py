import pytest
from htmltransform import extract_text_from_html, word_tokenization_ext, words_rule_based_replacement

def test_extract_text_from_html():
    html = "<html><head><title>Test</title></head><body><p>Hello World!</p></body></html>"
    assert extract_text_from_html(html,tag_text_sep=" ") == "Test Hello World!"

    html_with_scripts = "<html><script>Some script</script><body>Text</body></html>"
    assert extract_text_from_html(html_with_scripts) == "Text"

def test_word_tokenization_ext():
    text = "This is a test."
    assert word_tokenization_ext(text) == ["This", "is", "a", "test", "."]

    text_with_hash = "Testing # hash removal."
    assert word_tokenization_ext(text_with_hash) == ["Testing", "hash", "removal", "."]

def test_words_rule_based_replacement():
    words = ["This", "is", "a", "test"]
    assert words_rule_based_replacement(words) == ["this", "is", "a", "test"]

    words_with_percent = ["100", "%", "complete"]
    assert words_rule_based_replacement(words_with_percent) == ["100%", "complete"]
