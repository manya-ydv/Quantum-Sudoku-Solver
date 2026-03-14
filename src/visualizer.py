from typing import Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np


class SudokuVisualizer:
    def draw_puzzle(self, puzzle, solution: Optional[List[List]] = None):
        fig, ax = plt.subplots(figsize=(4, 4))
        ax.set_xlim(0, puzzle.size)
        ax.set_ylim(0, puzzle.size)
        ax.invert_yaxis()
        ax.set_xticks(range(puzzle.size + 1))
        ax.set_yticks(range(puzzle.size + 1))
        ax.grid(True)
        for r in range(puzzle.size):
            for c in range(puzzle.size):
                value = puzzle.grid[r][c] if solution is None else solution[r][c]
                if value is None:
                    text = "_"
                    color = "gray"
                else:
                    text = str(value)
                    color = "black" if puzzle.grid[r][c] is not None else "green"
                ax.text(c + 0.5, r + 0.5, text, ha="center", va="center", fontsize=16, color=color)
        ax.set_title("Sudoku")
        return fig

    def draw_circuit(self, circuit, decompose_level: int = 1):
        draw_target = circuit
        for _ in range(decompose_level):
            draw_target = draw_target.decompose()
        return draw_target.draw(output="mpl")

    def draw_oracle_circuit(self, oracle):
        return oracle.draw(output="mpl")

    def plot_amplitude_evolution(self, statevectors, valid_states: List[str]):
        fig, axes = plt.subplots(len(statevectors), 1, figsize=(8, 3 * len(statevectors)))
        if len(statevectors) == 1:
            axes = [axes]
        for idx, sv in enumerate(statevectors):
            amps = np.real(sv.data)
            x = np.arange(len(amps))
            axes[idx].bar(x, amps)
            axes[idx].set_title(f"Iteration {idx}")
        fig.tight_layout()
        return fig

    def plot_probability_evolution(self, statevectors, valid_states: List[str]):
        fig, axes = plt.subplots(len(statevectors), 1, figsize=(8, 3 * len(statevectors)))
        if len(statevectors) == 1:
            axes = [axes]
        for idx, sv in enumerate(statevectors):
            probs = np.abs(sv.data) ** 2
            x = np.arange(len(probs))
            axes[idx].bar(x, probs)
            axes[idx].set_title(f"Iteration {idx}")
        fig.tight_layout()
        return fig

    def animate_grover(self, statevectors, valid_states: List[str], save_path: str = None):
        raise NotImplementedError("Animation is optional in this MVP")

    def plot_measurement_histogram(self, counts: Dict[str, int], valid_states: List[str]):
        fig, ax = plt.subplots(figsize=(8, 4))
        keys = list(counts.keys())
        vals = [counts[k] for k in keys]
        colors = ["green" if k in valid_states else "gray" for k in keys]
        ax.bar(keys, vals, color=colors)
        ax.set_xlabel("Bitstring")
        ax.set_ylabel("Count")
        ax.set_title("Measurement histogram")
        return fig

    def plot_grover_geometry(self, n_qubits: int, n_solutions: int, n_iterations: int):
        N = 2**n_qubits
        theta = np.arcsin(np.sqrt(n_solutions / N)) if N > 0 and n_solutions > 0 else 0.0
        fig, ax = plt.subplots(figsize=(5, 5))
        angles = [(2 * k + 1) * theta for k in range(n_iterations + 1)]
        ax.plot(np.cos(angles), np.sin(angles), marker="o")
        ax.set_title("Grover geometric view")
        ax.set_xlabel("|w⊥>")
        ax.set_ylabel("|w>")
        return fig

    def plot_success_probability_vs_iterations(self, n_qubits: int, n_solutions: int, max_iter: int = 20):
        N = 2**n_qubits
        theta = np.arcsin(np.sqrt(n_solutions / N)) if N > 0 and n_solutions > 0 else 0.0
        ks = np.arange(max_iter + 1)
        probs = np.sin((2 * ks + 1) * theta) ** 2
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(ks, probs)
        ax.set_xlabel("Iterations")
        ax.set_ylabel("Success probability")
        return fig

    def create_comparison_dashboard(self, quantum_results: Dict, classical_results: Dict):
        fig, ax = plt.subplots(figsize=(8, 4))
        labels = ["Quantum", "Classical"]
        values = [
            quantum_results.get("n_iterations", 0),
            classical_results.get("n_queries", 0),
        ]
        ax.bar(labels, values, color=["purple", "orange"])
        ax.set_title("Query comparison")
        return fig

    def plot_qubit_scaling(self, sizes: List[int]):
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(sizes, [s * s for s in sizes], marker="o")
        ax.set_xlabel("Size")
        ax.set_ylabel("Relative qubit demand")
        return fig
