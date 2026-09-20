import os
import matplotlib.pyplot as plt
from typing import Any, Dict, List

class GraphGenerator:
    """
    Graph generator rendering matplotlib trend charts for qubit calibration drifts.
    Saves generated visualizations into the root evaluation/ directory.
    """

    @staticmethod
    def generate_plots(
        qubit_id: str,
        calibrations: List[Dict[str, Any]],
        output_dir: str
    ) -> None:
        """
        Generates and saves trend curves for T1, T2, Readout error, Gate errors, Frequency, and Temperature.
        
        Args:
            qubit_id: Label of qubit (e.g. Q0).
            calibrations: 100 epochs list of calibration dictionary items.
            output_dir: Path to write plotted image files.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        epochs = [c["epoch_number"] for c in calibrations]
        t1s = [c["t1"] for c in calibrations]
        t2s = [c["t2"] for c in calibrations]
        readouts = [c["readout_error"] for c in calibrations]
        single_gates = [c["single_gate_error"] for c in calibrations]
        two_gates = [c["two_gate_error"] for c in calibrations]
        frequencies = [c["frequency"] for c in calibrations]
        temperatures = [c["temperature"] for c in calibrations]

        plt.figure(figsize=(12, 10))
        plt.suptitle(f"TwinQ-Map Qubit Drift Trends: {qubit_id}", fontsize=16, color="white")
        plt.style.use("dark_background")

        # 1. Coherence (T1 and T2)
        plt.subplot(3, 2, 1)
        plt.plot(epochs, t1s, label="T1 (Relaxation)", color="#14b8a6")
        plt.plot(epochs, t2s, label="T2 (Dephasing)", color="#06b6d4")
        plt.title("Coherence Times (T1/T2)")
        plt.xlabel("Epoch")
        plt.ylabel("Microseconds")
        plt.legend()
        plt.grid(True, alpha=0.1)

        # 2. Readout Error
        plt.subplot(3, 2, 2)
        plt.plot(epochs, readouts, color="#f43f5e")
        plt.title("Readout Measurement Error Rate")
        plt.xlabel("Epoch")
        plt.ylabel("Error Rate")
        plt.grid(True, alpha=0.1)

        # 3. Gate Errors
        plt.subplot(3, 2, 3)
        plt.plot(epochs, single_gates, label="Single Gate", color="#10b981")
        plt.plot(epochs, two_gates, label="Two Gate", color="#8b5cf6")
        plt.title("Gate Error Rates")
        plt.xlabel("Epoch")
        plt.ylabel("Error Rate")
        plt.legend()
        plt.grid(True, alpha=0.1)

        # 4. Frequency Drift
        plt.subplot(3, 2, 4)
        plt.plot(epochs, frequencies, color="#eab308")
        plt.title("Operating Frequency Drift")
        plt.xlabel("Epoch")
        plt.ylabel("GHz")
        plt.grid(True, alpha=0.1)

        # 5. Temperature Fluctuation
        plt.subplot(3, 2, 5)
        plt.plot(epochs, temperatures, color="#f97316")
        plt.title("QPU Cryostat Temperature Cycles")
        plt.xlabel("Epoch")
        plt.ylabel("Kelvin")
        plt.grid(True, alpha=0.1)

        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        
        output_file = os.path.join(output_dir, f"{qubit_id}_drift_trends.png")
        plt.savefig(output_file, dpi=100)
        plt.close()
