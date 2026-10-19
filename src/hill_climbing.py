import itertools
import random
import time

from data import *

AXES = ("x", "y", "z")

#ukuran pada orientasi berbeda
def love_size(package, orientation):
    dimensions = {
        orientation.width_orientation: package.dimensions.width,
        orientation.length_orientation: package.dimensions.length,
        orientation.height_orientation: package.dimensions.height,
    }
    return dimensions["x"], dimensions["y"], dimensions["z"]

# semua orientasi yg bisa
def heavy_rotation(package):
    result, seen = [], set()

    for axes in itertools.permutations(AXES):
        orientation = Orientation(*axes)
        size = love_size(package, orientation)
        if size not in seen:
            result.append(orientation)
            seen.add(size)
    return result

# bisa masuk truck atau tidak
def will_it_work(truck, package, pos, orientation):
    x, y, z = love_size(package, orientation)
    d = truck.dimensions
    return (
        pos.x >= 0 and pos.y >= 0 and pos.z >= 0
        and pos.x + x <= d.width
        and pos.y + y <= d.length
        and pos.z + z <= d.height
    )

# hindarin state duplikat
def my_identity(state):
    result = []
    for package in state.isekai.packages:
        truck = state.get_package_truck(package)

        if truck is None:
            result.append((package.id, None))
            continue

        p = state.get_package_position(package)
        o = state.get_package_orientation(package)

        result.append((package.id, truck.id, p.x, p.y, p.z, o.width_orientation, o.height_orientation, o.length_orientation))

    return tuple(result)

# add package 
def new_chapter(state, package, truck, pos, orientation):
    candidate = state.copy()
    candidate.package_truck[package] = truck
    candidate.package_position[package] = pos.copy()
    candidate.package_orientation[package] = orientation.copy()
    return candidate

# remove package
def breakup(state, package):
    candidate = state.copy()
    candidate.package_truck.pop(package, None)
    candidate.package_position.pop(package, None)
    candidate.package_orientation.pop(package, None)
    return candidate

#posisi kandidat
def heroine_candidate(state, truck, skip = None):
    anchors = {(0, 0, 0)}

    for package in state.isekai.packages:
        if package is skip or state.get_package_truck(package) is not truck:
            continue

        low, high = state.calculate_bound(package)
        anchors.update((
            (high.x, low.y, low.z),
            (low.x, high.y, low.z),
            (low.x, low.y, high.z),
        ))
    return [Position(*p) for p in anchors]

#value 
def love_score(state):
    score = 0

    for p in state.isekai.packages:
        if state.get_package_truck(p) is not None:
            score += p.value

    return score

#config awal random
def generate_heroine(isekai, include_prob=0.5, rng = None):
    # initial config random
    if not 0 <= include_prob <= 1:
        raise ValueError("include_prob must be between 0 and 1")

    rng = rng or random.Random()
    state = IsekaiConfiguration(isekai)
    packages = list(isekai.packages)
    rng.shuffle(packages)

    for package in packages:
        if rng.random() > include_prob:
            continue

        trucks = list(isekai.trucks)
        rng.shuffle(trucks)
        orientations = heavy_rotation(package)
        rng.shuffle(orientations)

        for truck in trucks:
            positions = heroine_candidate(state, truck)
            rng.shuffle(positions)

            for pos in positions:
                for orientation in orientations:
                    if not will_it_work(truck, package, pos, orientation):
                        continue

                    candidate = new_chapter(state, package, truck, pos, orientation)

                    if candidate.is_valid():
                        state = candidate
                        break
                else:
                    continue
                break
            else:
                continue
            break
    return state

# semua neighbor yang mungkin
def get_childhood_neighbors(state):
    neighbors = []
    seen = {my_identity(state)}

    def add(candidate):
        key = my_identity(candidate)
        if key not in seen and candidate.is_valid():
            seen.add(key)
            neighbors.append(candidate)
    packages = state.isekai.packages

    for package in packages:
        old_truck = state.get_package_truck(package)
        old_pos = state.get_package_position(package)
        old_orientation = state.get_package_orientation(package)

        if old_truck is not None:
            base = breakup(state, package)
        else:
            base = state

        if old_truck is not None:
            add(base)

        if old_orientation is None:
            orientations = heavy_rotation(package)
        else:
            orientations = [old_orientation]

        for truck in state.isekai.trucks:
            for pos in heroine_candidate(base, truck):
                if old_truck is truck and old_pos is not None:
                    if (pos.x, pos.y, pos.z) == (old_pos.x, old_pos.y, old_pos.z):
                        continue

                for orientation in orientations:
                    if will_it_work(truck, package, pos, orientation):
                        add(new_chapter(base, package, truck, pos, orientation))

        if old_truck is not None:
            old_size = love_size(package, old_orientation)

            for orientation in heavy_rotation(package):
                if love_size(package, orientation) == old_size:
                    continue

                if will_it_work(old_truck, package, old_pos, orientation):
                    add(new_chapter(state, package, old_truck, old_pos, orientation))

    # tuker posisi / ganti paket baru
    for a in packages:
        if state.get_package_truck(a) is not None:
            continue

        for b in packages:
            truck_b = state.get_package_truck(b)
            if truck_b is None:
                continue

            pos_b = state.get_package_position(b)
            base = breakup(state, b)

            for orientation_a in heavy_rotation(a):
                if not will_it_work(truck_b, a, pos_b, orientation_a):
                    continue

                replaced = new_chapter(base, a, truck_b, pos_b, orientation_a)
                add(replaced)

                for pos_b_new in heroine_candidate(replaced, truck_b, skip=a):
                    for orientation_b in [state.get_package_orientation(b)]:
                        if not will_it_work(truck_b, b, pos_b_new, orientation_b):
                            continue
                        candidate = new_chapter(replaced, b, truck_b, pos_b_new, orientation_b)
                        add(candidate)

    # swap posisi paket
    for i, a in enumerate(packages):
        truck_a = state.get_package_truck(a)
        if truck_a is None:
            continue
        for b in packages[i + 1:]:
            truck_b = state.get_package_truck(b)
            if truck_b is None:
                continue
            candidate = state.copy()
            candidate.package_truck[a], candidate.package_truck[b] = truck_b, truck_a
            candidate.package_position[a] = state.get_package_position(b)
            candidate.package_position[b] = state.get_package_position(a)
            candidate.package_orientation[a] = state.get_package_orientation(b)
            candidate.package_orientation[b] = state.get_package_orientation(a)
            add(candidate)

    return neighbors

def total_value(isekai):
    return sum(p.value for p in isekai.packages)

def climbing(initial, mode = "Steepest", max_iterations = 500, rng = None, detail = False, max_sideways = 0, reset_sideways_on_improve = True, isekai = None):
    if mode not in ("Steepest", "Stochastic"):
        raise ValueError("Mode harus 'Steepest' atau 'Stochastic'")
    if max_iterations < 0 or max_sideways < 0:
        raise ValueError("Limit tidak boleh negatif")
    if not initial.is_valid():
        raise ValueError("Initial state tidak valid")

    rng = rng or random.Random()
    isekai = isekai or initial.isekai
    start_time = time.perf_counter()
    upper_bound = total_value(isekai)
    current = initial.copy()
    current_score = initial_score = love_score(current)
    our_history = [current_score]

    visited = {my_identity(current)} if max_sideways > 0 else None

    sideway_streak = sideway_count = 0
    stop_reason = "max iteration count"

    for iteration in range(max_iterations):
        if current_score >= upper_bound:
            stop_reason = "Semua paket sudah masuk truck"
            break

        neighbors = get_childhood_neighbors(current)
        if visited is not None:
            neighbors = [n for n in neighbors if my_identity(n) not in visited]
        if not neighbors:
            stop_reason = "no more neighbors"
            break
        scored = [(love_score(n), n) for n in neighbors]
        best_score = max(score for score, _ in scored)

        if best_score < current_score:
            stop_reason = "sudah Local Optimum"
            break

        if best_score == current_score:
            if max_sideways == 0:
                stop_reason = "sudah Local Optimum"
                break
            if sideway_streak >= max_sideways:
                stop_reason = "max sideway count"
                break
            sideway_streak += 1
            sideway_count += 1
            candidates = [n for score, n in scored if score == best_score]

        else:
            if reset_sideways_on_improve:
                sideway_streak = 0
            if mode == "Steepest":
                candidates = [n for score, n in scored if score == best_score]
            else:
                candidates = [n for score, n in scored if score > current_score]

        current = rng.choice(candidates)
        current_score = love_score(current)
        if visited is not None:
            visited.add(my_identity(current))
        our_history.append(current_score)

        if detail:  
            print(f"Iterasi {iteration + 1}: "  f"score={current_score} (sideways={sideway_streak})")

    return {
            "initial_state": initial,
            "final_state": current,
            "initial_value": initial_score,
            "final_value": current_score,
            "history": our_history,
            "iterations": len(our_history) - 1,
            "sideway_count": sideway_count,
            "max_sideways": max_sideways,
            "stop_reason": stop_reason,
            "duration": time.perf_counter() - start_time,
        }

def steepest_hill_climbing(initial, max_iterations = 500, rng = None, detail = False):
    return climbing(initial, "Steepest", max_iterations, rng, detail)

def stochastic_hill_climbing(initial, max_iterations = 500, rng = None, detail = False):
    return climbing(initial, "Stochastic", max_iterations, rng, detail)

def sideway_hill_climbing(initial, max_sideways = 20, max_iterations = 500, rng = None, reset_sideways_on_improve=True, detail=False):
    return climbing(initial, "Steepest", max_iterations, rng, detail, max_sideways, reset_sideways_on_improve)

def random_restart_hc(isekai, max_restarts = 5, max_iterations = 500, include_prob = 0.5, mode = "Steepest",max_sideways = 0, rng = None, detail=False):
    if max_restarts < 1:
        raise ValueError("max_restarts harus >= 1")
    
    rng = rng or random.Random()
    upper_bound = total_value(isekai)
    start_time = time.perf_counter()
    best_state = None
    history = []
    iterations_per_restart = []
    restart_value = []
    stop_reason = "max restart count"

    for i in range(max_restarts):
        initial_state = generate_heroine(isekai, include_prob=include_prob, rng=rng)
        result = climbing(initial_state, mode, max_iterations, rng, detail, max_sideways)
        history.extend(result["history"])
        iterations_per_restart.append(result["iterations"])
        restart_value.append(result["final_value"])

        if best_state is None or result["final_value"] > best_state["final_value"]:
            best_state = result
        if best_state["final_value"] >= upper_bound:
            stop_reason = "Semua paket sudah masuk di Truck"
            break

    return {
            "initial_state": best_state["initial_state"],
            "final_state": best_state["final_state"],
            "initial_value": best_state["initial_value"],
            "final_value": best_state["final_value"],
            "history": history,
            "iterations": sum(iterations_per_restart),
            "restarts": len(iterations_per_restart),
            "max_restarts": max_restarts,
            "iterations_per_restart": iterations_per_restart,
            "restart_value": restart_value,
            "stop_reason": stop_reason,
            "duration": time.perf_counter() - start_time,
        }

def run_steepest_hill_climbing(isekai, max_iterations=500, include_prob=0.5, seed=None, detail=False):
    rng = random.Random(seed)
    initial_state = generate_heroine(isekai, include_prob = include_prob, rng = rng)
    return steepest_hill_climbing(initial_state, max_iterations, rng , detail)

def run_stochastic_hill_climbing(isekai, max_iterations=500, include_prob=0.5, seed=None, detail=False):
    rng = random.Random(seed)
    initial_state = generate_heroine(isekai, include_prob = include_prob, rng = rng)
    return stochastic_hill_climbing(initial_state, max_iterations, rng , detail)

def run_sideway_hill_climbing(isekai, max_sideways=20, max_iterations=500, include_prob=0.5, seed=None, detail=False):
    rng = random.Random(seed)
    initial_state = generate_heroine(isekai, include_prob = include_prob, rng = rng)
    return sideway_hill_climbing(initial_state, max_sideways=max_sideways, max_iterations=max_iterations, rng=rng, detail=detail)

def run_random_restart_hc(isekai, max_restarts = 5, max_iterations = 500, include_prob = 0.5, seed = None, detail = False):
    return random_restart_hc(isekai, max_restarts, max_iterations, include_prob, "Steepest", 0, random.Random(seed), detail)

#contoh:
# isekai = load_isekai_from_file("../data/testcase_1.json")
# result = run_sideway_hill_climbing(isekai, max_sideways=20, max_iterations=500, seed=42)

# print(result["final_value"])