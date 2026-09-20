from typing import Dict, Any
from backend.config.constants import QHIWeights, QuantumFidelityThresholds

class QHIIndicator:
    """
    Qubit Health Index (QHI) calculator.
    
    ============================================================================
    MATHEMATICAL FORMULATIONS
    ============================================================================
    The health of a physical qubit is evaluated based on normalized ratio limits:
    
    QHI(v_p) = w_readout * (1.0 - E_R)
             + w_t1 * min(1.0, T_1 / T1_threshold)
             + w_t2 * min(1.0, T_2 / T2_threshold)
             + w_gate * (1.0 - E_{1Q})
             
    where:
      - E_R is Readout error.
      - E_{1Q} is Single-qubit gate error.
      - T_1, T_2 are decayed coherence times.
      - w_readout, w_t1, w_t2, w_gate are standard constants sum to 1.0.
    """

    @staticmethod
    def compute_qhi(calibration: Dict[str, Any]) -> float:
        """
        Computes the Qubit Health Index (QHI) score between 0.0 and 1.0.
        """
        # Read parameters
        t1 = calibration.get("t1", 0.0)
        t2 = calibration.get("t2", 0.0)
        er = calibration.get("readout_error", 0.0)
        eg_1q = calibration.get("single_gate_error", 0.0)

        # Normalize metrics to bounds
        t1_norm = min(1.0, t1 / QuantumFidelityThresholds.MIN_T1_MICROSECONDS) if QuantumFidelityThresholds.MIN_T1_MICROSECONDS > 0.0 else 1.0
        t2_norm = min(1.0, t2 / QuantumFidelityThresholds.MIN_T2_MICROSECONDS) if QuantumFidelityThresholds.MIN_T2_MICROSECONDS > 0.0 else 1.0
        
        readout_fidelity = max(0.0, 1.0 - er)
        gate_fidelity = max(0.0, 1.0 - eg_1q)

        # Weighted calculation
        qhi = (
            QHIWeights.READOUT_ERROR_WEIGHT * readout_fidelity +
            QHIWeights.T1_COHERENCE_WEIGHT * t1_norm +
            QHIWeights.T2_COHERENCE_WEIGHT * t2_norm +
            QHIWeights.GATE_ERROR_WEIGHT * gate_fidelity
        )

        return float(max(0.0, min(1.0, qhi)))
