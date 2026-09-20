import numpy as np
from typing import Dict, Any
from backend.mathematical_quantum_simulator.noise_generator import NoiseGenerator
from backend.mathematical_quantum_simulator.frequency_generator import FrequencyGenerator
from backend.mathematical_quantum_simulator.temperature_generator import TemperatureGenerator

class CalibrationGenerator:
    """
    Calibration generator evaluating NISQ qubit coherence, gate, and readout error drifts.
    
    ============================================================================
    MATHEMATICAL FORMULATIONS
    ============================================================================
    1. T1 Relaxation Time:
       T_1(epoch) = T_{1,0} * exp(-alpha_t1 * epoch)
       
    2. T2 Dephasing Time:
       T_2(epoch) = T_{2,0} * exp(-beta_t2 * epoch)
       
    3. Readout Error:
       E_R(epoch) = E_{R,0} + (linear_drift * epoch) + ReadoutNoise(epoch)
       
    4. Single-Qubit Gate Error:
       E_{1Q}(epoch) = E_{1Q,0} * (T_{1,0} / T_1(epoch)) + GateNoise(epoch)
       
    5. Two-Qubit Gate Error:
       E_{2Q}(epoch) = E_{2Q,0} * (T_{2,0} / T_2(epoch)) + GateNoise(epoch)
    """

    def __init__(self, seed: int = 42):
        self.noise_gen = NoiseGenerator(seed=seed)
        self.temp_gen = TemperatureGenerator()

    def generate_calibration(
        self,
        qubit_id: str,
        epoch: int,
        t1_0: float,
        t2_0: float,
        er_0: float,
        eg_1q_0: float,
        eg_2q_0: float,
        freq_0: float,
        alpha_t1: float = 0.002,
        beta_t2: float = 0.003,
        readout_drift_factor: float = 0.0001
    ) -> Dict[str, Any]:
        """
        Runs the deterministic formulas to calculate decayed calibration metrics for a single qubit.
        """
        # Coherence decays
        t1 = t1_0 * np.exp(-alpha_t1 * epoch)
        t2 = t2_0 * np.exp(-beta_t2 * epoch)

        # Operating frequency linear drift
        freq = FrequencyGenerator.generate_frequency(freq_0, epoch)

        # Cryostat temperature cycle
        temp = self.temp_gen.generate_temperature(epoch)

        # Gaussian Readout noise & drift
        readout_noise = self.noise_gen.generate_readout_noise()
        readout_error = er_0 + (readout_drift_factor * epoch) + readout_noise
        readout_error = max(0.0, min(1.0, readout_error))

        # Gate errors grow proportionally as T1/T2 decline
        eg_1q_noise = self.noise_gen.generate_gate_noise()
        eg_1q = eg_1q_0 * (t1_0 / t1) + eg_1q_noise
        eg_1q = max(0.0, min(1.0, eg_1q))

        eg_2q_noise = self.noise_gen.generate_gate_noise()
        eg_2q = eg_2q_0 * (t2_0 / t2) + eg_2q_noise
        eg_2q = max(0.0, min(1.0, eg_2q))

        return {
            "epoch_number": epoch,
            "qubit_id": qubit_id,
            "t1": float(t1),
            "t2": float(t2),
            "readout_error": float(readout_error),
            "single_gate_error": float(eg_1q),
            "two_gate_error": float(eg_2q),
            "frequency": float(freq),
            "temperature": float(temp),
            "noise_drift": float(readout_noise),
            "drift_rate": float(-alpha_t1 * t1),
            "backend_status": "Active",
            "version_number": 1
        }
