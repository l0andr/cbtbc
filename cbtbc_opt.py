import tqdm
import random

def branch_and_bound(binary_vector, index, best_solution, best_value, objective_function):
    """
    Perform the branch-and-bound algorithm to find the optimal binary vector.

    :param binary_vector: Current binary vector being evaluated
    :param index: Current index in the binary vector
    :param best_solution: Best solution found so far (wrapped in a list for mutability)
    :param best_value: Best value found so far (wrapped in a list for mutability)
    :param objective_function: Function to evaluate the value of a binary vector
    """
    n = len(binary_vector)
    # Base case: if we've considered all elements
    if index == n:
        current_value = objective_function(binary_vector)
        if current_value <= best_value[0]:  # Allow equal value to support multiple "True" values
            if current_value < best_value[0] or sum(binary_vector) < sum(best_solution[0]):
                best_solution[0] = binary_vector.copy()
                best_value[0] = current_value
        return

    # Pruning condition based on a more nuanced strategy
    # Check if the partial solution could potentially lead to an improvement
    if index > 0:
        partial_value = objective_function(binary_vector[:index] + [True] * (n - index))
        if partial_value > best_value[0]:
            return  # Prune if the partial solution already exceeds the best value

    # Branch with the current element set to False
    branch_and_bound(binary_vector, index + 1, best_solution, best_value, objective_function)

    # Branch with the current element set to True, without immediate pruning
    binary_vector[index] = True
    branch_and_bound(binary_vector, index + 1, best_solution, best_value, objective_function)
    binary_vector[index] = False  # Reset for the next branch


def binary_vector_bnb_random_search(n, objective_function, n_iter=100, bnb_method=True, random_search_method=True, Trueprob=0.5, verbose=0):
    """
    Find the binary vector of size n that minimizes the given objective function.

    :param n: The size of the binary vector
    :param objective_function: Function that takes a binary vector as input and returns a numerical value
    :param n_iter: Number of iterations for the random search method
    :param bnb_method: If True, use the branch-and-bound method
    :param random_search_method: If True, use the random search method
    :param verbose: Verbosity level (0: silent, 1: progress bar, 2: progress report)
    :param Trueprob: Probability for choosing True in random search
    :return: Tuple containing the optimal binary vector and its corresponding value
    """
    if not bnb_method and not random_search_method:
        raise Exception("At least one of the methods should be selected")

    best_solution = [None]  # Using list for mutable reference
    best_value = [float('inf')]
    binary_vector = [random.choice([True, False]) for _ in range(n)]

    # Pass the objective function as an argument to branch_and_bound
    list_of_initial_vectors = []
    overall_best_value = float('inf')
    overall_best_solution = None
    if bnb_method and not random_search_method and n_iter > 1:
        n_iter = 1
        if verbose > 0:
            print("Branch-and-bound method selected only, number of iteration will be set to 1")

    if random_search_method and bnb_method:
        method = 'bounds and branches random search'
    elif random_search_method:
        method = 'random search'
    else:
        method = 'bounds and branches'

    for i in tqdm.tqdm(range(n_iter), disable=(verbose != 1), desc=f'cbtbc model. Training. Method:{method}'):
        if random_search_method:
            while binary_vector in list_of_initial_vectors:
                binary_vector = [random.choice([True, False]) for _ in range(n)]
            list_of_initial_vectors.append(binary_vector.copy())
        else:
            binary_vector = [False] * n

        if bnb_method:
            best_solution = [None]
            best_value = [float('inf')]
            branch_and_bound(binary_vector, 0, best_solution, best_value, objective_function)
        else:
            initial_value = objective_function(binary_vector)
            best_solution = [binary_vector]
            best_value = [initial_value]

        if overall_best_solution is None or best_value[0] < overall_best_value:
            overall_best_solution = best_solution[0]
            overall_best_value = best_value[0]
            list_of_initial_vectors.append(overall_best_solution)
            if verbose >= 2:
                print(f"Iter:{i} new best value: {overall_best_value} ")

    return overall_best_solution, overall_best_value


def objective_function(x):
    """
    Example objective function to demonstrate the usage of the optimization functions.

    :param x: Binary vector to be evaluated
    :return: Numerical value representing the "cost" of the binary vector
    """
    global binary_vector_test
    i = 0
    sumv = len(x)
    for el in x:
        if el == binary_vector_test[i]:
            sumv -= 1
        i += 1
    return sumv