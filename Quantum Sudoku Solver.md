# 🥈 Quantum Sudoku Solver with Grover's Algorithm — Complete PRD, TRD & Implementation Plan

---

## 📋 PART 1: PRODUCT REQUIREMENTS DOCUMENT (PRD)

### 1.1 Product Vision

Build a **visually explainable Quantum Sudoku Solver** that models Sudoku puzzles as constraint satisfaction problems (CSP), encodes the constraints into a Grover oracle, and uses Grover's amplitude amplification to find valid solutions — all implemented in Qiskit with rich step-by-step visualizations of the quantum search process.

### 1.2 Problem Statement

Sudoku is a popular puzzle where one must arrange numbers such that no row, column, or block contains a number more than once. Classical brute-force approaches suffer from exponential complexity. On a quantum computer, this type of problem can be solved in O(√N) times by the general ideas of Grover's algorithm.

**Critical Constraint:** Since current quantum computers are very limited machines, we cannot solve a real 9x9 sudoku puzzle; our toy examples use a 2x2 matrix where a valid solution is when in every row and every column there are no repeated values (0 or 1). Therefore, this project targets **2×2** and **4×4** Sudoku variants as progressively complex tiers, while the architecture is designed to be generalizable.

### 1.3 Why Grover's Algorithm?

Grover's algorithm can speed up an unstructured search problem quadratically, but its uses extend beyond that; it can serve as a general trick or subroutine to obtain quadratic run time improvements for a variety of other algorithms.

The Grover's algorithm consists of four parts. The state preparation initializes qubit values. The oracle multiplies by -1 the amplitude of the state that corresponds to the correct solution. The amplitude amplification state increases the amplitude of the correct solution. The oracle and amplitude amplification part is repeated √N times. Then, the measurement operation measures states of the value qubits to the classical register. With some probability, the measured solution is the correct solution to the problem.

### 1.4 Target Users
- Quantum computing educators & students seeking tangible CSP examples
- Developers learning Grover's algorithm through interactive visualization
- Portfolio builders showcasing constraint satisfaction on quantum hardware
- Researchers exploring quantum approaches to NP-complete problems

### 1.5 Success Criteria

| Metric | Target |
|--------|--------|
| 2×2 Sudoku (4 unknowns, 4 qubits) | Solves correctly 100% of the time on simulator |
| 2×2 Sudoku (partial clues, 1–3 unknowns) | Solves correctly 100% of the time |
| 4×4 Sudoku (reduced, 2–4 unknowns) | Solves correctly ≥ 95% across 100 runs |
| Visualization quality | Step-by-step Bloch/histogram for every Grover iteration |
| Classical comparison | Demonstrably shows √N query advantage |
| End-to-end runtime | < 60 seconds on laptop for all supported sizes |

### 1.6 Feature Requirements

| ID | Feature | Priority | Description |
|----|---------|----------|-------------|
| F1 | Sudoku Puzzle Engine | P0 | Parse, validate, generate 2×2 and 4×4 Sudoku puzzles |
| F2 | Constraint-to-Oracle Compiler | P0 | Translate Sudoku constraints into a Grover phase-flip oracle circuit |
| F3 | Grover Solver Core | P0 | Full Grover search: state prep → oracle → diffuser → measurement |
| F4 | Step-by-Step Visualizer | P0 | Animate/display each Grover iteration: amplitudes, histograms, circuit |
| F5 | Solution Decoder | P0 | Decode measured bitstrings back into Sudoku grid solutions |
| F6 | Classical Brute-Force Baseline | P1 | Compare query count: classical O(N) vs quantum O(√N) |
| F7 | Interactive Puzzle Builder | P1 | Jupyter widget or CLI to input custom puzzles |
| F8 | Oracle Complexity Analyzer | P1 | Count gates, depth, ancilla qubits for each puzzle oracle |
| F9 | Noise Simulation | P2 | Run on Aer noisy simulator, analyze effect on solution quality |
| F10 | Real Hardware Execution | P2 | Execute small puzzles on IBM Quantum hardware |
| F11 | Scalability Analysis | P2 | Theoretical analysis of qubit requirements for 9×9 Sudoku |

### 1.7 Non-Functional Requirements

| Requirement | Specification |
|-------------|---------------|
| Python version | ≥ 3.10 |
| Qiskit compatibility | Qiskit ≥ 2.0 (preferably 2.1+ for `PhaseOracleGate`) + `qiskit-algorithms` |
| Execution | Local `StatevectorSampler` + optional IBM Quantum backend |
| Visualization | Matplotlib, ipywidgets, Qiskit `.draw()` |
| Reproducibility | Fixed random seeds, deterministic simulator for testing |
| Documentation | Full theory section + annotated Jupyter notebooks |

---

## 🔧 PART 2: TECHNICAL REQUIREMENTS DOCUMENT (TRD)

### 2.1 System Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                   QUANTUM SUDOKU SOLVER — GROVER'S ALGORITHM            │
├──────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────┐    ┌──────────────────┐    ┌───────────────────────┐  │
│  │ PUZZLE LAYER │───▶│ ORACLE COMPILER  │───▶│ GROVER ENGINE         │  │
│  │              │    │                  │    │                       │  │
│  │ • Parse grid │    │ • Binary encode  │    │ ┌───────────────────┐ │  │
│  │ • Validate   │    │ • XOR equality   │    │ │ 1. State Prep     │ │  │
│  │ • Find empty │    │   checks         │    │ │    H⊗n on value   │ │  │
│  │ • Generate   │    │ • Multi-ctrl AND │    │ │    qubits         │ │  │
│  │   puzzles    │    │ • Phase kickback │    │ ├───────────────────┤ │  │
│  │ • Known val  │    │ • Ancilla mgmt   │    │ │ 2. Oracle Sf      │ │  │
│  │   encoding   │    │                  │    │ │    (phase-flip    │ │  │
│  └──────────────┘    └──────────────────┘    │ │     solutions)    │ │  │
│                                              │ ├───────────────────┤ │  │
│  ┌──────────────┐    ┌──────────────────┐    │ │ 3. Diffuser D     │ │  │
│  │ VISUALIZER   │◀───│ SOLUTION DECODER │◀───│ │    H⊗n·S₀·H⊗n    │ │  │
│  │              │    │                  │    │ ├───────────────────┤ │  │
│  │ • Grid render│    │ • Bitstring→grid │    │ │ 4. Repeat √N      │ │  │
│  │ • Amplitude  │    │ • Verify rules   │    │ │    times          │ │  │
│  │   bar charts │    │ • Rank solutions │    │ ├───────────────────┤ │  │
│  │ • Circuit    │    │ • Multi-solution │    │ │ 5. Measure        │ │  │
│  │   diagrams   │    │   handling       │    │ └───────────────────┘ │  │
│  │ • Iteration  │    │                  │    │                       │  │
│  │   animation  │    │                  │    │                       │  │
│  └──────────────┘    └──────────────────┘    └───────────────────────┘  │
│                                                                          │
│  ┌──────────────┐    ┌──────────────────┐                               │
│  │ CLASSICAL    │    │ ANALYSIS &       │                               │
│  │ BASELINE     │    │ BENCHMARKING     │                               │
│  │              │    │                  │                               │
│  │ • Backtrack  │    │ • Gate counts    │                               │
│  │ • Brute force│    │ • Query counts   │                               │
│  │ • CSP solver │    │ • Qubit scaling  │                               │
│  └──────────────┘    └──────────────────┘                               │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack & Dependencies

```
# requirements.txt
python>=3.10
qiskit>=2.0
qiskit-algorithms>=0.4.0
qiskit-aer>=0.15.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
ipywidgets>=8.0.0
pandas>=2.0.0
pyyaml>=6.0.0
tqdm>=4.65.0
pytest>=7.4.0
```

**Key API Choices (Qiskit 2.x):**

We strongly recommend to run this tutorial using Qiskit 2.0 or newer. Though the use of PhaseOracle is possible in Qiskit < 2.0, it requires the tweedledum library, which has been deprecated for a long time and isn't compatible with the most recent versions of Python. This tutorial instead uses the more recent PhaseOracleGate that has been introduced in Qiskit 2.1.

**Two approaches to Grover oracles in this project:**

1. **High-level (PhaseOracleGate + Boolean expressions):** For simpler puzzles, encode Sudoku constraints as Boolean expression strings and let Qiskit synthesize the oracle.

2. **Low-level (Manual circuit construction):** Build the oracle gate-by-gate with explicit XOR comparators, multi-controlled Z gates, and ancilla management — this is the primary approach for deeper technical understanding and visualization.

The class `GroverOperator` is deprecated as of Qiskit 2.1. It will be removed in Qiskit 3.0. Use `qiskit.circuit.library.grover_operator` instead.

### 2.3 Sudoku-to-Quantum Encoding Theory

#### 2.3.1 Binary Encoding of Cell Values

A first step to solving a Sudoku is to convert the numbers into binary so a series of 0 and 1 can represent an easy-to-read solution.

**Tier 1 — 2×2 Sudoku (values 0 and 1):**
```
Grid:        Binary:       Qubits:
┌───┬───┐    ┌───┬───┐
│v₀ │v₁ │    │ 0 │ 1 │    v₀=q₀, v₁=q₁, v₂=q₂, v₃=q₃
├───┼───┤    ├───┼───┤    
│v₂ │v₃ │    │ 1 │ 0 │    4 value qubits total
└───┴───┘    └───┴───┘    1 bit per cell (values: 0 or 1)
```

**Tier 2 — 4×4 Sudoku (values 0–3):**
```
Grid (partial):   Binary per cell:     Qubits per empty cell:
┌───┬───┬───┬───┐  value 0 = 00        2 qubits per unknown cell
│ _ │ 1 │ _ │ 3 │  value 1 = 01        e.g., 4 unknowns × 2 bits = 8 value qubits
├───┼───┼───┼───┤  value 2 = 10        + ancilla qubits for constraint checks
│ 2 │ _ │ 0 │ _ │  value 3 = 11
├───┼───┼───┼───┤
│ _ │ 0 │ _ │ 2 │
├───┼───┼───┼───┤
│ 3 │ _ │ 1 │ _ │
└───┴───┴───┴───┘
```

#### 2.3.2 Qubit Budget

| Puzzle | Value Qubits | Ancilla Qubits (constraints) | Total Qubits | Search Space |
|--------|-------------|------------------------------|--------------|-------------|
| 2×2, 4 unknowns | 4 | 4–6 | 8–10 | 2⁴ = 16 |
| 2×2, 2 unknowns | 2 | 2–4 | 4–6 | 2² = 4 |
| 4×4, 2 unknowns | 4 | 4–6 | 8–10 | 2⁴ = 16 |
| 4×4, 4 unknowns | 8 | 8–16 | 16–24 | 2⁸ = 256 |
| 4×4, 8 unknowns | 16 | 16–32 | 32–48 | 2¹⁶ = 65536 |
| 9×9 (theoretical) | ~162 | ~500+ | ~700+ | Intractable for simulation |

#### 2.3.3 Constraint Encoding as Oracle

For a 2×2 Sudoku, the constraints are:
- **Row 0:** v₀ ≠ v₁ → XOR(v₀, v₁) = 1
- **Row 1:** v₂ ≠ v₃ → XOR(v₂, v₃) = 1
- **Col 0:** v₀ ≠ v₂ → XOR(v₀, v₂) = 1
- **Col 1:** v₁ ≠ v₃ → XOR(v₁, v₃) = 1

All four XOR constraints must be satisfied simultaneously → AND them together.

We encode these XOR-ing the values for each row and column.

**Oracle Logic (2×2, all unknowns):**
```
constraint_satisfied = XOR(v₀,v₁) AND XOR(v₂,v₃) AND XOR(v₀,v₂) AND XOR(v₁,v₃)
```

If a given cell has a **known (clue) value**, we fix that qubit classically (don't put it in superposition) and adjust the constraint circuit accordingly.

### 2.4 Project File Structure

```
quantum-sudoku-solver/
├── README.md
├── requirements.txt
├── setup.py
├── .env.example                      # IBM Quantum token (optional)
├── config/
│   └── config.yaml                   # Puzzle library + parameters
├── puzzles/
│   ├── 2x2/                          # Pre-defined 2×2 puzzles (JSON)
│   │   ├── puzzle_001_all_unknown.json
│   │   ├── puzzle_002_one_clue.json
│   │   └── puzzle_003_two_clues.json
│   └── 4x4/                          # Pre-defined 4×4 puzzles (JSON)
│       ├── puzzle_001_easy.json
│       ├── puzzle_002_medium.json
│       └── puzzle_003_hard.json
├── src/
│   ├── __init__.py
│   ├── puzzle_engine.py              # Module 1: Sudoku grid management
│   ├── binary_encoder.py             # Module 2: Grid → binary qubit mapping
│   ├── constraint_oracle.py          # Module 3: Constraint → oracle circuit
│   ├── diffuser.py                   # Module 4: Grover diffusion operator
│   ├── grover_solver.py              # Module 5: Full Grover pipeline
│   ├── solution_decoder.py           # Module 6: Bitstring → grid solution
│   ├── visualizer.py                 # Module 7: All visualizations
│   ├── classical_solver.py           # Module 8: Classical baselines
│   ├── complexity_analyzer.py        # Module 9: Gate/qubit analysis
│   └── utils.py                      # Shared helpers
├── notebooks/
│   ├── 01_sudoku_basics_and_encoding.ipynb
│   ├── 02_oracle_construction_deep_dive.ipynb
│   ├── 03_grover_step_by_step.ipynb
│   ├── 04_solving_2x2_sudoku.ipynb
│   ├── 05_solving_4x4_sudoku.ipynb
│   ├── 06_visualization_showcase.ipynb
│   └── 07_scalability_analysis.ipynb
├── tests/
│   ├── test_puzzle_engine.py
│   ├── test_binary_encoder.py
│   ├── test_constraint_oracle.py
│   ├── test_grover_solver.py
│   └── test_solution_decoder.py
└── results/
    ├── figures/
    ├── circuits/
    └── benchmarks/
```

### 2.5 Module Specifications

---

#### **MODULE 1: `puzzle_engine.py` — Sudoku Grid Management**

```python
"""
puzzle_engine.py — Sudoku puzzle parsing, generation, and validation

Classes:
    SudokuPuzzle

Data Format (JSON):
    {
        "size": 2,              # 2 = 2×2 grid, 4 = 4×4 grid
        "block_size": 1,        # 1 for 2×2 (no sub-blocks), 2 for 4×4
        "grid": [[null,null],[null,null]],  # null = unknown
        "solution": [[1,0],[0,1]],          # optional: known answer
        "difficulty": "easy"
    }

Methods:
    __init__(self, size: int = 2, grid: Optional[List[List]] = None)
        - size: 2 or 4 (grid dimension)
        - grid: 2D list with None for unknowns, int for clues
        - Validate: all clue values in valid range [0, size-1]
    
    @classmethod
    from_json(cls, filepath: str) -> 'SudokuPuzzle'
        - Load puzzle from JSON file
    
    @classmethod
    from_string(cls, puzzle_str: str) -> 'SudokuPuzzle'
        - Parse from string like "_ 1 | 0 _" for quick CLI input
    
    get_empty_cells(self) -> List[Tuple[int, int]]
        - Return list of (row, col) positions of unknown cells
        - Ordered row-major for consistent qubit mapping
    
    get_clue_cells(self) -> Dict[Tuple[int, int], int]
        - Return {(row, col): value} for all known cells
    
    get_constraints(self) -> List[Tuple[Tuple[int,int], Tuple[int,int]]]
        - Return list of (cell_a, cell_b) pairs that must differ
        - Includes: all row pairs + all column pairs + all block pairs
        - For 2×2 with no sub-blocks: just rows + columns
        - For 4×4 with 2×2 sub-blocks: rows + columns + blocks
    
    get_constraint_pairs_for_unknowns(self) -> List[Tuple]
        - Filter constraints to only those involving ≥1 unknown cell
        - Each entry: (cell_a, cell_b, val_a_known, val_b_known)
        - If both unknown: (cell_a, cell_b, None, None)
        - If one known: (cell_a, cell_b, known_val, None) 
    
    validate_solution(self, solution_grid: List[List[int]]) -> bool
        - Check all constraints are satisfied
        - Return True if valid complete solution
    
    display(self, highlight_unknowns: bool = True) -> str
        - Pretty-print the grid with borders
        - Highlight unknown cells with color/underscore
    
    generate_random(self, size: int, n_clues: int) -> 'SudokuPuzzle'
        - Generate a random valid puzzle with given number of clues
        - Ensure unique solution exists
    
    get_num_unknowns(self) -> int
        - Return count of empty cells
    
    get_value_range(self) -> int
        - Return number of possible values per cell (= size)
    
    get_bits_per_cell(self) -> int
        - Return ceil(log2(size))
        - 2×2: 1 bit, 4×4: 2 bits, 9×9: 4 bits (values 1-9 need 4 bits)
"""
```

**Puzzle Library:**

```yaml
# config/config.yaml
puzzles:
  tier1_2x2:
    - name: "2x2_all_unknown"
      size: 2
      grid: [[null,null],[null,null]]
      solutions: 2    # Two valid solutions
      
    - name: "2x2_one_clue_v0"
      size: 2
      grid: [[1,null],[null,null]]
      solutions: 1    # Unique solution
      
    - name: "2x2_two_clues"
      size: 2
      grid: [[1,null],[null,0]]
      solutions: 1
      
    - name: "2x2_three_clues"
      size: 2
      grid: [[1,0],[null,1]]
      solutions: 1

  tier2_4x4:
    - name: "4x4_two_unknowns"
      size: 4
      grid: [[0,1,2,3],[2,3,null,1],[1,null,3,2],[3,2,1,0]]
      solutions: 1
      
    - name: "4x4_four_unknowns"
      size: 4
      grid: [[null,1,2,null],[2,null,0,1],[1,0,null,2],[3,2,1,0]]
      solutions: 1

grover:
  max_iterations: null       # null = compute optimal, or set manually
  shots: 1024                # Measurement shots
  simulator: 'statevector'   # 'statevector' or 'aer' or 'ibm_hardware'
  
visualization:
  show_intermediate_states: true
  animation_delay_ms: 500
  color_scheme: 'viridis'
```

---

#### **MODULE 2: `binary_encoder.py` — Grid-to-Qubit Mapping**

```python
"""
binary_encoder.py — Map Sudoku cells to qubit registers

Classes:
    SudokuEncoder

PURPOSE:
    - Assign qubit indices to each unknown cell
    - Track which qubits represent which cell
    - Handle known-value constraints by NOT putting those cells in superposition

Methods:
    __init__(self, puzzle: SudokuPuzzle)
        - Analyze puzzle dimensions and unknowns
        - Compute bits_per_cell = ceil(log2(puzzle.size))
    
    encode(self) -> Dict
        - Build complete qubit allocation map
        - Returns {
            'n_value_qubits': int,        # qubits in superposition
            'n_ancilla_qubits': int,       # workspace qubits for oracle
            'n_output_qubit': 1,           # single oracle output qubit
            'total_qubits': int,
            'cell_to_qubits': {            # mapping cells to qubit indices
                (row, col): [qubit_idx, ...],  # list of qubit indices
                ...
            },
            'qubit_to_cell': {             # reverse mapping
                qubit_idx: (row, col, bit_position),
                ...
            },
            'clue_values': {               # known values (not superposed)
                (row, col): int,
                ...
            },
            'constraint_pairs': [          # pairs needing oracle checks
                {
                    'cell_a': (row, col),
                    'cell_b': (row, col),
                    'qubits_a': [idx, ...],  # or None if known
                    'qubits_b': [idx, ...],  # or None if known
                    'known_val_a': int or None,
                    'known_val_b': int or None,
                    'ancilla_qubit': int      # ancilla for this constraint
                },
                ...
            ]
          }
    
    get_state_preparation_circuit(self) -> QuantumCircuit
        - Build circuit that puts all value qubits in superposition
        - H gate on each value qubit
        - Known cells: encode fixed values using X gates (NOT superposition)
        - Returns QuantumCircuit
    
    decode_bitstring(self, bitstring: str) -> List[List[int]]
        - Convert measurement bitstring back to grid values
        - Use cell_to_qubits mapping in reverse
        - Handle Qiskit's reversed bit ordering!
        - Returns 2D grid of integers
    
    get_valid_bitstrings(self) -> List[str]
        - Classical brute force: enumerate all valid solutions
        - Used for oracle verification & testing
        - Returns list of bitstrings that satisfy all constraints
    
    print_mapping(self) -> str
        - Pretty-print the qubit assignment table
"""
```

**Encoding Example — 2×2 Sudoku, all unknowns:**

```
Grid:          Qubit Map:
┌────┬────┐    v₀ = q₀ (1 bit, values {0,1})
│ v₀ │ v₁ │    v₁ = q₁
├────┼────┤    v₂ = q₂
│ v₂ │ v₃ │    v₃ = q₃
└────┴────┘    
               + ancilla qubits: q₄, q₅, q₆, q₇ (one per constraint)
               + output qubit: q₈
               Total: 9 qubits

State Preparation: H on q₀, q₁, q₂, q₃
Search Space: 2⁴ = 16 states
```

**Encoding Example — 2×2 Sudoku, v₀=1 known:**

```
Grid:          Qubit Map:
┌────┬────┐    v₀ = FIXED to 1 (no qubit needed, encoded classically)
│  1 │ v₁ │    v₁ = q₀
├────┼────┤    v₂ = q₁
│ v₂ │ v₃ │    v₃ = q₂
└────┴────┘    
               + ancilla: q₃, q₄, q₅, q₆
               + output: q₇
               Total: 8 qubits

State Preparation: H on q₀, q₁, q₂
Search Space: 2³ = 8 states
Constraints involving v₀: use known value 1 directly in oracle logic
```

---

#### **MODULE 3: `constraint_oracle.py` — Sudoku Constraint Oracle** ⭐ CORE

```python
"""
constraint_oracle.py — Build the Grover phase-flip oracle for Sudoku constraints

THEORY:
    The oracle must flip the phase of states that satisfy ALL Sudoku constraints.
    For 2×2 (1-bit values): "not equal" = XOR gate (CNOT)
    For 4×4 (2-bit values): "not equal" requires comparing 2-bit registers

    The oracle is a PHASE oracle (not bit-flip):
    |x⟩ → (-1)^f(x) |x⟩   where f(x) = 1 if x satisfies all constraints

Classes:
    SudokuOracle

Methods:
    __init__(self, encoder: SudokuEncoder)
        - Store the encoding mapping
        - Pre-compute constraint pair information
    
    build_oracle(self) -> QuantumCircuit
        - HIGH-LEVEL FLOW:
          1. For each constraint pair (cell_a, cell_b):
             - Compute XOR(cell_a, cell_b) → store in ancilla
             - For 1-bit: single CNOT
             - For 2-bit: bitwise XOR then OR the results
          2. Multi-controlled Z gate on all ancilla qubits
             - This flips the phase ONLY if ALL ancillas are |1⟩
             - i.e., all constraints are satisfied
          3. UNCOMPUTE all ancilla operations (reverse step 1)
             - Critical! Oracle must leave ancillas clean
        - Returns QuantumCircuit implementing phase-flip oracle
    
    _build_xor_check_1bit(self, qc: QuantumCircuit, 
                           qubit_a: int, qubit_b: int,
                           ancilla: int) -> None
        - CASE: Both cells are unknown (1-bit each)
        - Implements: ancilla = XOR(qubit_a, qubit_b)
        - Circuit: CNOT(qubit_a, ancilla); CNOT(qubit_b, ancilla)
        - After: ancilla = |1⟩ iff qubit_a ≠ qubit_b
    
    _build_xor_check_1bit_with_known(self, qc: QuantumCircuit,
                                       qubit_unknown: int,
                                       known_value: int,
                                       ancilla: int) -> None
        - CASE: One cell is known, one is unknown (1-bit)
        - If known_value = 0: ancilla should be |1⟩ when unknown = 1
          → Just CNOT(qubit_unknown, ancilla)
        - If known_value = 1: ancilla should be |1⟩ when unknown = 0
          → X(qubit_unknown); CNOT(qubit_unknown, ancilla); X(qubit_unknown)
          OR: CNOT(qubit_unknown, ancilla); X(ancilla)
    
    _build_xor_check_2bit(self, qc: QuantumCircuit,
                           qubits_a: List[int], qubits_b: List[int],
                           ancilla: int, extra_ancillas: List[int]) -> None
        - CASE: Both cells are unknown (2-bit each, for 4×4 Sudoku)
        - Implements: ancilla = |1⟩ iff qubits_a ≠ qubits_b
        - Strategy: Check bit-by-bit XOR, then ensure at least one differs
        - Circuit:
          1. XOR high bits → extra_ancilla[0]
          2. XOR low bits → extra_ancilla[1]  
          3. OR(extra_ancilla[0], extra_ancilla[1]) → ancilla
          4. OR can be done as: X both; Toffoli(both, ancilla); X both; X ancilla
    
    _build_multicontrolled_z(self, qc: QuantumCircuit,
                              ancilla_qubits: List[int]) -> None
        - Apply multi-controlled Z on all ancilla qubits
        - Flips phase iff ALL ancillas are |1⟩
        - Implementation options:
          a) MCMTGate(ZGate(), n_controls, 1) — Qiskit built-in
          b) Manual: X on target, multi-controlled X, X on target
          c) For small counts: decompose into Toffoli chains
    
    _uncompute_ancillas(self, qc: QuantumCircuit) -> None
        - Reverse all ancilla computation gates
        - Ensures oracle is its own inverse on ancilla qubits
    
    build_oracle_boolean_expr(self) -> QuantumCircuit
        - ALTERNATIVE: Use PhaseOracleGate with Boolean expression
        - Convert Sudoku constraints to Boolean string:
          For 2×2: "(v0 ^ v1) & (v2 ^ v3) & (v0 ^ v2) & (v1 ^ v3)"
        - Build: PhaseOracleGate(BooleanExpression(expr_string))
        - Returns QuantumCircuit
    
    verify_oracle(self, oracle_circuit: QuantumCircuit) -> Dict
        - Classically verify oracle correctness
        - For each possible input state, simulate and check phase
        - Returns {bitstring: phase_flip_occurred}
        - Confirm: only valid solutions get phase-flipped
    
    get_oracle_stats(self) -> Dict
        - Return gate count, depth, ancilla count, etc.
"""
```

**Oracle Circuit Diagram — 2×2, All Unknowns:**

```
Value Qubits:    Ancilla Qubits:       Output:
                 (constraint checks)

q₀ (v₀): ─●────●───────────────────────────────●────●──────
           │    │                                │    │
q₁ (v₁): ─●────│────●──────────────────────●────│────●──────
           │    │    │                      │    │    │
q₂ (v₂): ─│────●────│────●─────────────●───│────●────│──────
           │    │    │    │             │   │    │    │
q₃ (v₃): ─│────│────●────●─────────●──│───│────│────●──────
           │    │    │    │         │  │   │    │    │
q₄ (a₀): ─⊕────│────│────│───      │  │  ─⊕────│────│──────  ← XOR(v₀,v₁)
                │    │    │   │     │  │        │    │
q₅ (a₁): ──────⊕────│────│───│─    │  │  ──────⊕────│──────  ← XOR(v₀,v₂)
                     │    │   │ │   │  │             │
q₆ (a₂): ───────────⊕────│───│─│─  │  │  ───────────⊕──────  ← XOR(v₁,v₃)
                          │   │ │ │ │  │             
q₇ (a₃): ────────────────⊕───│─│─│─│──│─────────────⊕──────  ← XOR(v₂,v₃)
                              │ │ │ │  │
                              MCZ gate  │  ← Phase flip iff all ancillas |1⟩
                     (multi-ctrl Z on   │
                      a₀,a₁,a₂,a₃)     │
                                        │
                              UNCOMPUTE ─┘  ← Reverse ancilla computation

                 ┌─────────────────┐
   Result:       │ COMPUTE ANCILLAS│ → MCZ → │ UNCOMPUTE │
                 └─────────────────┘         └───────────┘
```

---

#### **MODULE 4: `diffuser.py` — Grover Diffusion Operator**

```python
"""
diffuser.py — Grover diffusion operator (inversion about the mean)

THEORY:
    D = 2|s⟩⟨s| - I = H⊗n · (2|0⟩⟨0| - I) · H⊗n
    Where |s⟩ = H⊗n|0⟩ is the uniform superposition
    
    Implementation: H⊗n → X⊗n → MCZ → X⊗n → H⊗n

Functions:
    build_diffuser(n_qubits: int) -> QuantumCircuit
        - Build the standard Grover diffuser for n value qubits
        - Circuit:
          1. H on all value qubits
          2. X on all value qubits
          3. Multi-controlled Z (MCZ) on all value qubits
          4. X on all value qubits
          5. H on all value qubits
        - Returns QuantumCircuit acting on n_qubits
    
    build_diffuser_custom(n_qubits: int, 
                           state_prep: QuantumCircuit = None) -> QuantumCircuit
        - Generalized diffuser for amplitude amplification
        - If state_prep provided: reflects about that prepared state
        - Otherwise: standard uniform superposition reflection
    
    verify_diffuser(diffuser: QuantumCircuit) -> bool
        - Verify the diffuser is correct by checking matrix representation
        - Should have eigenvalues +1 and -1
"""
```

---

#### **MODULE 5: `grover_solver.py` — Full Grover Pipeline** ⭐ CORE

Qiskit implements Grover's algorithm in the Grover class. This class also includes the generalized version, Amplitude Amplification, and allows setting individual iterations and other meta-settings to Grover's algorithm.

```python
"""
grover_solver.py — Complete Grover's algorithm solver for Sudoku

THIS MODULE OFFERS TWO APPROACHES:
    Approach A: "From Scratch" — build oracle + diffuser manually, compose full circuit
    Approach B: "Qiskit High-Level" — use qiskit_algorithms.Grover + AmplificationProblem

Classes:
    QuantumSudokuSolver

Methods:
    __init__(self, puzzle: SudokuPuzzle, config: dict)
        - Initialize with puzzle and configuration
        - Build encoder, oracle, diffuser
        - Compute optimal number of Grover iterations
    
    compute_optimal_iterations(self) -> int
        - N = 2^n_value_qubits (search space size)
        - M = number of valid solutions
        - optimal_iters = floor(π/4 * √(N/M))
        - If M unknown, estimate or try iteratively
        - Returns optimal iteration count
    
    build_full_circuit(self, n_iterations: int = None) -> QuantumCircuit
        - APPROACH A: Manual Construction
        - 1. Create QuantumCircuit(total_qubits, n_classical_bits)
        - 2. State preparation: H on all value qubits
        - 3. For i in range(n_iterations):
               a. Apply oracle circuit
               b. Apply diffuser on value qubits
        - 4. Add measurement on value qubits only
        - Returns complete QuantumCircuit
    
    build_grover_high_level(self) -> Tuple[Grover, AmplificationProblem]
        - APPROACH B: Using qiskit_algorithms
        - Build oracle as QuantumCircuit
        - Create AmplificationProblem(oracle, is_good_state=valid_states)
        - Create Grover(sampler=StatevectorSampler())
        - Returns (grover_instance, problem_instance)
    
    solve(self, approach: str = 'manual', shots: int = 1024) -> Dict
        - Execute the solver
        - For 'manual':
            1. Build full circuit
            2. Run on StatevectorSampler or Aer with shots
            3. Collect measurement counts
        - For 'high_level':
            1. Call grover.amplify(problem)
            2. Get result.top_measurement
        - Decode top bitstring(s) into grid solution(s)
        - Validate each solution against Sudoku rules
        - Returns {
            'circuit': QuantumCircuit,
            'counts': dict,
            'top_measurement': str,
            'decoded_solution': List[List[int]],
            'is_valid': bool,
            'n_iterations': int,
            'success_probability': float,
            'all_solutions': List[Dict]  # ranked by count
          }
    
    solve_with_visualization(self, shots: int = 1024) -> Dict
        - Same as solve() but also records intermediate states
        - After each Grover iteration, snapshot the statevector
        - Returns results + list of intermediate Statevectors
    
    run_multiple_trials(self, n_trials: int = 100, 
                        shots: int = 1024) -> Dict
        - Run the solver multiple times
        - Compute success rate, average solution probability
        - Returns statistics dict
    
    solve_iteratively(self) -> Dict
        - When number of solutions is unknown
        - Try increasing iteration counts: 1, 2, 3, ...
        - Check if result is valid after each
        - Stop when valid solution found
"""
```

**Key API patterns for the two approaches:**

```python
# APPROACH A — Manual Circuit (preferred for visual explanation)
from qiskit import QuantumCircuit
from qiskit.primitives import StatevectorSampler

qc = QuantumCircuit(total_qubits, n_value_qubits)
# State prep
qc.h(value_qubit_indices)
# Grover iterations
for _ in range(optimal_iterations):
    qc.compose(oracle_circuit, inplace=True)
    qc.compose(diffuser_circuit, qubits=value_qubit_indices, inplace=True)
# Measure value qubits only
qc.measure(value_qubit_indices, range(n_value_qubits))

sampler = StatevectorSampler()
job = sampler.run([qc], shots=1024)
result = job.result()
counts = result[0].data.meas.get_counts()  # V2 primitive result access
```

```python
# APPROACH B — Qiskit Algorithms High-Level API
from qiskit_algorithms import Grover, AmplificationProblem
from qiskit.primitives import StatevectorSampler

problem = AmplificationProblem(
    oracle=oracle_circuit,
    is_good_state=valid_bitstrings,
    objective_qubits=value_qubit_indices
)
grover = Grover(sampler=StatevectorSampler())
result = grover.amplify(problem)
top = result.top_measurement
```

The returned result type is a GroverResult. If the search was successful, the oracle_evaluation attribute of the result will be True. In this case, the most sampled measurement, top_measurement, is one of the "good states".

---

#### **MODULE 6: `solution_decoder.py` — Bitstring-to-Grid Decoder**

```python
"""
solution_decoder.py — Convert measurement results back to Sudoku grids

Classes:
    SudokuDecoder

Methods:
    __init__(self, encoder: SudokuEncoder, puzzle: SudokuPuzzle)
        - Store encoding mapping and original puzzle
    
    decode_bitstring(self, bitstring: str) -> List[List[int]]
        - Convert a single bitstring to a complete grid
        - CRITICAL: Handle Qiskit's reversed qubit ordering
          Qiskit measures q₀ as RIGHTMOST bit in the string
        - Fill in known clue values + decoded unknown values
        - Returns 2D grid
    
    decode_counts(self, counts: Dict[str, int]) -> List[Dict]
        - Decode all measured bitstrings
        - For each: {
            'bitstring': str,
            'count': int,
            'probability': float,
            'grid': List[List[int]],
            'is_valid': bool
          }
        - Sort by count (descending)
        - Returns ranked list
    
    verify_solution(self, grid: List[List[int]]) -> Tuple[bool, List[str]]
        - Check all Sudoku constraints
        - Return (is_valid, list_of_violated_constraints)
    
    format_solution(self, grid: List[List[int]]) -> str
        - Pretty-print the solved grid
        - Highlight originally-unknown cells
"""
```

---

#### **MODULE 7: `visualizer.py` — Rich Visualization Engine** ⭐ KEY DIFFERENTIATOR

```python
"""
visualizer.py — Step-by-step quantum visualization for Sudoku solver

Classes:
    SudokuVisualizer

Methods:
    draw_puzzle(self, puzzle: SudokuPuzzle, 
                solution: Optional[List[List]] = None) -> Figure
        - Render Sudoku grid as colored matplotlib figure
        - Unknown cells in gray, clues in black, solutions in green/blue
    
    draw_circuit(self, circuit: QuantumCircuit, 
                  decompose_level: int = 1) -> Figure
        - Draw quantum circuit with custom styling
        - Annotate oracle and diffuser sections with labels
        - Color-code: state prep (blue), oracle (red), diffuser (green)
    
    draw_oracle_circuit(self, oracle: QuantumCircuit) -> Figure
        - Detailed view of just the oracle
        - Annotate each constraint check block
        - Show ancilla computation + MCZ + uncomputation
    
    plot_amplitude_evolution(self, statevectors: List[Statevector],
                              valid_states: List[str]) -> Figure
        - For each Grover iteration, plot bar chart of amplitudes
        - Highlight valid solution states in different color
        - Show amplitude growing with each iteration
        - X-axis: all basis states, Y-axis: amplitude
        - Multiple subplots: one per iteration
    
    plot_probability_evolution(self, statevectors: List[Statevector],
                                valid_states: List[str]) -> Figure
        - Same as above but plot |amplitude|² (probabilities)
        - Show total probability mass on solution states growing
    
    animate_grover(self, statevectors: List[Statevector],
                    valid_states: List[str],
                    save_path: str = None) -> FuncAnimation
        - Animated bar chart showing amplitudes evolving
        - Each frame = one Grover iteration
        - Optionally save as .gif or .mp4
    
    plot_measurement_histogram(self, counts: Dict[str, int],
                                valid_states: List[str]) -> Figure
        - Bar chart of measurement outcomes
        - Color valid solutions differently from invalid
        - Annotate top measurement with its decoded grid
    
    plot_grover_geometry(self, n_qubits: int, n_solutions: int,
                          n_iterations: int) -> Figure
        - 2D geometric visualization of Grover's algorithm
        - Show |s⟩, |w⟩, and the rotation by 2θ per iteration
        - Angle θ = arcsin(√(M/N))
        - Plot the state vector rotating toward |w⟩
    
    plot_success_probability_vs_iterations(self, n_qubits: int,
                                            n_solutions: int,
                                            max_iter: int = 20) -> Figure
        - Plot P(success) = sin²((2k+1)θ) for k iterations
        - Mark optimal iteration point
        - Show periodic nature (over-rotation)
    
    create_comparison_dashboard(self, quantum_results: Dict,
                                 classical_results: Dict) -> Figure
        - Side-by-side comparison
        - Query complexity: O(N) classical vs O(√N) quantum
        - Success rates, execution times
    
    plot_qubit_scaling(self, sizes: List[int]) -> Figure
        - Plot qubit requirements vs puzzle size
        - Show exponential growth
        - Mark "simulatable" vs "hardware-required" zones
"""
```

**Key Visualizations Produced:**

```
┌──────────────────────────────────────────────────────────────┐
│  VISUALIZATION 1: Amplitude Evolution                         │
│                                                                │
│  Iteration 0 (after H⊗n):                                    │
│  |00⟩ |01⟩ |10⟩ |11⟩  → all equal amplitudes (0.25 each)    │
│                                                                │
│  Iteration 1 (after Oracle + Diffuser):                       │
│  |00⟩ |01⟩ |10⟩ |11⟩  → solutions amplified, others shrunk  │
│  ████  ██   ██  ████                                          │
│  ^^^^              ^^^^  ← valid solutions highlighted        │
│                                                                │
│  VISUALIZATION 2: Geometric Rotation                          │
│                                                                │
│          |w⟩ (solution)                                       │
│           ↑                                                    │
│          /                                                     │
│         / 2θ rotation                                          │
│        /  per iteration                                        │
│       |s⟩ ────────→ |w⊥⟩ (non-solution)                      │
│                                                                │
│  VISUALIZATION 3: Sudoku Grid Solution                        │
│  ┌───┬───┐     ┌───┬───┐                                     │
│  │ ? │ ? │ →→→ │ 1 │ 0 │  ✅ All constraints satisfied       │
│  ├───┼───┤     ├───┼───┤                                     │
│  │ ? │ ? │     │ 0 │ 1 │                                     │
│  └───┴───┘     └───┴───┘                                     │
└──────────────────────────────────────────────────────────────┘
```

---

#### **MODULE 8: `classical_solver.py` — Classical Baselines**

```python
"""
classical_solver.py — Classical solvers for comparison

Functions:
    solve_bruteforce(puzzle: SudokuPuzzle) -> Dict
        - Enumerate ALL possible value assignments
        - Check each against constraints
        - Count total checks made (= query complexity)
        - Returns {'solutions': [...], 'n_queries': int, 'time': float}
    
    solve_backtracking(puzzle: SudokuPuzzle) -> Dict
        - Standard recursive backtracking
        - Count nodes explored
        - Returns {'solution': grid, 'n_nodes': int, 'time': float}
    
    solve_constraint_propagation(puzzle: SudokuPuzzle) -> Dict
        - Arc consistency + backtracking
        - Smarter but still classical
    
    compare_complexity(puzzle: SudokuPuzzle, 
                        quantum_queries: int) -> pd.DataFrame
        - Compare classical O(N) vs quantum O(√N) empirically
        - Create comparison table
"""
```

---

#### **MODULE 9: `complexity_analyzer.py` — Scalability Analysis**

```python
"""
complexity_analyzer.py — Analyze circuit complexity and scalability

Functions:
    analyze_circuit(circuit: QuantumCircuit) -> Dict
        - Gate count by type (CX, H, X, Z, Toffoli, etc.)
        - Circuit depth
        - Number of qubits
        - Number of classical bits
    
    estimate_qubits_for_size(size: int, n_unknowns: int) -> Dict
        - Estimate qubit requirements for given puzzle size
        - Value qubits: n_unknowns * ceil(log2(size))
        - Constraint ancillas: depends on number of constraint pairs
        - Returns detailed breakdown
    
    plot_scaling_analysis() -> Figure
        - Plot qubits needed vs puzzle size (2, 4, 9, 16, 25)
        - Show classical vs quantum resource comparison
    
    generate_complexity_report(puzzle: SudokuPuzzle,
                                circuit: QuantumCircuit) -> str
        - Comprehensive markdown report
"""
```

### 2.6 Algorithm Flow — Complete Pipeline

```
STEP 1: PUZZLE INPUT
════════════════════
User provides puzzle (JSON/string/widget):
┌───┬───┐
│ ? │ ? │    size=2, unknowns=[(0,0),(0,1),(1,0),(1,1)]
├───┼───┤    constraints=[(v₀≠v₁),(v₂≠v₃),(v₀≠v₂),(v₁≠v₃)]
│ ? │ ? │
└───┴───┘

STEP 2: BINARY ENCODING
═══════════════════════
v₀→q₀, v₁→q₁, v₂→q₂, v₃→q₃  (1 bit each, values {0,1})
Ancillas: q₄(c₀₁), q₅(c₂₃), q₆(c₀₂), q₇(c₁₃)
Search space: N = 2⁴ = 16

STEP 3: COMPUTE OPTIMAL ITERATIONS
══════════════════════════════════
# Two valid solutions exist for all-unknown 2×2:
# Solution A: [[1,0],[0,1]]  → bitstring 1001
# Solution B: [[0,1],[1,0]]  → bitstring 0110
M = 2 solutions, N = 16 states
θ = arcsin(√(M/N)) = arcsin(√(2/16)) = arcsin(0.354) ≈ 0.361 rad
Optimal iterations = floor(π/(4θ)) = floor(π/(4×0.361)) ≈ 2

STEP 4: BUILD QUANTUM CIRCUIT
═════════════════════════════
|0⟩⊗9  →  H⊗4 on value qubits
        →  [Oracle + Diffuser] × 2 iterations
        →  Measure q₀,q₁,q₂,q₃

STEP 5: EXECUTE
═══════════════
StatevectorSampler(shots=1024) → counts

STEP 6: DECODE
══════════════
Top bitstring: "1001" → v₀=1, v₁=0, v₂=0, v₃=1
Grid: [[1,0],[0,1]] → VALID ✅

STEP 7: VISUALIZE
════════════════
- Circuit diagram with annotated sections
- Amplitude bar charts per iteration
- Measurement histogram
- Solved grid display
- Geometric rotation diagram
```

---

## 📅 PART 3: IMPLEMENTATION PLAN

### Phase 0: Environment Setup (Day 1)

```bash
# Step 0.1: Create project structure
mkdir -p quantum-sudoku-solver/{config,puzzles/{2x2,4x4},src,notebooks,tests,results/{figures,circuits,benchmarks}}

# Step 0.2: Virtual environment
python -m venv .venv && source .venv/bin/activate

# Step 0.3: Install dependencies
pip install qiskit qiskit-algorithms qiskit-aer \
            numpy matplotlib seaborn ipywidgets \
            pandas pyyaml tqdm pytest

# Step 0.4: Verify critical imports
python -c "
from qiskit import QuantumCircuit
from qiskit.circuit.library import grover_operator, MCMTGate, ZGate
from qiskit.primitives import StatevectorSampler
from qiskit_algorithms import Grover, AmplificationProblem
print('All imports OK')
"

# Step 0.5: Verify PhaseOracleGate availability (Qiskit ≥ 2.1)
python -c "
from qiskit.circuit.library.phase_oracle import PhaseOracleGate
print('PhaseOracleGate available')
"

# Step 0.6: Create config/config.yaml with puzzle library
# Step 0.7: Create all puzzle JSON files in puzzles/ directory
```

### Phase 1: Puzzle Engine + Encoding (Day 1–2)

**Build order: `config.yaml` → `utils.py` → `puzzle_engine.py` → `binary_encoder.py`**

```
TASK 1.1: Create config/config.yaml
- Include all puzzle definitions from section 2.5 Module 1
- Include grover and visualization parameters

TASK 1.2: Create puzzle JSON files
- puzzles/2x2/puzzle_001_all_unknown.json through puzzle_003
- puzzles/4x4/puzzle_001_easy.json through puzzle_003
- Each must have: size, block_size, grid, solution, difficulty

TASK 1.3: Create src/utils.py
- load_config(path) → load YAML
- setup_logging() → Python logging
- set_random_seed(seed)
- timer decorator
- bits_needed(n) → ceil(log2(n))

TASK 1.4: Create src/puzzle_engine.py
- Implement SudokuPuzzle class per Module 1 spec
- KEY: get_constraints() must return ALL uniqueness pairs
  For 2×2: 4 pairs (2 rows × C(2,1) + 2 cols × C(2,1))
  For 4×4: 24 row pairs + 24 col pairs + 24 block pairs = 72 pairs total
  (But many are redundant; deduplicate)
- validate_solution: Check EVERY constraint pair
- display: Use Unicode box-drawing characters

TASK 1.5: Create src/binary_encoder.py
- Implement SudokuEncoder per Module 2 spec
- CRITICAL: Qubit ordering must be consistent throughout
  Convention: value qubits first (q₀..qₙ₋₁), then ancillas, then output
- CRITICAL: decode_bitstring must handle Qiskit's REVERSED bit ordering
  In Qiskit, a measured string "1001" means q₃=1, q₂=0, q₁=0, q₀=1
  So you must REVERSE the string before extracting qubit values!

TASK 1.6: Create tests/test_puzzle_engine.py
- Test loading from JSON
- Test constraint generation for 2×2 (should be 4 pairs)
- Test constraint generation for 4×4 (should be ≤72 unique pairs)
- Test validation accepts correct solutions, rejects wrong ones

TASK 1.7: Create tests/test_binary_encoder.py
- Test qubit allocation for 2×2 all unknown (4 value qubits)
- Test qubit allocation for 2×2 with 1 clue (3 value qubits)
- Test decode_bitstring round-trips correctly
- Test Qiskit bit ordering is handled
```

### Phase 2: Oracle Construction (Day 2–4) ⭐ HARDEST PART

**Build order: `constraint_oracle.py` → extensive testing → `diffuser.py`**

```
TASK 2.1: Create src/constraint_oracle.py — XOR building blocks
- Start with _build_xor_check_1bit():
    def _build_xor_check_1bit(qc, qubit_a, qubit_b, ancilla):
        # After these gates: ancilla = |1⟩ iff qubit_a ≠ qubit_b
        qc.cx(qubit_a, ancilla)  # ancilla ^= qubit_a
        qc.cx(qubit_b, ancilla)  # ancilla ^= qubit_b
        # Now ancilla = qubit_a XOR qubit_b
        # XOR=1 means "different" = constraint satisfied ✓

- Then _build_xor_check_1bit_with_known():
    # When one cell has known value:
    if known_value == 0:
        # constraint: unknown ≠ 0 → unknown must be 1
        qc.cx(qubit_unknown, ancilla)  # ancilla=1 iff unknown=1
    elif known_value == 1:
        # constraint: unknown ≠ 1 → unknown must be 0
        qc.cx(qubit_unknown, ancilla)
        qc.x(ancilla)  # flip: ancilla=1 iff unknown=0

TASK 2.2: Build the multi-controlled Z gate
- For 4 ancilla qubits (2×2 full puzzle):
    from qiskit.circuit.library import MCMTGate, ZGate
    # MCMTGate applies a target gate controlled on multiple qubits
    mcz = MCMTGate(ZGate(), num_ctrl_qubits=n_constraints, num_target_qubits=1)
    # OR manually:
    # Multi-controlled Z = H on target → Multi-controlled X → H on target
    # For small n: decompose using Toffoli chain

TASK 2.3: Build the complete oracle
- build_oracle():
    qc = QuantumCircuit(total_qubits)
    
    # STEP 1: Compute all constraint XORs into ancillas
    for constraint in constraints:
        if both_unknown:
            _build_xor_check_1bit(qc, q_a, q_b, ancilla_i)
        elif one_known:
            _build_xor_check_1bit_with_known(qc, q_unknown, known_val, ancilla_i)
    
    # STEP 2: Multi-controlled Z on all ancilla qubits
    # Phase flip iff ALL ancillas = |1⟩ (all constraints satisfied)
    _build_multicontrolled_z(qc, ancilla_list)
    
    # STEP 3: UNCOMPUTE ancillas (apply steps in reverse)
    # This is CRITICAL — oracle must restore ancillas to |0⟩
    for constraint in reversed(constraints):
        # Same gates as step 1 (they are self-inverse for CNOT+X)
        if both_unknown:
            _build_xor_check_1bit(qc, q_a, q_b, ancilla_i)
        elif one_known:
            _build_xor_check_1bit_with_known(qc, q_unknown, known_val, ancilla_i)
    
    return qc

TASK 2.4: Verify the oracle EXHAUSTIVELY
- verify_oracle():
    from qiskit.quantum_info import Statevector
    
    for bitstring in all_possible_bitstrings:
        # Prepare state |bitstring⟩
        init = QuantumCircuit(total_qubits)
        for i, bit in enumerate(bitstring):
            if bit == '1':
                init.x(i)
        
        # Apply oracle
        test_circuit = init.compose(oracle)
        
        # Get statevector
        sv = Statevector.from_instruction(test_circuit)
        
        # Check phase: valid solutions should have phase = -1
        # Invalid states should have phase = +1
        amplitude = sv[int(bitstring, 2)]
        phase_flipped = (amplitude.real < 0)
        
        # Verify against classical constraint check
        is_valid = classical_check(bitstring)
        assert phase_flipped == is_valid, f"Oracle error on {bitstring}"

TASK 2.5: Alternative oracle using PhaseOracleGate
- build_oracle_boolean_expr():
    For 2×2 all unknown:
        expression = "(v0 ^ v1) & (v2 ^ v3) & (v0 ^ v2) & (v1 ^ v3)"
        from qiskit.circuit.library.phase_oracle import PhaseOracleGate
        oracle = PhaseOracleGate(expression)
    
    NOTE: Variable names in expression map to qubits in alphabetical order
    So use names like 'a', 'b', 'c', 'd' and map them consistently

TASK 2.6: Create src/diffuser.py
- Implement build_diffuser(n_qubits):
    qc = QuantumCircuit(n_qubits, name='Diffuser')
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    # Multi-controlled Z
    qc.h(n_qubits - 1)
    qc.mcx(list(range(n_qubits - 1)), n_qubits - 1)  # Toffoli chain
    qc.h(n_qubits - 1)
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    return qc

TASK 2.7: Test oracle + diffuser
- tests/test_constraint_oracle.py:
    - 2×2 all unknown: verify exactly 2 states get phase-flipped
    - 2×2 one clue: verify exactly 1 state gets phase-flipped
    - Test uncomputation: ancillas return to |0⟩ after oracle
    - Test both manual oracle and PhaseOracleGate give same results
    - Compare gate counts between both approaches
```

### Phase 3: Grover Solver Core (Day 4–5) ⭐ INTEGRATION

```
TASK 3.1: Create src/grover_solver.py — Approach A (Manual)
- Implement QuantumSudokuSolver per Module 5 spec
- build_full_circuit():
    total_qubits = encoder.total_qubits
    n_value = encoder.n_value_qubits
    n_iter = compute_optimal_iterations()
    
    qc = QuantumCircuit(total_qubits, n_value)
    
    # State preparation: H on value qubits only
    qc.h(range(n_value))
    qc.barrier()
    
    # Grover iterations
    for i in range(n_iter):
        qc.compose(oracle, inplace=True)
        qc.barrier()
        qc.compose(diffuser, qubits=range(n_value), inplace=True)
        qc.barrier()
    
    # Measure value qubits
    qc.measure(range(n_value), range(n_value))
    
    return qc

TASK 3.2: Implement solve() with StatevectorSampler
    from qiskit.primitives import StatevectorSampler
    
    sampler = StatevectorSampler()
    pub = (circuit,)
    job = sampler.run([pub], shots=shots)
    result = job.result()
    
    # V2 Primitive result access:
    counts = result[0].data.meas.get_counts()
    # OR for Statevector access:
    # from qiskit.quantum_info import Statevector
    # sv = Statevector(circuit.remove_final_measurements(inplace=False))

TASK 3.3: Implement solve() — Approach B (Qiskit Algorithms)
    from qiskit_algorithms import Grover, AmplificationProblem
    from qiskit.primitives import StatevectorSampler
    
    valid_states = encoder.get_valid_bitstrings()
    
    problem = AmplificationProblem(
        oracle=oracle_circuit,
        is_good_state=valid_states,
        objective_qubits=list(range(n_value))
    )
    
    grover = Grover(sampler=StatevectorSampler())
    result = grover.amplify(problem)
    
    top = result.top_measurement
    success = result.oracle_evaluation

TASK 3.4: Implement solve_with_visualization()
    - After EACH Grover iteration, snapshot the statevector:
    
    from qiskit.quantum_info import Statevector
    
    statevectors = []
    qc_partial = QuantumCircuit(total_qubits)
    qc_partial.h(range(n_value))  # state prep
    
    # Snapshot after state prep
    sv = Statevector.from_instruction(qc_partial)
    statevectors.append(sv)
    
    for i in range(n_iterations):
        qc_partial.compose(oracle, inplace=True)
        qc_partial.compose(diffuser, qubits=range(n_value), inplace=True)
        sv = Statevector.from_instruction(qc_partial)
        statevectors.append(sv)
    
    return statevectors

TASK 3.5: Create src/solution_decoder.py
- decode_bitstring:
    IMPORTANT — Qiskit bit ordering:
    measured_string = "1001" means q₃=1, q₂=0, q₁=0, q₀=1
    Reverse: "1001" → read right-to-left → q₀=1, q₁=0, q₂=0, q₃=1
    
    reversed_bits = bitstring[::-1]
    for cell, qubit_indices in cell_to_qubits.items():
        bits = [reversed_bits[qi] for qi in qubit_indices]
        cell_value = int(''.join(bits), 2)
        grid[cell[0]][cell[1]] = cell_value

TASK 3.6: Create tests/test_grover_solver.py
- Test 2×2 all unknown: should find one of two valid solutions
- Test 2×2 one clue: should find unique solution
- Test 2×2 two clues: should find unique solution
- Test solution validity for all cases
- Test both approaches give same results
- Test optimal iteration count computation
- Run 100 trials and verify success rate > 95%
```

### Phase 4: Visualization Engine (Day 5–7) ⭐ DIFFERENTIATOR

```
TASK 4.1: Create src/visualizer.py
- Implement all methods per Module 7 spec

TASK 4.2: draw_puzzle()
    - Use matplotlib with Rectangle patches
    - Color scheme: gray for unknown, white for clues, green for solved
    - Draw grid lines with thick borders for sub-blocks
    - Large centered numbers in each cell

TASK 4.3: draw_circuit()
    - Use circuit.draw(output='mpl', style='iqp', fold=30)
    - Add section labels using barriers + annotations:
      "State Prep" | "Oracle (Iter 1)" | "Diffuser (Iter 1)" | ...
    - For large circuits: draw oracle and diffuser as named sub-circuits

TASK 4.4: plot_amplitude_evolution() — THE MONEY VISUAL
    import matplotlib.pyplot as plt
    import numpy as np
    
    fig, axes = plt.subplots(1, n_iterations + 1, figsize=(5*(n_iterations+1), 4))
    
    for i, sv in enumerate(statevectors):
        ax = axes[i]
        amplitudes = sv.data.real[:2**n_value]  # only value qubit subspace
        
        colors = ['green' if bs in valid_states else 'lightblue' 
                  for bs in all_bitstrings]
        
        ax.bar(range(len(amplitudes)), amplitudes, color=colors)
        ax.set_title(f'After Iteration {i}')
        ax.set_xlabel('State')
        ax.set_ylabel('Amplitude')
        ax.axhline(y=0, color='black', linewidth=0.5)
    
    plt.tight_layout()

TASK 4.5: plot_grover_geometry()
    - Draw 2D unit circle diagram
    - |w⟩ axis (solution subspace) vertical
    - |w⊥⟩ axis (non-solution subspace) horizontal
    - Show initial state |s⟩ at angle θ from |w⊥⟩
    - Draw rotation arrow for each iteration: 2θ per step
    - Mark state after each iteration
    - This is the iconic "Grover rotation" diagram

TASK 4.6: plot_success_probability_vs_iterations()
    - P(success) = sin²((2k+1)θ) where θ = arcsin(√(M/N))
    - Plot for k = 0, 1, 2, ..., max_iter
    - Mark the optimal k with a star
    - Show the periodic nature (probability oscillates!)
    - This demonstrates why we can't just add more iterations

TASK 4.7: plot_measurement_histogram()
    - Bar chart of counts
    - Color code: green for valid solutions, red for invalid
    - Annotate top result with mini Sudoku grid
    - Show theoretical expected probability as horizontal line

TASK 4.8: Create notebooks/06_visualization_showcase.ipynb
    - Run 2×2 puzzle with all visualizations
    - 8-panel figure: puzzle → encoding → circuit → 
      amplitude iter0 → amplitude iter1 → amplitude iter2 → 
      histogram → solved grid
```

### Phase 5: Classical Baselines (Day 7)

```
TASK 5.1: Create src/classical_solver.py
- Brute force: iterate all 2^n_value_qubits assignments, count checks
- Backtracking: recursive with constraint propagation
- Log the number of "oracle queries" (constraint checks) for fair comparison

TASK 5.2: Create src/complexity_analyzer.py
- Analyze oracle circuit: gate counts, depth
- Estimate qubit needs for larger puzzles
- Generate scaling table from 2×2 to 9×9
```

### Phase 6: Notebooks & Integration (Day 7–9)

```
TASK 6.1: Create notebooks/01_sudoku_basics_and_encoding.ipynb
- Explain Sudoku rules
- Show binary encoding of cell values
- Demonstrate qubit allocation for 2×2 and 4×4
- Print qubit mapping tables

TASK 6.2: Create notebooks/02_oracle_construction_deep_dive.ipynb
- Build XOR checker gate step by step
- Show truth table for each gate
- Build complete oracle incrementally
- Verify with statevector simulation
- Compare manual oracle vs PhaseOracleGate
- THIS IS THE MOST EDUCATIONAL NOTEBOOK

TASK 6.3: Create notebooks/03_grover_step_by_step.ipynb
- Explain Grover's algorithm theory
- Show the 4 components: state prep, oracle, diffuser, measurement
- Walk through a 2-qubit example (finding |11⟩)
- Demonstrate with amplitude bar charts at each step
- Explain optimal iteration count formula

TASK 6.4: Create notebooks/04_solving_2x2_sudoku.ipynb
- Solve 3 different 2×2 puzzles (all unknown, 1 clue, 2 clues)
- Full visualization for each
- Show that more clues → fewer qubits → faster solve
- Run 100 trials, plot success rate histogram

TASK 6.5: Create notebooks/05_solving_4x4_sudoku.ipynb
- Solve 4×4 puzzle with 2 unknowns (feasible on simulator)
- Show oracle complexity increase
- Discuss scalability limits
- Compare with classical solver timing

TASK 6.6: Create notebooks/07_scalability_analysis.ipynb
- Table: puzzle size vs qubits vs classical complexity
- Theoretical qubit estimates for 9×9 Sudoku
- Discussion: why quantum Sudoku is mostly educational today
- Comparison with other quantum CSP approaches (QAOA)
```

### Phase 7: Main Script + Polish (Day 9–10)

```
TASK 7.1: Create run_solver.py (main entry point)
"""
run_solver.py — Solve any puzzle from command line

Usage:
  python run_solver.py --puzzle puzzles/2x2/puzzle_001_all_unknown.json
  python run_solver.py --puzzle puzzles/4x4/puzzle_001_easy.json --approach manual
  python run_solver.py --size 2 --grid "_ _ | _ _" --visualize
"""

TASK 7.2: Create comprehensive README.md
- Project overview with sample output images
- Quick start (3 commands)
- Theory section: Grover's algorithm for CSP
- Architecture diagram
- Gallery of visualizations
- Scalability discussion
- References and acknowledgments

TASK 7.3: Final test suite
- Run ALL tests
- Verify every puzzle in the library solves correctly
- Verify all notebooks run without errors
- Performance test: all puzzles solve in < 60 seconds

TASK 7.4: Create run_demo.py
- Single script that solves all puzzle tiers and generates all figures
- Output: results/figures/ with numbered PNG files
- Output: results/benchmarks/comparison_table.csv
```

### Phase 8: Stretch Goals (Day 10+)

```
STRETCH 1: Interactive Jupyter Widget
- ipywidgets-based puzzle builder
- Click cells to set/clear values
- "Solve Quantum" button runs Grover
- Live circuit + histogram display

STRETCH 2: Noisy Simulation
- Run on AerSimulator with noise model
- Compare ideal vs noisy success rates
- Show how noise degrades solution quality
- Discuss error mitigation

STRETCH 3: Real IBM Quantum Hardware
- Run 2×2 puzzle on real hardware
- Use SamplerV2 with IBM Quantum backend
- Compare: simulator vs real hardware results
- Discuss decoherence effects

STRETCH 4: QAOA Comparison
- Solve same puzzles with QAOA
- Encode Sudoku constraints as QUBO
- Compare: Grover vs QAOA for CSP

STRETCH 5: Web App (Streamlit)
- Upload or select puzzle
- Configure qubits and iterations
- Run solver, display all visualizations
- Educational mode with step-by-step explanation
```

---

## 🔑 CRITICAL IMPLEMENTATION NOTES FOR THE AI COPILOT

### ⚠️ Common Pitfalls to Avoid

```python
# PITFALL 1: Qiskit bit ordering (THE #1 SOURCE OF BUGS)
# ❌ Assuming string "1001" means q₀=1, q₁=0, q₂=0, q₃=1
# ✅ In Qiskit, "1001" means q₃=1, q₂=0, q₁=0, q₀=1 (reversed!)
#    To get qubit values: reversed_string = bitstring[::-1]
#    Then reversed_string[i] gives the value of qubit i

# PITFALL 2: Forgetting to UNCOMPUTE ancillas in the oracle
# ❌ Compute constraint → MCZ → done (ancillas still entangled!)
# ✅ Compute constraint → MCZ → UNCOMPUTE constraint (ancillas back to |0⟩)
# If ancillas aren't cleaned up, the oracle won't work as a proper phase oracle

# PITFALL 3: Using bit-flip oracle instead of phase-flip oracle
# ❌ Oracle that flips |0⟩↔|1⟩ on an auxiliary qubit
# ✅ Oracle that flips the PHASE: |x⟩ → -|x⟩ for good states
# To convert: put auxiliary in |−⟩ state using H,X before oracle

# PITFALL 4: Applying diffuser to ALL qubits instead of VALUE qubits only
# ❌ diffuser on all 9 qubits (including ancillas)
# ✅ diffuser on only the 4 VALUE qubits
# qc.compose(diffuser, qubits=range(n_value_qubits), inplace=True)

# PITFALL 5: Wrong optimal iteration count
# ❌ Always using 1 iteration, or too many iterations (over-rotation)
# ✅ Optimal = floor(π/4 × √(N/M))
#    For N=16, M=2: optimal = floor(π/4 × √8) ≈ floor(2.22) = 2

# PITFALL 6: Using deprecated Qiskit APIs
# ❌ from qiskit.aqua import Grover             # REMOVED long ago
# ❌ GroverOperator(oracle)                      # Deprecated in 2.1
# ✅ from qiskit.circuit.library import grover_operator  # function form
# ✅ from qiskit_algorithms import Grover, AmplificationProblem
# ✅ from qiskit.primitives import StatevectorSampler

# PITFALL 7: Oracle for known+unknown cell pair logic error
# ❌ Treating known cell as if it's on a qubit in superposition
# ✅ Known values are handled classically in the oracle:
#    If cell_a has known_value=1 and cell_b is on qubit q:
#    constraint "cell_a ≠ cell_b" → "1 ≠ q_value" → "q_value must be 0"
#    → ancilla = NOT(q_value) → CNOT(q, ancilla); X(ancilla)

# PITFALL 8: MCZ gate on wrong qubits
# ❌ Including value qubits in the MCZ control list
# ✅ MCZ targets should be ONLY the ancilla qubits (or include output qubit)
#    The MCZ flips phase when all ANCILLAS are |1⟩

# PITFALL 9: Not handling puzzles with multiple solutions correctly
# 2×2 all-unknown has 2 valid solutions
# Grover will amplify BOTH — the top measurement could be either
# Test should accept either solution as correct

# PITFALL 10: V2 Primitive result access
# ❌ result.get_counts()                          # V1 API
# ✅ result[0].data.meas.get_counts()             # V2 API via StatevectorSampler
#    OR use: result[0].data.c.get_counts()        # depends on classical register name
```

### 🏗️ Build Order Summary

```
DAY 1:   Environment + config.yaml + puzzle JSONs + utils.py + puzzle_engine.py
DAY 2:   binary_encoder.py + tests + first XOR oracle building blocks
DAY 3:   constraint_oracle.py (FULL) + exhaustive oracle verification tests
DAY 4:   diffuser.py + grover_solver.py (manual approach)
DAY 5:   grover_solver.py (high-level approach) + solution_decoder.py + integration tests
DAY 6:   visualizer.py (all plots) + notebook 06_visualization_showcase
DAY 7:   classical_solver.py + complexity_analyzer.py + comparison
DAY 8:   Notebooks 01–05 (theory + walkthroughs)
DAY 9:   Notebook 07 + run_solver.py + run_demo.py + README
DAY 10:  Full test suite + polish + stretch goals
```

### 🧪 Minimum Viable Test Sequence

After each phase, run this sanity check:

```python
"""
quick_test.py — Verify end-to-end on simplest case
"""
# This should be runnable after Phase 3 is complete

from src.puzzle_engine import SudokuPuzzle
from src.binary_encoder import SudokuEncoder
from src.constraint_oracle import SudokuOracle
from src.diffuser import build_diffuser
from src.grover_solver import QuantumSudokuSolver
from src.solution_decoder import SudokuDecoder

# Simplest case: 2×2 with one clue
puzzle = SudokuPuzzle(size=2, grid=[[1, None], [None, None]])
solver = QuantumSudokuSolver(puzzle)
result = solver.solve(approach='manual', shots=1024)

print(f"Top measurement: {result['top_measurement']}")
print(f"Decoded solution:")
for row in result['decoded_solution']:
    print(row)
print(f"Valid: {result['is_valid']}")
assert result['is_valid'] == True, "SOLUTION INVALID!"

# Expected: [[1, 0], [0, 1]]
print("\n✅ Quick test PASSED!")
```

### 📊 Expected Output Summary

```
┌──────────────────────────────────────────────────────────┐
│ QUANTUM SUDOKU SOLVER — Results                           │
├──────────────────────────────────────────────────────────┤
│                                                            │
│  Puzzle: 2×2 All Unknown                                  │
│  ┌───┬───┐     ┌───┬───┐                                 │
│  │ ? │ ? │ →→→ │ 1 │ 0 │  ✅                              │
│  ├───┼───┤     ├───┼───┤                                 │
│  │ ? │ ? │     │ 0 │ 1 │                                 │
│  └───┴───┘     └───┴───┘                                 │
│                                                            │
│  Qubits: 4 value + 5 ancilla = 9 total                   │
│  Grover iterations: 2 (optimal)                           │
│  Success probability: 99.6%                                │
│  Circuit depth: 47                                         │
│  Gate count: 38 (12 CNOT, 16 H, 8 X, 2 MCZ)             │
│                                                            │
│  Classical brute force: 16 queries                         │
│  Quantum (Grover): 2 oracle queries (√16 = 4, optimal 2) │
│  Speedup: 8× fewer oracle calls                           │
│                                                            │
│  Generated artifacts:                                      │
│  ├── results/figures/amplitude_evolution.png               │
│  ├── results/figures/measurement_histogram.png             │
│  ├── results/figures/grover_geometry.png                   │
│  ├── results/figures/circuit_diagram.png                   │
│  ├── results/figures/solved_puzzle.png                     │
│  └── results/benchmarks/comparison.csv                     │
└──────────────────────────────────────────────────────────┘
```

---

This document provides everything an AI coding assistant needs to build a complete, visually rich, and technically deep Quantum Sudoku Solver. The oracle construction (Phase 2) is the hardest part — spend the most time verifying it. Feed one phase at a time and test thoroughly before moving on. 🧩⚛️
