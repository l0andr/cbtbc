import pytest
from cbtbc_model import cbtbc_model
from conditions import condition_float_in_last_n_words, condition_keywords_in_last_n_words
# Fixture for creating a model instance
@pytest.fixture
def model_instance():
    return cbtbc_model(conditions_list=[condition_float_in_last_n_words({'n_words':3}), condition_keywords_in_last_n_words({'n_words':3,'keywords':['test','keyword']})])

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
    new_instance = cbtbc_model()
    new_instance.load_conditions(str(file_path))
    # This test assumes `conditions` can be compared directly, which might not be the case
    # You might need to compare the effects of the conditions instead
    assert new_instance == model_instance, "Loaded conditions should match saved conditions"

def test_train_bruteforce(model_instance):
    # This test might need adjustments based on the actual logic within `train_minimize_number_of_conditions`
    min_number_of_differences, best_conditions_switchers = model_instance.train_minimize_number_of_conditions(
        ["10.0 test string","test string"], [True,False], method='bruteforce', verbose=1
    )
    assert min_number_of_differences == 0, "Number of differences should be 0"
    assert best_conditions_switchers == [True, False], "Best conditions switchers should be [True, False]"

def test_cbtcb_model_run():
    from cbtbc_model import cbtbc_model
    conditions_set = []
    conditions_param = []
    i = 3
    conditions_set.append('condition_floatpercent_in_last_n_words')
    conditions_param.append({'n_words': i})
    conditions_set.append('condition_keywords_in_last_n_words')
    conditions_param.append({'n_words': i, 'keywords': ['rates']})
    test_strings = ["<html><body>Special.<b>rates</b> is <i>100.00<b>%</b></i></body></html>",
                    "<html><body>Special.<b>rates</b> is good and acceptable for <i>100.00<b>%</b></i> of customers</body></html>",
                    "<html><body>Special.<b>price</b> is good for <i>100.00<b>%</b></i> of customers</body></html>"
                    ]
    test_label = [True, False, False]
    testmodel = cbtbc_model(conditions_set, conditions_param)
    model_results = []
    for string in test_strings:
        model_results.append(testmodel.run(string))
    assert model_results == test_label

def test_cbtcb_model_train_bruteforce():
    from cbtbc_model import cbtbc_model
    conditions_set = []
    conditions_param = []
    for i in range(2, 5):
        conditions_set.append('condition_floatpercent_in_last_n_words')
        conditions_param.append({'n_words': i})
        conditions_set.append('condition_keywords_in_last_n_words')
        conditions_param.append({'n_words': i, 'keywords': ['price']})
        conditions_set.append('condition_keywords_in_last_n_words')
        conditions_param.append({'n_words': i, 'keywords': ['rates']})

    testmodel = cbtbc_model(conditions_set, conditions_param)
    test_strings = ["<html><body>Special.<b>rates</b> is <i>100.00<b>%</b></i></body></html>",
                    "<html><body>Special.<b>rates</b> is good and acceptable for <i>100.00<b>%</b></i> of customers</body></html>",
                    "<html><body>Special.<b>price</b> is good for <i>100.00<b>%</b></i> of customers</body></html>"
                    ]
    test_label = [True, True, False]
    [min_number_of_differences, best_conditions_switchers] = testmodel.train_minimize_number_of_conditions(test_strings,
                                                                                                           test_label,
                                                                                                           method='bruteforce',
                                                                                                           verbose=0)
    assert min_number_of_differences == 0
    results_before_training = []
    results_after_training = []
    for string in test_strings:
        results_before_training.append(testmodel.run(string))
    for string in test_strings:
        results_after_training.append(testmodel.run(string, conditions_switches=best_conditions_switchers))
    assert results_before_training != test_label
    assert results_after_training == test_label
