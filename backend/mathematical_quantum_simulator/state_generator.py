from typing import List

class StateGenerator:
    """
    Mathematical state space generator for multi-qubit systems.
    Generates computational basis states for N-qubit systems.
    """

    @staticmethod
    def generate_basis_states(num_qubits: int) -> List[str]:
        """
        Generates the 2^N computational basis states in binary string format.
        
        Args:
            num_qubits: Number of physical qubits in the system (1 to 5).
            
        Returns:
            List of binary string representation of states (e.g. ['00', '01', '10', '11'] for 2 qubits).
        """
        if not (1 <= num_qubits <= 5):
            raise ValueError("Supported qubit count is between 1 and 5.")
            
        total_states = 1 << num_qubits
        basis_states = []
        for i in range(total_states):
            # Format to binary string padded to qubit count
            binary_str = format(i, f"0{num_qubits}b")
            basis_states.append(binary_str)
        return basis_states
