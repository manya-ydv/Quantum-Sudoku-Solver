import itertools
from typing import Dict, List, Tuple

from .puzzle_engine import SudokuPuzzle


class SudokuEncoder:
    def __init__(self, puzzle: SudokuPuzzle):
        self.puzzle = puzzle
        self.bits_per_cell = puzzle.get_bits_per_cell()
        self.empty_cells = puzzle.get_empty_cells()
        self.clues = puzzle.get_clue_cells()
        self._encoding = self.encode()

    def encode(self) -> Dict:
        cell_to_qubits: Dict[Tuple[int, int], List[int]] = {}
        qubit_to_cell: Dict[int, Tuple[int, int, int]] = {}

        q_idx = 0
        for cell in self.empty_cells:
            qubits = list(range(q_idx, q_idx + self.bits_per_cell))
            cell_to_qubits[cell] = qubits
            for bit_pos, qubit in enumerate(qubits):
                qubit_to_cell[qubit] = (cell[0], cell[1], bit_pos)
            q_idx += self.bits_per_cell

        n_value_qubits = q_idx
        n_ancilla_qubits = len(self.puzzle.get_constraint_pairs_for_unknowns())
        n_output_qubit = 1

        constraint_pairs = []
        ancilla_offset = n_value_qubits
        for idx, (cell_a, cell_b, val_a, val_b) in enumerate(self.puzzle.get_constraint_pairs_for_unknowns()):
            constraint_pairs.append(
                {
                    "cell_a": cell_a,
                    "cell_b": cell_b,
                    "qubits_a": cell_to_qubits.get(cell_a),
                    "qubits_b": cell_to_qubits.get(cell_b),
                    "known_val_a": val_a,
                    "known_val_b": val_b,
                    "ancilla_qubit": ancilla_offset + idx,
                }
            )

        return {
            "n_value_qubits": n_value_qubits,
            "n_ancilla_qubits": n_ancilla_qubits,
            "n_output_qubit": n_output_qubit,
            "total_qubits": n_value_qubits + n_ancilla_qubits + n_output_qubit,
            "cell_to_qubits": cell_to_qubits,
            "qubit_to_cell": qubit_to_cell,
            "clue_values": self.clues,
            "constraint_pairs": constraint_pairs,
        }

    @property
    def mapping(self) -> Dict:
        return self._encoding

    def get_state_preparation_circuit(self):
        from qiskit import QuantumCircuit

        qc = QuantumCircuit(self.mapping["n_value_qubits"])
        for qubit in range(self.mapping["n_value_qubits"]):
            qc.h(qubit)
        return qc

    def decode_bitstring(self, bitstring: str) -> List[List[int]]:
        grid = [[self.puzzle.grid[r][c] for c in range(self.puzzle.size)] for r in range(self.puzzle.size)]
        reversed_bits = bitstring[::-1]
        for cell, qubits in self.mapping["cell_to_qubits"].items():
            value = 0
            for bit_pos, qubit in enumerate(qubits):
                value |= (int(reversed_bits[qubit]) << bit_pos)
            grid[cell[0]][cell[1]] = value
        return grid

    def _bitstring_for_assignment(self, values: List[int]) -> str:
        n = self.mapping["n_value_qubits"]
        q_bits = ["0"] * n
        for idx, cell in enumerate(self.empty_cells):
            value = values[idx]
            qubits = self.mapping["cell_to_qubits"][cell]
            for bit_pos, qubit in enumerate(qubits):
                q_bits[qubit] = str((value >> bit_pos) & 1)
        return "".join(reversed(q_bits))

    def get_valid_bitstrings(self) -> List[str]:
        if not self.empty_cells:
            solved = [[self.puzzle.grid[r][c] for c in range(self.puzzle.size)] for r in range(self.puzzle.size)]
            return [""] if self.puzzle.validate_solution(solved) else []

        valid = []
        for assignment in itertools.product(range(self.puzzle.size), repeat=len(self.empty_cells)):
            test_grid = [[self.puzzle.grid[r][c] for c in range(self.puzzle.size)] for r in range(self.puzzle.size)]
            for value, (r, c) in zip(assignment, self.empty_cells):
                test_grid[r][c] = value
            if self.puzzle.validate_solution(test_grid):
                valid.append(self._bitstring_for_assignment(list(assignment)))
        return valid

    def print_mapping(self) -> str:
        lines = [f"Value qubits: {self.mapping['n_value_qubits']}"]
        for cell, qubits in self.mapping["cell_to_qubits"].items():
            lines.append(f"cell {cell} -> {qubits}")
        for cell, value in self.mapping["clue_values"].items():
            lines.append(f"cell {cell} fixed={value}")
        return "\n".join(lines)
