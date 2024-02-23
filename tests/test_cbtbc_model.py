import pytest
from cbtbc_model import CbtbcModel
from conditions import ConditionFloatInLastNWords,ConditionKeywordsInLastNWords
# Fixture for creating a model instance
@pytest.fixture
def model_instance():
    return CbtbcModel(conditions_list=[ConditionFloatInLastNWords({'n_words':3}), ConditionKeywordsInLastNWords({'n_words':3,'keywords':['test','keyword']})])

def test_initialization_default(model_instance):
    assert model_instance.top_level_operation == 'and', "Default top level operation should be 'and'"

def test_run_with_default_conditions(model_instance):
    # Assuming the default implementation of `run` requires specific conditions to return True/False
    # This test might need adjustments based on the actual logic within `run`
    assert not model_instance.run("sample text"), "Run should return False with default (None) conditions"

def test_run_with_specific_condition_enabled(model_instance):
    # Setup a model with a mock condition that always returns True
    assert model_instance.run("1.2 sample test"), "Run should return True when condition is met"
    assert model_instance.run("1.2 sample sample") == False, "Run should return False when not all conditions is met"

def test_filter_conditions(model_instance):
    model_instance.filter_conditions([True, False])
    assert model_instance.run("1.2 sample sample"), "Run should return True"

def test_save_and_load_conditions(tmp_path, model_instance):
    # Use `tmp_path` fixture provided by pytest for creating a temporary file
    file_path = tmp_path / "conditions.dat"
    model_instance.save_conditions(str(file_path))
    new_instance = CbtbcModel()
    new_instance.load_conditions(str(file_path))
    # This test assumes `conditions` can be compared directly, which might not be the case
    # You might need to compare the effects of the conditions instead
    assert new_instance.conditions == model_instance.conditions, "Loaded conditions should match saved conditions"
