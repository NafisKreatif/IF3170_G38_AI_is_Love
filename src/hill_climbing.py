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

def hill_climbing(initial, max_sideways = 20, max_iterations = 500, rng = None, reset_sideways_on_improve=True, detail=False):
    # Steepest Ascent HC + Sideway
    if max_sideways < 0 or max_iterations < 0:
        raise ValueError("Limit tidak boleh negatif")

    if not initial.is_valid():
        raise ValueError("Initial state tidak valid")

    rng = rng or random.Random()
    start_time = time.perf_counter()
    current = initial.copy()
    initial_score = current_score = love_score(current)

    history = [current_score]
    visited = {my_identity(current)}
    sideway_streak = sideway_count = 0
    stop_reason = "max iteration count"

    for iteration in range(max_iterations):
        neighbors = [
            n for n in get_childhood_neighbors(current)
            if my_identity(n) not in visited
        ]

        if not neighbors:
            stop_reason = "no more neighbors"
            break

        scored = [(love_score(n), n) for n in neighbors]
        best_score = max(score for score, _ in scored)

        if best_score < current_score:
            stop_reason = "sudah Local Optimum"
            break

        if best_score == current_score:
            if sideway_streak >= max_sideways:
                stop_reason = "max sideway count"
                break

            sideway_streak += 1
            sideway_count += 1
        elif reset_sideways_on_improve:
            sideway_streak = 0

        current = rng.choice([
            n for score, n in scored if score == best_score
        ])
        current_score = best_score
        visited.add(my_identity(current))
        history.append(current_score)

        if detail:
            print(f"Iterasi {iteration + 1}: "  f"score={current_score} (sideways={sideway_streak})")

    return {
        "initial_state": initial,
        "final_state": current,
        "initial_value": initial_score,
        "final_value": current_score,
        "history": history,
        "iterations": len(history) - 1,
        "sideway_count": sideway_count,
        "max_sideways": max_sideways,
        "stop_reason": stop_reason,
        "duration": time.perf_counter() - start_time,
    }

def run_hill_climbing(isekai, max_sideways=20, max_iterations=500, include_prob=0.5, seed=None, detail=False):
    rng = random.Random(seed)
    initial_state = generate_heroine(isekai, include_prob=include_prob, rng=rng)
    return hill_climbing(initial_state, max_sideways=max_sideways, max_iterations=max_iterations, rng=rng, detail=detail)

# isekai = load_isekai_from_file("../data/testcase_1.json")
# result = run_hill_climbing(isekai, max_sideways=20, max_iterations=500, seed=42)

# print(result["final_value"])