'''
Conditions based text binnary classification model
'''

import conditions
import htmltransform
from nltk.tokenize import word_tokenize
import cbtbc_opt
import pickle
from typing import List, Dict, Union, Optional  # Importing specific types from typing module for type hinting
from tqdm import tqdm  # Importing tqdm module for progress bar

class cbtbc_model():
    def __init__(self, conditions_list: Optional[List[Union[str, object]]] = None, condition_params: Optional[List[Dict]] = None):
        """
        Initialize the cbtbc_model with a list of conditions and their parameters.

        :param conditions_list: List of condition strings or condition objects
        :param condition_params: List of dictionaries containing parameters for each condition
        """
        self.top_level_operation = 'and'  # Setting default top-level operation to 'and'
        if conditions_list is None:
            self.conditions = conditions_list  # Assigning conditions list if provided
        else:
            self.conditions = []  # Initializing conditions as an empty list
            i = 0
            for cond in conditions_list:
                if isinstance(cond, conditions.condition_base):
                    self.conditions.append(cond)  # Adding condition if it's an instance of condition_base
                elif isinstance(cond, str):
                    if cond == 'or':
                        self.top_level_operation = 'or'  # Setting top-level operation to 'or'
                    elif cond == 'and':
                        self.top_level_operation = 'and'  # Setting top-level operation to 'and'
                    else:
                        self.conditions.append(conditions.condition_factory(cond, condition_params[i]))
                        i += 1
                else:
                    raise TypeError(f'conditions must be list of strings or list of conditions.condition_base, got {type(cond)}')

    def run(self, intext, conditions_switches: Optional[List[bool]] = None,ishtml:bool = True):
        """
        Run the model on the provided HTML and return True if the conditions are met.

        :param intext: plain text\HTML string to be processed
        :param conditions_switches: Optional list of booleans to enable/disable specific conditions
        :return: Boolean indicating if the conditions are met
        """
        if self.conditions is None:
            return False
        for cond in self.conditions:
            cond.clean()
        if ishtml:
            text = htmltransform.extract_text_from_html(intext, tag_text_sep="#")
            words = htmltransform.word_tokenization_ext(text)
            words = htmltransform.words_rule_based_replacement(words)
        else:
            words = word_tokenize(intext)

        if conditions_switches is not None:
            list_of_conditions = [cond for cond, switch in zip(self.conditions, conditions_switches) if switch]
        else:
            list_of_conditions = self.conditions
        for word in words:
            conds_results = [cond.check(word) for cond in list_of_conditions]
            if self.top_level_operation == 'and':
                if all(conds_results):
                    return True
            elif self.top_level_operation == 'or':
                if any(conds_results):
                    return True
        return False

    def train_minimize_number_of_conditions(self, list_of_htmls: List[str], list_of_labels: List[bool], method: str = 'bruteforce', verbose: int = 0, n_iter=100, trueprob=0.5):
        """
        Train the model to minimize the number of conditions using the specified method.

        :param list_of_htmls: List of HTML strings for training
        :param list_of_labels: Corresponding list of labels (True/False) for each HTML string
        :param method: Training method to use ('bruteforce', 'random_bnb', 'bnb', 'random')
        :param verbose: Verbosity level for training output
        :param n_iter: Number of iterations for random search methods
        :param trueprob: Probability for random search methods
        :return: Tuple of minimum number of differences and best condition switchers
        """
        if len(list_of_htmls) != len(list_of_labels):
            raise Exception('Length of list_of_htmls and list_of_labels must be equal')

        minimum_number_of_conditions = len(self.conditions)
        best_conditions_switchers = [True for cond in self.conditions]
        if method == 'bruteforce':
            # Bruteforce method
            # Create all possible combinations of conditions
            bruteforce_results = []
            for i in tqdm(range(0, 2**len(self.conditions)), disable=(verbose != 1), desc=f'cbtbc model. Training. Method:{method}'):
                # Create bool list with length len(self.conditions_list) with 2-base representation of i
                cond_switchers = [bool(int(digit)) for digit in bin(i)[2:].zfill(len(self.conditions))]
                current_conditions_results = [self.run(html, cond_switchers) for html in list_of_htmls]
                bruteforce_results.append(sum([int(current_conditions_results[j] != list_of_labels[j]) for j in range(len(list_of_labels))]))

            min_number_of_differences = min(bruteforce_results)
            # List of indexes of conditions with minimum number of differences
            min_number_of_differences_indexes = [i for i in range(len(bruteforce_results)) if bruteforce_results[i] == min_number_of_differences]
            for i in min_number_of_differences_indexes:
                # Compute sum of 1 in binary representation of i
                number_of_conditions = sum([int(digit) for digit in bin(i)[2:].zfill(len(self.conditions))])

                if number_of_conditions < minimum_number_of_conditions:
                    minimum_number_of_conditions = number_of_conditions
                    best_conditions_switchers = [bool(int(digit)) for digit in bin(i)[2:].zfill(len(self.conditions))]
        elif method == 'random_bnb':
            def bnb_random_objective_function(x):
                current_conditions_results = [self.run(html, x) for html in list_of_htmls]
                return sum([int(current_conditions_results[j] != list_of_labels[j]) for j in range(len(list_of_labels))])
            opt_res = cbtbc_opt.binary_vector_bnb_random_search(len(self.conditions), bnb_random_objective_function, n_iter=n_iter, bnb_method=True, random_search_method=True, trueprob=trueprob, verbose=verbose)
            best_conditions_switchers = opt_res[0]
            min_number_of_differences = opt_res[1]
        elif method == 'bnb':
            def bnb_random_objective_function(x):
                current_conditions_results = [self.run(html, x) for html in list_of_htmls]
                return sum([int(current_conditions_results[j] != list_of_labels[j]) for j in range(len(list_of_labels))])
            opt_res = cbtbc_opt.binary_vector_bnb_random_search(len(self.conditions), bnb_random_objective_function, n_iter=1, bnb_method=True, random_search_method=False, verbose=verbose)
            best_conditions_switchers = opt_res[0]
            min_number_of_differences = opt_res[1]
        elif method == 'random':
            def bnb_random_objective_function(x):
                current_conditions_results = [self.run(html, x) for html in list_of_htmls]
                return sum([int(current_conditions_results[j] != list_of_labels[j]) for j in range(len(list_of_labels))])
            opt_res = cbtbc_opt.binary_vector_bnb_random_search(len(self.conditions), bnb_random_objective_function, n_iter=n_iter, bnb_method=False, random_search_method=True, verbose=verbose)
            best_conditions_switchers = opt_res[0]
            min_number_of_differences = opt_res[1]
        else:
            raise Exception(f'Unknown method {method} for training')
        return min_number_of_differences, best_conditions_switchers

    def save_conditions(self, filename):
        """
        Save the current set of conditions to a file.

        :param filename: Name of the file to save the conditions
        """
        with open(filename, 'wb') as f:
            pickle.dump(self.conditions, f)

    def load_conditions(self, filename):
        """
        Load a set of conditions from a file.

        :param filename: Name of the file to load the conditions from
        """
        with open(filename, 'rb') as f:
            self.conditions = pickle.load(f)

    def filter_conditions(self, condition_switchers):
        """
        Filter the current set of conditions based on the provided condition switchers.

        :param condition_switchers: List of booleans indicating which conditions to keep
        """
        new_set_of_conditions = []
        i = 0
        for cs in condition_switchers:
            if cs:
                new_set_of_conditions.append(self.conditions[i])
            i += 1
        self.conditions = new_set_of_conditions

    def __str__(self):
        """
        Return a string representation of the model.
        """
        return f'{self.__class__.__name__}({self.conditions})'

    def __repr__(self):
        """
        Return a detailed string representation of the model.
        """
        return f'{self.__class__.__name__}({self.conditions})'

    def __eq__(self, other):
        """
        Check if two models are equal based on their conditions.

        :param other: The other model to compare with
        :return: Boolean indicating if the models are equal
        """
        if isinstance(other, cbtbc_model):
            all_conditions = [cond1 == cond2 for cond1, cond2 in zip(self.conditions, other.conditions)]
            return all_conditions
        else:
            return False

    def __ne__(self, other):
        """
        Check if two models are not equal.
        """
        return not self.__eq__(other)

