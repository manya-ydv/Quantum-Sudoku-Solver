from typing import Dict, List, Optional

from .binary_encoder import SudokuEncoder


class SudokuOracle:
    def __init__(self, encoder: SudokuEncoder):
        self.encoder = encoder
        self.valid_bitstrings = encoder.get_valid_bitstrings()

    @staticmethod
    def _phase_flip_on_state(qc, display_bitstring: str) -> None:
        n = len(display_bitstring)
        q_order = display_bitstring[::-1]
        for i, bit in enumerate(q_order):
            if bit == "0":
                qc.x(i)
        if n == 1:
            qc.z(0)
        else:
            target = n - 1
            controls = list(range(n - 1))
            qc.h(target)
            qc.mcx(controls, target)
            qc.h(target)
        for i, bit in enumerate(q_order):
            if bit == "0":
                qc.x(i)

    def build_oracle(self):
        from qiskit import QuantumCircuit

        n = self.encoder.mapping["n_value_qubits"]
        qc = QuantumCircuit(n, name="SudokuOracle")
        if n == 0:
            return qc
        for bitstring in self.valid_bitstrings:
            self._phase_flip_on_state(qc, bitstring)
        return qc

    def build_oracle_boolean_expr(self):
        raise NotImplementedError("Boolean-expression oracle is not implemented in this MVP")

    def verify_oracle(self, oracle_circuit=None) -> Dict[str, bool]:
        n = self.encoder.mapping["n_value_qubits"]
        valid = set(self.valid_bitstrings)
        results = {}
        for i in range(2**n):
            bitstring = format(i, f"0{n}b")
            results[bitstring] = bitstring in valid
        return results

    def get_oracle_stats(self) -> Dict[str, int]:
        oracle = self.build_oracle()
        ops = oracle.count_ops()
        return {
            "depth": oracle.depth(),
            "n_qubits": oracle.num_qubits,
            "gate_count": sum(ops.values()),
            "cx": int(ops.get("cx", 0)),
            "x": int(ops.get("x", 0)),
            "h": int(ops.get("h", 0)),
            "mcx": int(ops.get("mcx", 0)),
        }


def apply_xor_check_1bit(qc, qubit_a: int, qubit_b: int, ancilla: int) -> None:
    qc.cx(qubit_a, ancilla)
    qc.cx(qubit_b, ancilla)


def apply_xor_check_1bit_with_known(qc, qubit_unknown: int, known_value: int, ancilla: int) -> None:
    qc.cx(qubit_unknown, ancilla)
    if known_value == 1:
        qc.x(ancilla)
