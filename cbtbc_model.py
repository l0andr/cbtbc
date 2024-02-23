'''
Conditions based text binnary classification model
'''

import conditions
import pickle
from typing import List, Dict, Union, Optional,Tuple
from nltk.tokenize import word_tokenize
from tqdm import tqdm
class CbtbcModel():
    def __init__(self, conditions_list:Optional[List[Union[str,object]]] = None,condition_params:Optional[List[Dict]]=None):
        self.top_level_operation = 'and'
        if conditions_list is None:
            self.conditions= conditions_list
        else:
            self.conditions = []
            i = 0
            for cond in conditions_list:
                if isinstance(cond, conditions.ConditionBase):
                    self.conditions.append(cond)
                elif isinstance(cond, str):
                    if cond == 'or':
                        self.top_level_operation = 'or'
                    elif cond == 'and':
                        self.top_level_operation = 'and'
                    else:
                        self.conditions.append(conditions.condition_factory(cond,condition_params[i]))
                        i+=1
                else:
                    raise TypeError(f'conditions must be list of strings or list of conditions.condition_base, got {type(cond)}')

    def run(self, text,conditions_switches:Optional[List[bool]] = None):
        if self.conditions is None:
            return False
        for cond in self.conditions:
            cond.clean()
        words = word_tokenize(text)
        if conditions_switches is not None:
            list_of_conditions = [cond for cond,switch in zip(self.conditions,conditions_switches) if switch]
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

    def train_minimize_number_of_conditions(self, list_of_texts: List[str], list_of_labels: List[bool],
                                            method: str = 'bruteforce', verbose: int = 0, n_iter: int = 100) -> Tuple[int, List[bool]]:
        """
        Train the model to minimize the number of conditions used for classification.

        :param list_of_texts: List of HTML content to classify.
        :param list_of_labels: Corresponding list of labels (True/False) for the HTML content.
        :param method: The optimization method to use ('bruteforce', 'random_bnb', 'bnb', or 'random').
        :param verbose: Verbosity level of the training process.
        :param n_iter: Number of iterations for methods that require iterations.
        :return: Tuple containing the minimum number of misclassifications and the list of switches for the best set of conditions.
        """
        if len(list_of_texts) != len(list_of_labels):
            raise ValueError('Length of list_of_htmls and list_of_labels must be equal')

        minimum_number_of_conditions = len(self.conditions)
        best_conditions_switchers = [True] * len(self.conditions)

        if method == 'bruteforce':
            bruteforce_results = self._bruteforce_optimization(list_of_texts, list_of_labels, verbose)
            min_number_of_differences, best_conditions_switchers = self._evaluate_bruteforce_results(bruteforce_results)
        elif method == 'random_bnb':
            raise NotImplementedError('random_bnb method is not implemented yet')
        elif method == 'bnb':
            raise NotImplementedError('bnb method is not implemented yet')
        elif method == 'random':
            raise NotImplementedError('random method is not implemented yet')
        else:
            raise Exception(f'Unknown method {method} for training')
        return min_number_of_differences, best_conditions_switchers


    def _bruteforce_optimization(self, list_of_texts: List[str], list_of_labels: List[bool], verbose: int) -> List[int]:
        """
        Perform brute force optimization to find the best set of conditions.

        :param list_of_htmls: List of HTML content to classify.
        :param list_of_labels: Corresponding list of labels for the HTML content.
        :param verbose: Verbosity level of the training process.
        :return: List of misclassification counts for each combination of conditions.
        """
        bruteforce_results = []
        for i in tqdm(range(2 ** len(self.conditions)), disable=(verbose != 1),
                      desc='cbtbc model. Training. Method: bruteforce'):
            cond_switchers = [bool(int(digit)) for digit in bin(i)[2:].zfill(len(self.conditions))]
            current_conditions_results = [self.run(html, cond_switchers) for html in list_of_texts]
            bruteforce_results.append(
                sum(current_conditions_results[j] != list_of_labels[j] for j in range(len(list_of_labels))))
        return bruteforce_results

    def _evaluate_bruteforce_results(self, bruteforce_results: List[int]) -> Tuple[int, List[bool]]:
        """
        Evaluate brute force results to find the minimum number of misclassifications and corresponding condition switches.

        :param bruteforce_results: List of misclassification counts for each combination of conditions.
        :return: Tuple of minimum number of misclassifications and list of best condition switches.
        """
        min_number_of_differences = min(bruteforce_results)
        min_indexes = [i for i, count in enumerate(bruteforce_results) if count == min_number_of_differences]

        minimum_number_of_conditions = len(self.conditions)
        best_conditions_switchers = []

        for i in min_indexes:
            number_of_conditions = bin(i).count('1')
            if number_of_conditions < minimum_number_of_conditions:
                minimum_number_of_conditions = number_of_conditions
                best_conditions_switchers = [bool(int(digit)) for digit in bin(i)[2:].zfill(len(self.conditions))]

        return min_number_of_differences, best_conditions_switchers

    def save_conditions(self, filename: str):
        with open(filename, 'wb') as f:
            pickle.dump(self.conditions, f)

    def load_conditions(self, filename : str):
        with open(filename, 'rb') as f:
            self.conditions = pickle.load(f)

    def filter_conditions(self,condition_switchers:List[bool]):
        new_set_of_conditions = []
        i = 0
        for cs in condition_switchers:
            if cs:
                new_set_of_conditions.append(self.conditions[i])
            i+=1
        self.conditions = new_set_of_conditions
    def __str__(self):
        return f'{self.__class__.__name__}({self.conditions})'
    def __repr__(self):
        return f'{self.__class__.__name__}({self.conditions})'
    def __eq__(self, other):
        if isinstance(other, CbtbcModel):
            return self.conditions == other.conditions
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)
