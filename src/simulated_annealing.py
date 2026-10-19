import math
import random
import time
from data import *
from genetic_algorithm_v2 import *


def random_successor(config: IsekaiConfiguration) -> IsekaiConfiguration:

    if isinstance(config, IsekaiOrder):
        successor = config.copy()
    else:
        successor = IsekaiOrder(config.isekai)
        for truck in config.isekai.trucks:
            packages = [
                package for package in config.isekai.packages
                if config.get_package_truck(package) is truck
            ]
            packages.sort(key=lambda package: (
                config.get_package_position(package).y,
                config.get_package_position(package).z,
                config.get_package_position(package).x,
            ))
            for order, package in enumerate(packages):
                successor.configure_package(
                    package,
                    truck,
                    config.get_package_position(package),
                    config.get_package_orientation(package),
                    order=order,
                )

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


def post_honeymoon(isekai: Isekai, schedule, initial_state: IsekaiConfiguration = None, max_iterations: int = 1000, record_every: int = 1) -> dict:

    start_time = time.perf_counter()

    if initial_state is not None:
        current = initial_state.copy()
    else:
        current = ngasal(isekai)

    current_value = kesejahteraan(current)
    current_fitness = current_value + kesengsaraan(current)
    initial_value = current_value
    initial_state = current.copy()

    best_state = current.copy() if current.is_valid() else None
    best_value = current_value if best_state is not None else None

    value_history = [current_value]
    temperature_history = [schedule(0) if max_iterations > 0 else 0.0]
    deltaE_history = [0.0]
    acceptance_prob_history = [1.0]
    accepted_history = [True]
    stuck_history = [0]           # consecutive non-improving accepted steps
    stuck_count = 0               # consecutive iterations with no improvement
    local_optima_count = 0       

    
    PLATEAU_LEN = 67
    plateau_value = current_value
    plateau_len = 0

    for t in range(1, max_iterations + 1):

        T = schedule(t)
        if T == 0:
            break

        next_state = random_successor(current)
        next_value = kesejahteraan(next_state)
        next_fitness = next_value + kesengsaraan(next_state)

        deltaE = next_fitness - current_fitness
        prob = math.exp(deltaE / T) if deltaE <= 0 else 1.0

        accepted = False
        if deltaE > 0:
            current = next_state
            current_value = next_value
            current_fitness = next_fitness
            accepted = True
        else:
            if random.random() < prob:
                current = next_state
                current_value = next_value
                current_fitness = next_fitness
                accepted = True


        if current.is_valid():
            valid_value = kesejahteraan(current, check_validity=True)
            if best_state is None or valid_value > best_value:
                best_value = valid_value
                best_state = current.copy()


        if current_value == plateau_value:
            plateau_len += 1
        else:
            plateau_value = current_value
            plateau_len = 0

        if plateau_len >= PLATEAU_LEN:
            stuck_count += 1
        else:
            stuck_count = 0

        if plateau_len >= PLATEAU_LEN and accepted and deltaE < 0:
            local_optima_count += 1

        # record
        if t % record_every == 0 or t == max_iterations:
            value_history.append(current_value)
            temperature_history.append(T)
            deltaE_history.append(deltaE)
            acceptance_prob_history.append(prob)
            accepted_history.append(accepted)
            stuck_history.append(stuck_count)

    final_value = best_value

    duration = time.perf_counter() - start_time

    return {
        "initial_state": initial_state,
        "final_state": best_state,
        "initial_value": initial_value,
        "final_value": final_value,
        "value_history": value_history,
        "temperature_history": temperature_history,
        "deltaE_history": deltaE_history,
        "acceptance_prob_history": acceptance_prob_history,
        "accepted_history": accepted_history,
        "stuck_history": stuck_history,
        "local_optima_count": local_optima_count,
        "iterations": len(value_history) - 1,
        "max_iterations": max_iterations,
        "duration": duration,
    }
