import math
import random
from data import *
from genetic_algorithm import *

def random_successor(config: IsekaiConfiguration) -> IsekaiConfiguration:

    successor = config.copy()

    match random.randint(0, 2):
        case 0: kesenggol(successor)
        case 1: keguling(successor)
        case 2: ketukar(successor)

    return successor

# https://tenor.com/view/thats-a-nice-argument-senator-why-dont-you-back-it-up-with-a-source-gif-26196944
# https://algorithmafternoon.com/books/simulated_annealing/chapter02/

def linear_schedule(T0: float = 100.0, T_end: float = 0.0, steps: int = 1000):
    def schedule(t: int) -> float:
        if t >= steps:
            return 0.0
        return T0 - (T0 - T_end) * (t/steps)
    return schedule

def exponent_schedule(T0: float = 100.0, alpha: float = 0.67, steps: int = 1000):
    def schedule(t: int) -> float:
        if t >= steps:
            return 0.0
        return T0 * (alpha ** t)
    return schedule


def post_honeymoon(isekai: Isekai, schedule, initial_state: IsekaiConfiguration = None, max_iterations: int = 1000) -> IsekaiConfiguration:

    if initial_state is not None:
        current = initial_state.copy()
    else:
        current = ngasal(isekai)

    current_value = kesejahteraan(current)

    for t in range(1, max_iterations + 1):
        T = schedule(t)
        if T == 0:
            return current

        next_state = random_successor(current)
        next_value = kesejahteraan(next_state)

        deltaE = next_value - current_value

        if deltaE > 0:
            current = next_state
            current_value = next_value
        else:
            if random.random() < math.exp(deltaE / T):
                current = next_state
                current_value = next_value

    return current