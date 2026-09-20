from typing import Any, Dict, List
from datetime import datetime, timezone
import numpy as np
from backend.quantum.base import BaseQuantumProviderAdapter
from backend.core.logging import quantum_api_logger
from backend.mathematical_quantum_simulator.calibration_generator import CalibrationGenerator

class MathematicalQuantumSimulator(BaseQuantumProviderAdapter):
    """
    Unified Mathematical Quantum Simulator interface consolidates calibration models,
    noise perturbations, and execution estimations.
    """

    def __init__(self, start_epoch: datetime = None, seed: int = 42):
        self.start_epoch = start_epoch or datetime(2026, 7, 2, 0, 0, 0, tzinfo=timezone.utc)
        self.provider_name = "mathematical_quantum_simulator"
        self.active_qubit_ids = ["Q0", "Q1", "Q2", "Q3", "Q4"]
        self.cal_gen = CalibrationGenerator(seed=seed)

    def get_provider_name(self) -> str:
        return self.provider_name

    def _get_elapsed_epochs(self) -> int:
        """
        Translates time passed since start_epoch into integer epochs (1 hour per epoch).
        """
        current_time = datetime.now(timezone.utc)
        delta = current_time - self.start_epoch
        # Return elapsed hours as integer epoch index
        return max(0, int(delta.total_seconds() / 3600.0))

    def _simulate_qubit_calibration(self, qubit_id: str, epoch: int) -> Dict[str, Any]:
        """
        Runs deterministic formulas to evaluate qubit parameters at a specific epoch.
        """
        try:
            q_idx = int(qubit_id.replace("Q", ""))
        except ValueError:
            q_idx = 0

        t1_0 = 100.0 + (q_idx * 10.0)
        t2_0 = 80.0 + (q_idx * 5.0)
        er_0 = 0.01 + (q_idx * 0.005)
        freq_0 = 5.0 + (q_idx * 0.05)

        return self.cal_gen.generate_calibration(
            qubit_id=qubit_id,
            epoch=epoch,
            t1_0=t1_0,
            t2_0=t2_0,
            er_0=er_0,
            eg_1q_0=0.0005,
            eg_2q_0=0.010,
            freq_0=freq_0
        )

    async def get_calibration_data(self) -> List[Dict[str, Any]]:
        """
        Fetches decayed calibrations for all active simulator qubits.
        """
        quantum_api_logger.info("Retrieving calibrations from AutonomousSimulationRunner...")
        from backend.machine_learning.training.runner import AutonomousSimulationRunner
        state = AutonomousSimulationRunner.state
        if state["status"] != "IDLE" and state["latest_calibrations"]:
            return state["latest_calibrations"]
            
        # Fallback to loading latest calibrations from database
        try:
            from backend.database.connection import MongoDBManager
            if MongoDBManager.client is not None:
                qubit_count = state.get("qubit_count", 5)
                coll_name = f"exp_{qubit_count}Q_calibrations"
                cursor = db[coll_name].find({"epoch_number": state.get("current_epoch", 0)})
                res = []
                async for doc in cursor:
                    doc["_id"] = str(doc["_id"])
                    res.append(doc)
                if res:
                    return res
        except Exception:
            pass
            
        # Hard fallback to baseline if database is empty
        epoch = self._get_elapsed_epochs()
        return [self._simulate_qubit_calibration(qid, epoch) for qid in self.active_qubit_ids]

    async def execute_circuit(
        self,
        circuit_representation: Any,
        physical_mapping: List[int],
        shots: int = 1024
    ) -> Dict[str, Any]:
        """
        Deterministic execution logic returning counts and fidelity based on formulas.
        """
        quantum_api_logger.info("Executing circuit program mathematically on simulated backend...")
        epoch = self._get_elapsed_epochs()
        
        active_calibs = [self._simulate_qubit_calibration(f"Q{p}", epoch) for p in physical_mapping]
        
        if not active_calibs:
            avg_gate_error = 0.01
            avg_readout_error = 0.02
            avg_coherence = 100.0
        else:
            avg_gate_error = sum(c["single_gate_error"] for c in active_calibs) / len(active_calibs)
            avg_readout_error = sum(c["readout_error"] for c in active_calibs) / len(active_calibs)
            avg_coherence = sum(c["t1"] + c["t2"] for c in active_calibs) / (2.0 * len(active_calibs))

        # Model a circuit of depth = 15 with 10 single-qubit and 5 two-qubit gates
        n_1q = 10
        n_2q = 5
        t_circ = 0.5  # duration in microseconds

        # P_success model
        p_succ = float(np.exp(-(n_1q * avg_gate_error) - (n_2q * avg_gate_error * 10)))
        fidelity = float(p_succ * np.exp(-t_circ / avg_coherence))
        
        import re
        import random

        # 1. Parse number of qubits in register from QASM
        qreg_match = re.search(r"qreg\s+q\s*\[(\d+)\]", str(circuit_representation))
        num_qubits = int(qreg_match.group(1)) if qreg_match else 1
            
        # 2. Determine target states based on gates
        has_h = "h " in str(circuit_representation) or "h\t" in str(circuit_representation) or "h(" in str(circuit_representation)
        has_cx = "cx " in str(circuit_representation) or "cx\t" in str(circuit_representation) or "cx(" in str(circuit_representation) or "cnot" in str(circuit_representation).lower()
        
        target_counts = int(shots * fidelity)
        noise_counts = shots - target_counts
        
        counts = {}
        def format_state(val: int) -> str:
            return format(val, f"0{num_qubits}b")
            
        if num_qubits == 2 and has_h and has_cx:
            # Entangled Bell State (|00> + |11>) / sqrt(2)
            half_target = target_counts // 2
            drift = int(random.gauss(0, 15))
            c_00 = max(0, min(target_counts, half_target + drift))
            c_11 = max(0, target_counts - c_00)
            
            half_noise = noise_counts // 2
            c_01 = half_noise
            c_10 = noise_counts - c_01
            
            counts["00"] = c_00
            counts["11"] = c_11
            if c_01 > 0: counts["01"] = c_01
            if c_10 > 0: counts["10"] = c_10
        elif num_qubits == 1:
            if has_h:
                # Superposition state (|0> + |1>) / sqrt(2)
                half_target = target_counts // 2
                drift = int(random.gauss(0, 10))
                c_0 = max(0, min(target_counts, half_target + drift))
                c_1 = max(0, target_counts - c_0)
                counts["0"] = c_0
                counts["1"] = c_1 + noise_counts
            else:
                counts["0"] = target_counts
                counts["1"] = noise_counts
        else:
            # General case: ground state |00...0> is the primary outcome, distribute noise
            counts[format_state(0)] = target_counts
            if noise_counts > 0:
                states_to_distribute = min(noise_counts, (1 << num_qubits) - 1)
                if states_to_distribute > 0:
                    noise_per_state = noise_counts // states_to_distribute
                    remainder = noise_counts % states_to_distribute
                    for i in range(1, states_to_distribute + 1):
                        state_str = format_state(i)
                        counts[state_str] = noise_per_state + (1 if i <= remainder else 0)
                        
        success_rate = target_counts / shots

        return {
            "job_id": f"sim_job_{int(datetime.now(timezone.utc).timestamp())}",
            "provider": self.provider_name,
            "status": "COMPLETED",
            "counts": counts,
            "fidelity": fidelity,
            "success_rate": success_rate
        }

    async def get_device_status(self) -> Dict[str, Any]:
        """
        Queries status of the mathematical quantum simulator.
        """
        return {
            "status": "ONLINE",
            "pending_jobs": 0,
            "backend_name": "TwinQ_Math_Simulator_5Q"
        }
