import math
from typing import Dict, List, Optional, Tuple

from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler
from qiskit.quantum_info import Statevector

from .binary_encoder import SudokuEncoder
from .constraint_oracle import SudokuOracle
from .diffuser import build_diffuser
from .puzzle_engine import SudokuPuzzle
from .solution_decoder import SudokuDecoder


class QuantumSudokuSolver:
    def __init__(self, puzzle: SudokuPuzzle, config: Optional[dict] = None):
        self.puzzle = puzzle
        self.config = config or {}
        self.encoder = SudokuEncoder(puzzle)
        self.oracle_builder = SudokuOracle(self.encoder)
        self.decoder = SudokuDecoder(self.encoder, puzzle)
        self.n_value_qubits = self.encoder.mapping["n_value_qubits"]
        self.valid_bitstrings = self.encoder.get_valid_bitstrings()

    def compute_optimal_iterations(self) -> int:
        n = self.n_value_qubits
        N = 2**n if n > 0 else 1
        M = max(1, len(self.valid_bitstrings))
        k = math.floor((math.pi / 4) * math.sqrt(N / M))
        return max(1, k)

    def build_full_circuit(self, n_iterations: int = None) -> QuantumCircuit:
        if n_iterations is None:
            n_iterations = self.compute_optimal_iterations()

        qc = QuantumCircuit(self.n_value_qubits, self.n_value_qubits)
        oracle = self.oracle_builder.build_oracle()
        diffuser = build_diffuser(self.n_value_qubits)

        if self.n_value_qubits > 0:
            qc.h(range(self.n_value_qubits))
            for _ in range(n_iterations):
                qc.compose(oracle, inplace=True)
                qc.compose(diffuser, inplace=True)
            qc.measure(range(self.n_value_qubits), range(self.n_value_qubits))
        return qc

    def build_grover_high_level(self):
        from qiskit_algorithms import AmplificationProblem, Grover

        oracle = self.oracle_builder.build_oracle()
        problem = AmplificationProblem(
            oracle=oracle,
            is_good_state=self.valid_bitstrings,
            objective_qubits=list(range(self.n_value_qubits)),
        )
        grover = Grover(sampler=StatevectorSampler())
        return grover, problem

    @staticmethod
    def _extract_counts(result_item) -> Dict[str, int]:
        data = result_item.data
        for field in ("meas", "c", "cr"):
            if hasattr(data, field):
                return getattr(data, field).get_counts()
        for key in data.keys():
            value = data[key]
            if hasattr(value, "get_counts"):
                return value.get_counts()
        raise RuntimeError("Unable to extract counts from sampler result")

    def solve(self, approach: str = "manual", shots: int = 1024) -> Dict:
        if approach == "high_level":
            grover, problem = self.build_grover_high_level()
            result = grover.amplify(problem)
            top = result.top_measurement
            grid = self.decoder.decode_bitstring(top)
            is_valid, _ = self.decoder.verify_solution(grid)
            return {
                "circuit": None,
                "counts": {top: 1},
                "top_measurement": top,
                "decoded_solution": grid,
                "is_valid": is_valid,
                "n_iterations": result.iterations,
                "success_probability": 1.0 if is_valid else 0.0,
                "all_solutions": [
                    {
                        "bitstring": top,
                        "count": 1,
                        "probability": 1.0,
                        "grid": grid,
                        "is_valid": is_valid,
                    }
                ],
            }

        n_iterations = self.compute_optimal_iterations()
        qc = self.build_full_circuit(n_iterations=n_iterations)
        sampler = StatevectorSampler()
        job = sampler.run([qc], shots=shots)
        result = job.result()
        counts = self._extract_counts(result[0])
        decoded = self.decoder.decode_counts(counts)
        top = decoded[0]

        return {
            "circuit": qc,
            "counts": counts,
            "top_measurement": top["bitstring"],
            "decoded_solution": top["grid"],
            "is_valid": top["is_valid"],
            "n_iterations": n_iterations,
            "success_probability": top["probability"],
            "all_solutions": decoded,
        }

    def solve_with_visualization(self, shots: int = 1024) -> Dict:
        n_iterations = self.compute_optimal_iterations()
        oracle = self.oracle_builder.build_oracle()
        diffuser = build_diffuser(self.n_value_qubits)

        snapshots: List[Statevector] = []
        evolving = QuantumCircuit(self.n_value_qubits)
        if self.n_value_qubits > 0:
            evolving.h(range(self.n_value_qubits))
        snapshots.append(Statevector.from_instruction(evolving))
        for _ in range(n_iterations):
            evolving.compose(oracle, inplace=True)
            evolving.compose(diffuser, inplace=True)
            snapshots.append(Statevector.from_instruction(evolving))

        result = self.solve(approach="manual", shots=shots)
        result["statevectors"] = snapshots
        return result

    def run_multiple_trials(self, n_trials: int = 100, shots: int = 1024) -> Dict:
        valids = 0
        top_probs = []
        for _ in range(n_trials):
            res = self.solve(shots=shots)
            if res["is_valid"]:
                valids += 1
            top_probs.append(res["success_probability"])
        return {
            "n_trials": n_trials,
            "success_rate": valids / n_trials,
            "avg_top_probability": sum(top_probs) / max(1, len(top_probs)),
        }

    def solve_iteratively(self) -> Dict:
        max_iters = max(1, self.compute_optimal_iterations() * 3)
        for k in range(1, max_iters + 1):
            qc = self.build_full_circuit(n_iterations=k)
            sampler = StatevectorSampler()
            result = sampler.run([qc], shots=1024).result()
            counts = self._extract_counts(result[0])
            decoded = self.decoder.decode_counts(counts)
            if decoded and decoded[0]["is_valid"]:
                return {
                    "n_iterations": k,
                    "counts": counts,
                    "top_measurement": decoded[0]["bitstring"],
                    "decoded_solution": decoded[0]["grid"],
                    "is_valid": True,
                }
        return {"n_iterations": max_iters, "is_valid": False}
