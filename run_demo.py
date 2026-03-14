from pathlib import Path

from src.classical_solver import solve_bruteforce
from src.grover_solver import QuantumSudokuSolver
from src.puzzle_engine import SudokuPuzzle
from src.utils import ensure_dir, save_figure
from src.visualizer import SudokuVisualizer


def main() -> None:
    puzzle = SudokuPuzzle.from_json("puzzles/2x2/puzzle_002_one_clue.json")
    solver = QuantumSudokuSolver(puzzle)
    result = solver.solve_with_visualization(shots=1024)

    visualizer = SudokuVisualizer()

    ensure_dir("results/figures")
    ensure_dir("results/circuits")
    ensure_dir("results/benchmarks")

    solved_fig = visualizer.draw_puzzle(puzzle, result["decoded_solution"])
    save_figure(solved_fig, "results/figures/solved_puzzle.png")

    histogram_fig = visualizer.plot_measurement_histogram(
        result["counts"], solver.valid_bitstrings
    )
    save_figure(histogram_fig, "results/figures/measurement_histogram.png")

    prob_fig = visualizer.plot_probability_evolution(
        result["statevectors"], solver.valid_bitstrings
    )
    save_figure(prob_fig, "results/figures/probability_evolution.png")

    amp_fig = visualizer.plot_amplitude_evolution(
        result["statevectors"], solver.valid_bitstrings
    )
    save_figure(amp_fig, "results/figures/amplitude_evolution.png")

    geom_fig = visualizer.plot_grover_geometry(
        n_qubits=solver.n_value_qubits,
        n_solutions=max(1, len(solver.valid_bitstrings)),
        n_iterations=result["n_iterations"],
    )
    save_figure(geom_fig, "results/figures/grover_geometry.png")

    sp_fig = visualizer.plot_success_probability_vs_iterations(
        n_qubits=solver.n_value_qubits,
        n_solutions=max(1, len(solver.valid_bitstrings)),
        max_iter=10,
    )
    save_figure(sp_fig, "results/figures/success_vs_iterations.png")

    circuit_fig = visualizer.draw_circuit(result["circuit"])
    circuit_fig.savefig("results/circuits/full_grover_circuit.png", bbox_inches="tight")

    oracle_fig = visualizer.draw_oracle_circuit(solver.oracle_builder.build_oracle())
    oracle_fig.savefig("results/circuits/oracle_circuit.png", bbox_inches="tight")

    classical = solve_bruteforce(puzzle)
    with open("results/benchmarks/comparison.csv", "w", encoding="utf-8") as f:
        f.write("method,queries\n")
        f.write(f"classical_bruteforce,{classical['n_queries']}\n")
        f.write(f"quantum_grover,{result['n_iterations']}\n")

    print("Demo artifacts generated under results/")


if __name__ == "__main__":
    main()
