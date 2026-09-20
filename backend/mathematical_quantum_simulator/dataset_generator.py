import os
import json
import csv
import numpy as np
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List

from backend.mathematical_quantum_simulator.state_generator import StateGenerator
from backend.mathematical_quantum_simulator.topology_generator import TopologyGenerator
from backend.mathematical_quantum_simulator.calibration_generator import CalibrationGenerator
from backend.mathematical_quantum_simulator.statistics_generator import StatisticsGenerator
from backend.mathematical_quantum_simulator.graph_generator import GraphGenerator

class DatasetGenerator:
    """
    Dataset Generator engine driving 100-epoch simulations, chronological data splits,
    statistics calculations, and plotting configurations.
    """

    def __init__(self, base_output_path: str = None, seed: int = 42):
        self.output_path = base_output_path or r"C:\Users\chsai\.gemini\antigravity\scratch\TwinQ-Map\datasets"
        self.eval_path = r"C:\Users\chsai\.gemini\antigravity\scratch\TwinQ-Map\evaluation"
        self.cal_gen = CalibrationGenerator(seed=seed)
        self.rng = np.random.default_rng(seed=seed)

    def generate_all_datasets(self) -> List[str]:
        """
        Drives simulation data generations for 1Q, 2Q, 3Q, 4Q, and 5Q.
        
        Returns:
            List of generated directory paths.
        """
        qubit_configurations = {
            "1_qubit": {"qubits": ["Q0"]},
            "2_qubit": {"qubits": ["Q0", "Q1"]},
            "3_qubit": {"qubits": ["Q0", "Q1", "Q2"]},
            "4_qubit": {"qubits": ["Q0", "Q1", "Q2", "Q3"]},
            "5_qubit": {"qubits": ["Q0", "Q1", "Q2", "Q3", "Q4"]}
        }
        
        generated_paths = []
        for name, config in qubit_configurations.items():
            path = self.generate_system_dataset(name, config["qubits"])
            generated_paths.append(path)
        return generated_paths

    def generate_system_dataset(self, system_name: str, qubits: List[str]) -> str:
        """
        Runs 100 epoch simulation for a specific multi-qubit system and writes outputs.
        """
        n_qubits = len(qubits)
        epochs_count = 100
        start_time = datetime(2026, 7, 2, 0, 0, 0, tzinfo=timezone.utc)
        
        # 1. Setup paths
        system_dir = os.path.join(self.output_path, system_name)
        os.makedirs(system_dir, exist_ok=True)

        # 2. Setup Topologies & States
        topology = TopologyGenerator.generate_topology(n_qubits)
        states = StateGenerator.generate_basis_states(n_qubits)

        # 3. Simulate Calibrations over 100 Epochs
        calibrations = []
        t1_0 = {q: 100.0 + (i * 10.0) for i, q in enumerate(qubits)}
        t2_0 = {q: 80.0 + (i * 5.0) for i, q in enumerate(qubits)}
        er_0 = {q: 0.01 + (i * 0.005) for i, q in enumerate(qubits)}
        freq_0 = {q: 5.0 + (i * 0.05) for i, q in enumerate(qubits)}

        for epoch in range(epochs_count):
            epoch_time = start_time + timedelta(hours=epoch)
            for q in qubits:
                cal = self.cal_gen.generate_calibration(
                    qubit_id=q,
                    epoch=epoch,
                    t1_0=t1_0[q],
                    t2_0=t2_0[q],
                    er_0=er_0[q],
                    eg_1q_0=0.0005,
                    eg_2q_0=0.010,
                    freq_0=freq_0[q]
                )
                # Parse timestamp
                cal["timestamp"] = epoch_time.isoformat()
                calibrations.append(cal)

        # Write calibration.csv
        cal_fields = ["epoch_number", "timestamp", "qubit_id", "t1", "t2", "readout_error", "single_gate_error", "two_gate_error", "frequency", "temperature", "noise_drift", "drift_rate", "backend_status", "version_number"]
        self._write_csv(os.path.join(system_dir, "calibration.csv"), cal_fields, calibrations)

        # Chronological Split (Train 70, Val 15, Test 15)
        train_split = 70
        val_split = 85

        train_cal = [c for c in calibrations if c["epoch_number"] < train_split]
        val_cal = [c for c in calibrations if train_split <= c["epoch_number"] < val_split]
        test_cal = [c for c in calibrations if c["epoch_number"] >= val_split]

        self._write_csv(os.path.join(system_dir, "train.csv"), cal_fields, train_cal)
        self._write_csv(os.path.join(system_dir, "validation.csv"), cal_fields, val_cal)
        self._write_csv(os.path.join(system_dir, "test.csv"), cal_fields, test_cal)

        # 4. Generate Predictions CSV
        predictions = []
        for epoch in range(epochs_count):
            epoch_time = start_time + timedelta(hours=epoch)
            for q in qubits:
                predictions.append({
                    "timestamp": epoch_time.isoformat(),
                    "prediction_timestamp": (epoch_time + timedelta(hours=24)).isoformat(),
                    "qubit_id": q,
                    "predicted_readout_error": float(er_0[q] + ((epoch + 24) * 0.0001)),
                    "predicted_t1": float(t1_0[q] * np.exp(-0.002 * (epoch + 24))),
                    "predicted_t2": float(t2_0[q] * np.exp(-0.003 * (epoch + 24))),
                    "predicted_gate_error_1q": float(0.0005 * np.exp(0.002 * (epoch + 24))),
                    "predicted_gate_error_2q": float(0.0100 * np.exp(0.003 * (epoch + 24))),
                    "prediction_confidence": 0.95
                })
        pred_fields = ["timestamp", "prediction_timestamp", "qubit_id", "predicted_readout_error", "predicted_t1", "predicted_t2", "predicted_gate_error_1q", "predicted_gate_error_2q", "prediction_confidence"]
        self._write_csv(os.path.join(system_dir, "prediction.csv"), pred_fields, predictions)

        # 5. Generate Executions CSV
        executions = []
        for epoch in range(epochs_count):
            epoch_time = start_time + timedelta(hours=epoch)
            success_rate = 0.985 - (epoch * 0.0004)
            fidelity = 0.990 - (epoch * 0.0004)
            executions.append({
                "timestamp": epoch_time.isoformat(),
                "circuit_id": f"circ_{epoch:03d}",
                "provider": "MathematicalQuantumSimulator",
                "physical_qubits": ",".join(str(i) for i in range(n_qubits)),
                "logical_qubits": n_qubits,
                "execution_time": 0.045,
                "success_rate": float(success_rate),
                "error_count": int(1024 * (1.0 - success_rate)),
                "fidelity": float(fidelity)
            })
        exec_fields = ["timestamp", "circuit_id", "provider", "physical_qubits", "logical_qubits", "execution_time", "success_rate", "error_count", "fidelity"]
        self._write_csv(os.path.join(system_dir, "execution.csv"), exec_fields, executions)

        # 6. Generate Feedback CSV
        feedback = []
        for epoch in range(epochs_count):
            epoch_time = start_time + timedelta(hours=epoch)
            for q in qubits:
                predicted_t1 = t1_0[q] * np.exp(-0.002 * epoch)
                observed_t1 = predicted_t1 + self.rng.normal(0, 0.2)
                feedback.append({
                    "timestamp": epoch_time.isoformat(),
                    "qubit_id": q,
                    "observed_error": float(observed_t1),
                    "predicted_error": float(predicted_t1),
                    "error_delta": float(observed_t1 - predicted_t1),
                    "learning_rate": 0.01,
                    "parameter_updates": 0.002
                })
        feedback_fields = ["timestamp", "qubit_id", "observed_error", "predicted_error", "error_delta", "learning_rate", "parameter_updates"]
        self._write_csv(os.path.join(system_dir, "feedback.csv"), feedback_fields, feedback)

        # 7. Generate QHI CSV
        qhi_data = []
        for epoch in range(epochs_count):
            epoch_time = start_time + timedelta(hours=epoch)
            for q in qubits:
                qhi_data.append({
                    "timestamp": epoch_time.isoformat(),
                    "qubit_id": q,
                    "health_index": float(0.98 - (epoch * 0.0008)),
                    "weight_readout": 0.3,
                    "weight_t1": 0.2,
                    "weight_t2": 0.2,
                    "weight_gate": 0.3
                })
        qhi_fields = ["timestamp", "qubit_id", "health_index", "weight_readout", "weight_t1", "weight_t2", "weight_gate"]
        self._write_csv(os.path.join(system_dir, "qhi.csv"), qhi_fields, qhi_data)

        # 8. Generate Scheduler CSV
        sched_data = []
        for epoch in range(epochs_count):
            epoch_time = start_time + timedelta(hours=epoch)
            sched_data.append({
                "timestamp": epoch_time.isoformat(),
                "job_id": f"job_{epoch:03d}",
                "logical_circuit_size": n_qubits,
                "mapping_selected": ",".join(str(i) for i in range(n_qubits)),
                "scheduling_algorithm": "QHI_Greedy",
                "cost_evaluated": float(0.005 * epoch),
                "waiting_time": 1.2,
                "execution_status": "COMPLETED"
            })
        sched_fields = ["timestamp", "job_id", "logical_circuit_size", "mapping_selected", "scheduling_algorithm", "cost_evaluated", "waiting_time", "execution_status"]
        self._write_csv(os.path.join(system_dir, "scheduler.csv"), sched_fields, sched_data)

        # 9. Generate Training CSV
        train_data = []
        for epoch in range(epochs_count):
            epoch_time = start_time + timedelta(hours=epoch)
            train_data.append({
                "timestamp": epoch_time.isoformat(),
                "epoch": epoch,
                "loss": float(0.15 * np.exp(-0.05 * epoch)),
                "val_loss": float(0.16 * np.exp(-0.04 * epoch)),
                "accuracy": float(0.90 + (0.09 * (1.0 - np.exp(-0.05 * epoch)))),
                "val_accuracy": float(0.89 + (0.08 * (1.0 - np.exp(-0.04 * epoch)))),
                "model_version": f"v1.{epoch}"
            })
        train_fields = ["timestamp", "epoch", "loss", "val_loss", "accuracy", "val_accuracy", "model_version"]
        self._write_csv(os.path.join(system_dir, "training.csv"), train_fields, train_data)

        # 10. Compute JSON metrics files
        stats = StatisticsGenerator.calculate_statistics(calibrations)
        metadata = StatisticsGenerator.generate_metadata(n_qubits, qubits, topology)
        summary = StatisticsGenerator.generate_summary(stats)

        self._write_json(os.path.join(system_dir, "statistics.json"), stats)
        self._write_json(os.path.join(system_dir, "metadata.json"), metadata)
        self._write_json(os.path.join(system_dir, "summary.json"), summary)

        # 11. Plot Curves for the main Qubit Q0
        GraphGenerator.generate_plots(
            qubit_id=f"{system_name}_Q0",
            calibrations=[c for c in calibrations if c["qubit_id"] == "Q0"],
            output_dir=self.eval_path
        )

        return system_dir

    def _write_csv(self, filepath: str, fieldnames: List[str], data: List[Dict[str, Any]]):
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)

    def _write_json(self, filepath: str, data: Dict[str, Any]):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
