'''
Pytest test of conditions.py
'''

import pytest
from conditions import (
    is_float,
    is_percent,
    ConditionFloatInLastNWords,
    ConditionKeywordsInLastNWords,
    ConditionFloatPercentInLastNWords,
    ConditionFloatOrPercentInLastNWords,
    NegativeCondition
)

# Tests for utility functions
def test_is_float():
    assert is_float("123.45") is True
    assert is_float("notafloat") is False

def test_is_percent():
    assert is_percent("50%") is True
    assert is_percent("notapercent") is False

# Tests for ConditionFloatInLastNWords
def test_condition_float_in_last_n_words():
    condition = ConditionFloatInLastNWords({"n_words": 2})
    assert condition.check("100.5") is True
    condition.clean()
    assert condition.check("not a float") is False

# Tests for ConditionKeywordsInLastNWords
def test_condition_keywords_in_last_n_words():
    condition = ConditionKeywordsInLastNWords({"n_words": 2, "keywords": ["test", "keyword"]})
    assert condition.check("test") is True
    condition.clean()
    assert condition.check("not a keyword") is False

# Tests for ConditionFloatPercentInLastNWords
def test_condition_float_percent_in_last_n_words():
    condition = ConditionFloatPercentInLastNWords({"n_words": 2})
    assert condition.check("50%") is True
    condition.clean()
    assert condition.check("100.5") is True

# Tests for ConditionFloatOrPercentInLastNWords
def test_condition_float_or_percent_in_last_n_words():
    condition = ConditionFloatOrPercentInLastNWords({"n_words": 2})
    assert condition.check("50%") is True
    assert condition.check("100.5") is True
    condition.clean()
    assert condition.check("neither") is False

# Tests for NegativeCondition
def test_negative_condition():
    positive_condition = ConditionFloatInLastNWords({"n_words": 2})
    negative_condition = NegativeCondition(positive_condition)
    assert negative_condition.check("100.5") is False
    negative_condition.clean()
    assert negative_condition.check("not a float") is True
