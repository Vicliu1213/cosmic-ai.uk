# core/circuit.py
class QuantumCircuit:
    """最简单的量子电路表示，用于占位"""
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.gates = []

    def add_gate(self, gate_name: str, qubits: list, params: list = None):
        self.gates.append((gate_name, qubits, params))

    def __len__(self):
        return len(self.gates)
