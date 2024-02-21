'''
    In this module implemented parametrised conditions for text classification
    The main idea is  use set of conditions, and pass text words by words through those conditions
    Each condition on each step obtain one word and return boolean value
'''


import re

# Utility functions
def is_float(value):
    """Check if the input value can be converted to a float."""
    try:
        float(value)
        return True
    except ValueError:
        return False

def is_percent(value):
    """Check if the input value is a percent (ends with '%')."""
    if value.endswith('%'):
        try:
            float(value[:-1])
            return True
        except ValueError:
            return False
    return False

# Base condition class
class ConditionBase:
    """Base class for conditions with common functionalities."""
    mandatory_params = []

    def __init__(self, params=None):
        if params is None:
            params = {}
        self.params = params
        self.validate_params()
        self.error_handler = self.default_error_handler

    def validate_params(self):
        """Validate mandatory parameters."""
        for param in self.mandatory_params:
            if param not in self.params:
                self.default_error_handler(f'No required parameter [{param}]')

    def default_error_handler(self, msg):
        """Default error handler raising an exception with a message."""
        raise ValueError(msg)

    def check(self, string):
        """Check condition against the input string."""
        return False

    def clean(self):
        """Clean or reset the condition state."""
        raise NotImplementedError('Clean method should be implemented in child class.')

    def __str__(self):
        return f'{self.__class__.__name__}({self.params})'

# Derived condition classes
class ConditionFloatInLastNWords(ConditionBase):
    """Condition to check if a float is within the last n words."""
    mandatory_params = ['n_words']

    def __init__(self, params=None):
        super().__init__(params)
        self.max_distance = self.params['n_words']
        self.last_distance = None

    def check(self, string):
        if is_float(string):
            self.last_distance = 0
        else:
            if self.last_distance is not None:
                self.last_distance += 1

        return self.last_distance is not None and self.last_distance < self.max_distance

    def clean(self):
        self.last_distance = None

class ConditionKeywordsInLastNWords(ConditionBase):
    """Condition to check if any of the specified keywords are within the last n words."""
    mandatory_params = ['n_words', 'keywords']

    def __init__(self, params=None):
        super().__init__(params)
        self.max_distance = self.params['n_words']
        self.keywords = self.params['keywords']
        self.last_distance = None

    def check(self, string):
        if string in self.keywords:
            self.last_distance = 0
        else:
            if self.last_distance is not None:
                self.last_distance += 1

        return self.last_distance is not None and self.last_distance < self.max_distance

    def clean(self):
        self.last_distance = None

class ConditionFloatPercentInLastNWords(ConditionFloatInLastNWords):
    """Condition to check if a percent is within the last n words, inheriting from ConditionFloatInLastNWords."""
    def check(self, string):
        if is_percent(string):
            self.last_distance = 0
        else:
            if self.last_distance is not None:
                self.last_distance += 1
        return super().check(string)

class ConditionFloatOrPercentInLastNWords(ConditionFloatInLastNWords):
    """Condition to check if either a float or a percent is within the last n words."""
    def check(self, string):
        if is_percent(string) or is_float(string):
            self.last_distance = 0
        else:
            if self.last_distance is not None:
                self.last_distance += 1
        return super().check(string)

class NegativeCondition(ConditionBase):
    """Inverts the result of another condition."""
    def __init__(self, positive_condition):
        super().__init__(positive_condition.params)
        self.positive_condition = positive_condition

    def check(self, string):
        return not self.positive_condition.check(string)

    def clean(self):
        self.positive_condition.clean()

# Example of usage and testing
if __name__ == "__main__":
    test_strings = ["The price is 100.00$","100.00% of success", "Special rates is 100.00%"]
    splited_words = [string.split() for string in test_strings]
    test_conditions = [ConditionFloatInLastNWords({'n_words':3}),
                       ConditionFloatPercentInLastNWords({'n_words':3}),
                       ConditionKeywordsInLastNWords({'n_words':3,'keywords':['price','rates']}),
                       NegativeCondition(ConditionKeywordsInLastNWords({'n_words':3,'keywords':['price','rates']}))]
    for cond in test_conditions:
        print(cond)
        for words in splited_words:
            for word in words:
                print(cond.check(word),end=' ')
            print()

