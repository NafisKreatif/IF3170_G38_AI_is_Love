from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt

from data import load_isekai_from_file
from genetic_algorithm import dolan as run_genetic_algorithm_v1
from genetic_algorithm import kesejahteraan as genetic_package_value_v1
from genetic_algorithm_v2 import dolan as run_genetic_algorithm_v2
from genetic_algorithm_v2 import kesejahteraan as genetic_package_value_v2
from hill_climbing import (
    run_random_restart_hc,
    run_sideway_hill_climbing,
    run_steepest_hill_climbing,
    run_stochastic_hill_climbing,
)
from simulated_annealing import exponent_schedule, post_honeymoon
from visualization import save_state_comparison


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RESULTS_DIR = PROJECT_ROOT / "results"
ALGORITHM_LABELS = {
    "hc": "Hill Climbing (HC)",
    "sa": "Simulated Annealing (SA)",
    "ga": "Genetic Algorithm v1 (GA)",
    "ga2": "Genetic Algorithm v2 (GA2)",
}


def normalize_result(algorithm: str, result: dict[str, Any]) -> dict[str, Any]:
    """Samakan format hasil algoritma untuk ringkasan dan grafik."""
    history = {
        "best_valid_value": [],
        "current_fitness": [],
        "population_mean_objective": [],
        "diagnostics": {},
    }

    if algorithm == "hc":
        # Simpan nilai terbaik sejauh ini, termasuk jika HC melakukan restart.
        best_so_far = 0
        for value in result.get("history", []):
            best_so_far = max(best_so_far, value)
            history["best_valid_value"].append(best_so_far)
    elif algorithm == "sa":
        # History SA bisa memuat state antara yang tidak valid(buat diagnostik)
        # State akhir adalah state valid terbaik.
        history["diagnostics"]["current_package_value"] = result.get("value_history", [])
    elif algorithm == "ga" or algorithm == "ga2":
        history["diagnostics"]["population_best_objective"] = result.get("best_value_history", [])
        history["diagnostics"]["population_best_fitness"] = result.get("max_fitness_history", [])
        history["diagnostics"]["population_mean_fitness"] = result.get("avg_fitness_history", [])
        history["diagnostics"]["population_worst_fitness"] = result.get("min_fitness_history", [])

    initial_value = result.get("initial_value")
    final_value = result.get("final_value")
    if algorithm in ("ga", "ga2"):
        initial_state = result.get("initial_state")
        final_state = result.get("final_state")
        if algorithm == "ga":
            package_value = genetic_package_value_v1
            value_kwargs = {}
        else:
            package_value = genetic_package_value_v2
            value_kwargs = {"check_validity": True}
        initial_value = (
            package_value(initial_state, **value_kwargs)
            if initial_state is not None and initial_state.is_valid()
            else None
        )
        final_value = (
            package_value(final_state, **value_kwargs)
            if final_state is not None and final_state.is_valid()
            else None
        )

    return {
        "algorithm": algorithm,
        "initial_state": result.get("initial_state"),
        "final_state": result.get("final_state"),
        "initial_value": initial_value,
        "final_value": final_value,
        "iterations": result.get("iterations", 0),
        "duration": result.get("duration", 0.0),
        "history": history,
        "raw_result": result,
    }


def run_selected_algorithm(args: argparse.Namespace, isekai) -> dict[str, Any]:
    if args.algorithm == "hc":
        common = {"max_iterations": args.iterations}
        if args.hc_mode == "steepest":
            result = run_steepest_hill_climbing(isekai, **common)
        elif args.hc_mode == "stochastic":
            result = run_stochastic_hill_climbing(isekai, **common)
        elif args.hc_mode == "sideway":
            result = run_sideway_hill_climbing(isekai, **common)
        else:
            result = run_random_restart_hc(
                isekai,
                max_restarts=args.restarts,
                max_iterations=args.iterations,
            )
    elif args.algorithm == "sa":
        schedule = exponent_schedule(steps=args.iterations + 1)
        result = post_honeymoon(
            isekai,
            schedule,
            max_iterations=args.iterations,
        )
    elif args.algorithm == "ga":
        result = run_genetic_algorithm_v1(
            isekai,
            generation=args.iterations,
            jumlah_penduduk=args.population,
        )
    else:
        result = run_genetic_algorithm_v2(
            isekai,
            generation=args.iterations,
            jumlah_penduduk=args.population,
        )

    total_value = 0
    for packages in isekai.packages:
        total_value += packages.value
    result["max_value"] = total_value
    
    return normalize_result(args.algorithm, result)


def print_summary(result: dict[str, Any], args: argparse.Namespace, output_path) -> None:
    final_state = result["final_state"]
    valid = final_state is not None and final_state.is_valid()
    print("\n===== Ringkasan hasil =====")
    print(f"Algoritma       : {ALGORITHM_LABELS[result['algorithm']]}")
    print(f"Testcase        : {args.testcase}")
    if result["algorithm"] == "hc":
        print(f"Mode HC         : {args.hc_mode.replace('-', ' ').title()}")
        if args.hc_mode == "random-restart":
            print(f"Jumlah restart  : {result['raw_result'].get('restarts', 0)}/{args.restarts}")
    elif result["algorithm"] in ("ga", "ga2"):
        print(f"Ukuran populasi : {args.population}")
    print(f"Nilai terbaik yang mungkin : {result['raw_result'].get('max_value')}")
    print(f"Nilai awal      : {result['initial_value']}")
    print(f"Nilai akhir     : {result['final_value']}")
    print(f"State akhir     : {'valid' if valid else 'tidak ada solusi valid'}")
    if result["algorithm"] == "hc" and args.hc_mode == "random-restart":
        print(
            f"Iterasi total    : {result['iterations']} "
            f"(maks. {args.iterations} per restart)"
        )
    else:
        print(f"Iterasi/generasi: {result['iterations']}/{args.iterations}")
    print(f"Durasi          : {result['duration']:.3f} detik")

    stop_reason = result["raw_result"].get("stop_reason")
    if stop_reason:
        print(f"Alasan berhenti : {stop_reason}")

    with open(output_path, "w") as output_file:
        output_file.write("\n===== Ringkasan hasil =====")
        output_file.write(f"Algoritma       : {ALGORITHM_LABELS[result['algorithm']]}")
        output_file.write(f"Testcase        : {args.testcase}")
        if result["algorithm"] == "hc":
            output_file.write(f"Mode HC         : {args.hc_mode.replace('-', ' ').title()}")
            if args.hc_mode == "random-restart":
                output_file.write(f"Jumlah restart  : {result['raw_result'].get('restarts', 0)}/{args.restarts}")
        elif result["algorithm"] in ("ga", "ga2"):
            output_file.write(f"Ukuran populasi : {args.population}")
        output_file.write(f"Nilai terbaik yang mungkin : {result['raw_result'].get('max_value')}")
        output_file.write(f"Nilai awal      : {result['initial_value']}")
        output_file.write(f"Nilai akhir     : {result['final_value']}")
        output_file.write(f"State akhir     : {'valid' if valid else 'tidak ada solusi valid'}")
        if result["algorithm"] == "hc" and args.hc_mode == "random-restart":
            output_file.write(
                f"Iterasi total    : {result['iterations']} "
                f"(maks. {args.iterations} per restart)"
            )
        else:
            output_file.write(f"Iterasi/generasi: {result['iterations']}/{args.iterations}")
        output_file.write(f"Durasi          : {result['duration']:.3f} detik")

        if stop_reason:
            output_file.write(f"Alasan berhenti : {stop_reason}")


def plot_history(result: dict[str, Any], output_path: Path) -> None:
    history = result["history"]
    fig, ax = plt.subplots(figsize=(9, 5))
    has_series = False

    if history["best_valid_value"]:
        values = history["best_valid_value"]
        label = "Best valid package value"
        ax.plot(range(len(values)), values, label=label)
        has_series = True

    diagnostics = history["diagnostics"]
    if "current_package_value" in diagnostics:
        values = diagnostics["current_package_value"]
        ax.plot(range(len(values)), values, label="SA current package value")
        has_series = True

    for key, label in (
        ("population_best_objective", "GA best objective"),
        ("population_best_fitness", "GA best fitness"),
        ("population_mean_fitness", "GA mean fitness"),
        ("population_worst_fitness", "GA worst fitness"),
    ):
        if result["algorithm"] == "ga":
            label = label.replace("GA", "GAv1")
        else:
            label = label.replace("GA", "GAv2")
        values = diagnostics.get(key)
        if values:
            ax.plot(range(len(values)), values, label=label)
            has_series = True

    if not has_series:
        plt.close(fig)
        print("Tidak ada data riwayat untuk dibuat grafik.")
        return

    ax.set_title(f"{result['algorithm'].upper()} history")
    ax.set_xlabel("Iteration / generation")
    ylabel = "Fitness (package value + penalties)" if result["algorithm"].startswith("ga") else "Objective value"
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.tight_layout()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Grafik riwayat disimpan: {output_path}")


def parse_args() -> argparse.Namespace:
    testcase_files = sorted(path.name for path in DATA_DIR.glob("*.json"))
    parser = argparse.ArgumentParser(
        description="Menjalankan algoritma pencarian untuk menyusun paket ke dalam truk.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog=(
            "Contoh:\n"
            "  python src/main.py --algorithm hc --hc-mode sideway --testcase testcase_1.json\n"
            "  python src/main.py --algorithm sa --iterations 1000\n"
            "  python src/main.py --algorithm ga2 --population 50 --iterations 100"
        ),
    )
    parser.add_argument(
        "--testcase",
        choices=testcase_files,
        default="testcase_1.json",
        help="Nama berkas testcase JSON di folder data.",
    )
    parser.add_argument(
        "--algorithm",
        choices=("hc", "sa", "ga", "ga2"),
        default="hc",
        help="Algoritma: hc (Hill Climbing), sa (Simulated Annealing), ga (GA v1), ga2 (GA v2).",
    )
    parser.add_argument(
        "--hc-mode",
        choices=("steepest", "stochastic", "sideway", "random-restart"),
        default="sideway",
        help="Varian Hill Climbing; hanya digunakan jika --algorithm hc.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=500,
        help="Batas iterasi untuk HC/SA atau jumlah generasi untuk GA.",
    )
    parser.add_argument(
        "--restarts",
        type=int,
        default=5,
        help="Jumlah maksimum restart untuk HC mode random-restart.",
    )
    parser.add_argument(
        "--population",
        type=int,
        default=50,
        help="Ukuran populasi; hanya digunakan oleh GA dan GA2.",
    )
    parser.add_argument(
        "--no-plot",
        action="store_true",
        help="Jangan simpan grafik riwayat PNG; visualisasi 3D tetap dibuat jika solusi valid.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    isekai = load_isekai_from_file(str(DATA_DIR / args.testcase))
    result = run_selected_algorithm(args, isekai)
    print_summary(result, args, output_path = RESULTS_DIR / f"{args.algorithm}_{Path(args.testcase).stem}.txt")

    initial_state = result["initial_state"]
    final_state = result["final_state"]
    if initial_state is not None and final_state is not None and final_state.is_valid():
        output_path = RESULTS_DIR / f"{args.algorithm}_{Path(args.testcase).stem}_3d.html"
        saved_path = save_state_comparison(
            isekai,
            initial_state,
            final_state,
            output_path,
            run_summary=result,
        )
        print(f"Visualisasi 3D disimpan: {saved_path}")
    else:
        print("Visualisasi 3D dilewati karena tidak ada state akhir yang valid.")

    if not args.no_plot:
        output_path = RESULTS_DIR / f"{args.algorithm}_{Path(args.testcase).stem}.png"
        plot_history(result, output_path)


if __name__ == "__main__":
    main()
