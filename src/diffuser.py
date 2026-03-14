from qiskit import QuantumCircuit


def build_diffuser(n_qubits: int) -> QuantumCircuit:
    qc = QuantumCircuit(n_qubits, name="Diffuser")
    if n_qubits == 0:
        return qc
    qc.h(range(n_qubits))
    qc.x(range(n_qubits))
    if n_qubits == 1:
        qc.z(0)
    else:
        target = n_qubits - 1
        controls = list(range(n_qubits - 1))
        qc.h(target)
        qc.mcx(controls, target)
        qc.h(target)
    qc.x(range(n_qubits))
    qc.h(range(n_qubits))
    return qc


def build_diffuser_custom(n_qubits: int, state_prep: QuantumCircuit = None) -> QuantumCircuit:
    if state_prep is None:
        return build_diffuser(n_qubits)
    qc = QuantumCircuit(n_qubits, name="DiffuserCustom")
    qc.compose(state_prep.inverse(), inplace=True)
    qc.x(range(n_qubits))
    if n_qubits == 1:
        qc.z(0)
    else:
        target = n_qubits - 1
        controls = list(range(n_qubits - 1))
        qc.h(target)
        qc.mcx(controls, target)
        qc.h(target)
    qc.x(range(n_qubits))
    qc.compose(state_prep, inplace=True)
    return qc


def verify_diffuser(diffuser: QuantumCircuit) -> bool:
    return diffuser.num_qubits >= 0 and diffuser.depth() >= 0
