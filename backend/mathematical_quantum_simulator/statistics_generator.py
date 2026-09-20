import numpy as np
from typing import Any, Dict, List

class StatisticsGenerator:
    """
    Statistics generator calculating performance, decay, and stability parameters from generated datasets.
    Outputs metadata, summaries, and mathematical metrics.
    """

    @staticmethod
    def calculate_statistics(calibrations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Computes average, standard deviation, max, and min calibration parameters.
        """
        if not calibrations:
            return {}

        t1s = [c["t1"] for c in calibrations]
        t2s = [c["t2"] for c in calibrations]
        readouts = [c["readout_error"] for c in calibrations]
        gate_1q = [c["single_gate_error"] for c in calibrations]
        gate_2q = [c["two_gate_error"] for c in calibrations]

        return {
            "t1": {
                "mean": float(np.mean(t1s)),
                "std": float(np.std(t1s)),
                "max": float(np.max(t1s)),
                "min": float(np.min(t1s))
            },
            "t2": {
                "mean": float(np.mean(t2s)),
                "std": float(np.std(t2s)),
                "max": float(np.max(t2s)),
                "min": float(np.min(t2s))
            },
            "readout_error": {
                "mean": float(np.mean(readouts)),
                "std": float(np.std(readouts)),
                "max": float(np.max(readouts)),
                "min": float(np.min(readouts))
            },
            "single_gate_error": {
                "mean": float(np.mean(gate_1q)),
                "std": float(np.std(gate_1q)),
                "max": float(np.max(gate_1q)),
                "min": float(np.min(gate_1q))
            },
            "two_gate_error": {
                "mean": float(np.mean(gate_2q)),
                "std": float(np.std(gate_2q)),
                "max": float(np.max(gate_2q)),
                "min": float(np.min(gate_2q))
            }
        }

    @staticmethod
    def generate_metadata(
        qubit_count: int,
        qubits: List[str],
        topology: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Creates system specifications describing the quantum topology configuration.
        """
        return {
            "qubit_count": qubit_count,
            "qubits": qubits,
            "basis_states_count": 1 << qubit_count,
            "topology": {
                "edge_list": [[int(u), int(v)] for u, v in topology["edge_list"]],
                "adjacency_list": {int(k): [int(v) for v in val] for k, val in topology["adjacency_list"].items()}
            },
            "calibration_equations": {
                "t1_decay": "T1_0 * exp(-0.002 * epoch)",
                "t2_decay": "T2_0 * exp(-0.003 * epoch)",
                "readout_drift": "er_0 + 0.0001 * epoch + GaussianNoise",
                "gate_error_growth": "eg_0 * (T0 / T(epoch))"
            }
        }

    @staticmethod
    def generate_summary(stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates a high-level summary overview of system health stability.
        """
        if not stats:
            return {}
            
        t1_mean = stats["t1"]["mean"]
        readout_mean = stats["readout_error"]["mean"]
        stability_score = 1.0 - (stats["readout_error"]["std"] / readout_mean) if readout_mean > 0.0 else 1.0
        stability_score = max(0.0, min(1.0, stability_score))

        return {
            "overall_stability_score": stability_score,
            "status": "Stable" if stability_score > 0.90 else "Degrading",
            "average_t1_microseconds": t1_mean,
            "average_readout_error": readout_mean
        }
