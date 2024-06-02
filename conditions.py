'''
    In this module implemented parametrised conditions for text classification
    The main idea is  use set of conditions, and pass text words by words through those conditions
    Each condition on each step obtain one word and return boolean value
'''

#Some utility functions
def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def ispercent(value):
    #check the last symbol is %
    if value[-1] != '%':
        return False
    #check the rest is float
    try:
        float(value[:-1])
        return True
    except ValueError:
        return False


class condition_base():
    mandatory_params = []
    def __init__(self,params = None):
        for param in self.mandatory_params:
            if param not in params:
                self.default_error_handler(f'No required parameter [{param}] ')
        self.params = params
        self.error_handler = self.default_error_handler
    def default_error_handler(self,msg):
        raise Exception(msg)
    def check(self, string):
        return False
    def clean(self):
        raise NotImplementedError('clean method should be implemented in child class')
    def __str__(self):
        return f'{self.__class__.__name__}({self.params})'

class condition_float_in_last_n_words(condition_base):
    mandatory_params = ['n_words']
    def __init__(self,params = None):
        super().__init__(params)
        self.max_distance = self.params['n_words']
        self.last_distance = None
    def check(self, string):
        if isfloat(string):
            self.last_distance = 0
        else:
            if self.last_distance is not None:
                self.last_distance += 1

        if self.last_distance is not None and self.last_distance < self.max_distance:
            return True
        else:
            return False
    def __eq__(self, other):
        return self.params == other.params and self.__class__ == other.__class__
    def clean(self):
        self.last_distance = None
class condition_keywords_in_last_n_words(condition_base):
    mandatory_params = ['n_words','keywords']
    def __init__(self,params = None):
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

        if self.last_distance is not None and self.last_distance < self.max_distance:
            return True
        else:
            return False
    def clean(self):
        self.last_distance = None
class condition_floatpercent_in_last_n_words(condition_float_in_last_n_words):
    def check(self, string):
        if ispercent(string):
            self.last_distance = 0
        else:
            if self.last_distance is not None:
                self.last_distance += 1
        if self.last_distance is not None and self.last_distance < self.max_distance:
            return True
        else:
            return False
class condition_floatorpercent_in_last_n_words(condition_float_in_last_n_words):
    def check(self, string):
        if ispercent(string) or isfloat(string):
            self.last_distance = 0
        else:
            if self.last_distance is not None:
                self.last_distance += 1
        if self.last_distance is not None and self.last_distance < self.max_distance:
            return True
        else:
            return False

class negative_condition(condition_base):
    def __init__(self,positive_conditions:condition_base):
        self.positive_conditions = positive_conditions
        self.params = positive_conditions.params
    def check(self, string):
        return not self.positive_conditions.check(string)
    def clean(self):
        self.positive_conditions.clean()
#Conditions factory
def condition_factory(condition_name,params = None):
    if condition_name == 'condition_float_in_last_n_words':
        return condition_float_in_last_n_words(params)
    elif condition_name == 'condition_keywords_in_last_n_words':
        return condition_keywords_in_last_n_words(params)
    elif condition_name == 'condition_floatpercent_in_last_n_words':
        return condition_floatpercent_in_last_n_words(params)
    elif condition_name == 'condition_floatorpercent_in_last_n_words':
        return condition_floatorpercent_in_last_n_words(params)
    else:
        raise Exception(f'Unknown condition name {condition_name}')
