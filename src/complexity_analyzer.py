import math
from typing import Dict, List

import matplotlib.pyplot as plt


def analyze_circuit(circuit) -> Dict:
    ops = circuit.count_ops()
    return {
        "gate_count": int(sum(ops.values())),
        "depth": int(circuit.depth()),
        "n_qubits": int(circuit.num_qubits),
        "n_classical_bits": int(circuit.num_clbits),
        "ops": {k: int(v) for k, v in ops.items()},
    }


def estimate_qubits_for_size(size: int, n_unknowns: int) -> Dict:
    bits_per_cell = math.ceil(math.log2(size))
    value_qubits = n_unknowns * bits_per_cell
    approx_constraint_pairs = n_unknowns * max(1, size - 1)
    ancillas = approx_constraint_pairs
    return {
        "size": size,
        "n_unknowns": n_unknowns,
        "bits_per_cell": bits_per_cell,
        "value_qubits": value_qubits,
        "ancilla_qubits": ancillas,
        "total_qubits": value_qubits + ancillas + 1,
    }


def plot_scaling_analysis():
    sizes = [2, 4, 9, 16, 25]
    totals = [estimate_qubits_for_size(s, min(s * s, 8))["total_qubits"] for s in sizes]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(sizes, totals, marker="o")
    ax.set_xlabel("Puzzle size")
    ax.set_ylabel("Estimated total qubits")
    ax.set_title("Qubit scaling estimate")
    return fig


def generate_complexity_report(puzzle, circuit) -> str:
    stats = analyze_circuit(circuit)
    return (
        f"# Complexity Report\n"
        f"- Size: {puzzle.size}x{puzzle.size}\n"
        f"- Unknowns: {puzzle.get_num_unknowns()}\n"
        f"- Qubits: {stats['n_qubits']}\n"
        f"- Depth: {stats['depth']}\n"
        f"- Gate count: {stats['gate_count']}\n"
    )
