from abc import ABC, abstractmethod
from typing import Any, Dict, List

class BaseQuantumProviderAdapter(ABC):
    """
    Hardware-agnostic abstract interface for quantum cloud backends and mathematical simulators.
    Enables pluggable data source execution and calibration reading.
    """

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Returns the unique identifier of the quantum provider (e.g., 'ibm', 'ionq', 'simulator').
        """
        pass

    @abstractmethod
    async def get_calibration_data(self) -> List[Dict[str, Any]]:
        """
        Fetches current physical calibration parameters (T1, T2, readout errors, gate errors, frequency)
        for all active qubits.
        
        Returns:
            A list of dictionary calibration records matching CalibrationHistory schema.
        """
        pass

    @abstractmethod
    async def execute_circuit(
        self,
        circuit_representation: Any,
        physical_mapping: List[int],
        shots: int = 1024
    ) -> Dict[str, Any]:
        """
        Dispatches a logical quantum circuit mapping to specified physical qubits on the hardware backend.
        
        Args:
            circuit_representation: The logical circuit (Qiskit QuantumCircuit or openQASM string).
            physical_mapping: Map from logical index -> physical qubit index (e.g. [3, 0, 1]).
            shots: Total number of execution trials.
            
        Returns:
            A standardized dictionary containing job ID, counts, estimated fidelity, and success rate.
        """
        pass

    @abstractmethod
    async def get_device_status(self) -> Dict[str, Any]:
        """
        Queries status, queue wait time, active physical qubit count, and operational state.
        """
        pass
