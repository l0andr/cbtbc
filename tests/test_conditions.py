'''
Pytest test of conditions.py
'''

import pytest
from conditions import isfloat,ispercent, condition_float_in_last_n_words, condition_keywords_in_last_n_words, condition_floatpercent_in_last_n_words, condition_floatorpercent_in_last_n_words, negative_condition

# Tests for utility functions
def test_is_float():
    assert isfloat("123.45") is True
    assert isfloat("notafloat") is False

def test_is_percent():
    assert ispercent("50%") is True
    assert ispercent("notapercent") is False

# Tests for ConditionFloatInLastNWords
def test_condition_float_in_last_n_words():
    condition = condition_float_in_last_n_words({"n_words": 2})
    assert condition.check("100.5") is True
    condition.clean()
    assert condition.check("not a float") is False

# Tests for ConditionKeywordsInLastNWords
def test_condition_keywords_in_last_n_words():
    condition = condition_keywords_in_last_n_words({"n_words": 2, "keywords": ["test", "keyword"]})
    assert condition.check("test") is True
    condition.clean()
    assert condition.check("not a keyword") is False

# Tests for ConditionFloatPercentInLastNWords
def test_condition_float_percent_in_last_n_words():
    condition = condition_floatorpercent_in_last_n_words({"n_words": 2})
    assert condition.check("50%") is True
    condition.clean()
    assert condition.check("100.5") is True

# Tests for ConditionFloatOrPercentInLastNWords
def test_condition_float_or_percent_in_last_n_words():
    condition = condition_floatorpercent_in_last_n_words({"n_words": 2})
    assert condition.check("50%") is True
    assert condition.check("100.5") is True
    condition.clean()
    assert condition.check("neither") is False

# Tests for NegativeCondition
def test_negative_condition():
    positive_condition = condition_float_in_last_n_words({"n_words": 2})
    negative_condition_obj = negative_condition(positive_condition)
    assert negative_condition_obj.check("100.5") is False
    negative_condition_obj.clean()
    assert negative_condition_obj.check("not a float") is True
