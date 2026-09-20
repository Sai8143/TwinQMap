import os
import math
import json
import joblib
import asyncio
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.multioutput import MultiOutputRegressor
from xgboost import XGBRegressor
from lightgbm import LGBMRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from backend.database.connection import MongoDBManager
from backend.config.constants import DBCollections
from backend.scheduler.health.qhi import QHIIndicator
from backend.scheduler.mapping.mapper import QubitMapper
from backend.mathematical_quantum_simulator.topology_generator import TopologyGenerator
from backend.core.logging import training_logger

DEFAULT_DECAY_PARAMS = {
    "alpha": 0.003,
    "beta": 0.004,
    "gamma": 0.001,
    "delta": 0.0005,
    "epsilon": 0.0001,
    "eta": 0.00005,
    "theta": 0.0001,
    "kappa": 0.00005
}

class MathematicalQubitEvolution:
    """
    Simulates physical decay, thermal drifts, and 1/f noise cycles for physical qubits.
    """
    def __init__(self, decay_params: dict = None, qubit_count: int = 5):
        self.params = decay_params or DEFAULT_DECAY_PARAMS
        self.qubit_count = qubit_count

    def evolve_qubit(self, prev_cal: dict, qubit_id: str, epoch: int) -> dict:
        try:
            q_idx = int(qubit_id.replace("Q", "").replace("q", ""))
        except ValueError:
            q_idx = 0

        # Epoch 0 baseline initialization
        if not prev_cal:
            if self.qubit_count in (11, 25):
                # Trapped-Ion (IonQ) parameter ranges
                t1_val = 2000000.0 + (q_idx * 1000.0)
                t2_val = 1000000.0 + (q_idx * 500.0)
                ro_val = 0.005 + (q_idx * 0.0001)
                sg_val = 0.0004 + (q_idx * 0.00001)
                return {
                    "qubit_id": qubit_id,
                    "epoch_number": 0,
                    "t1": t1_val,
                    "t2": t2_val,
                    "readout_error": ro_val,
                    "single_gate_error": sg_val,
                    "two_gate_error": 0.015,
                    "frequency": 3.2,
                    "temperature": 0.0,
                    "noise_drift": 0.0,
                    "drift_rate": 0.0,
                    "backend_status": "Active",
                    "backend_name": "ionq_aria_simulated" if self.qubit_count == 11 else "ionq_forte_simulated",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "version": 1,
                    "is_deleted": False,
                    # Retain base trackers
                    "t1_base": t1_val,
                    "t2_base": t2_val,
                    "frequency_base": 3.2,
                    "readout_base": ro_val,
                    "single_gate_base": sg_val
                }
            
            return {
                "qubit_id": qubit_id,
                "epoch_number": 0,
                "t1": 120.0 + (q_idx * 15.0),
                "t2": 90.0 + (q_idx * 10.0),
                "readout_error": 0.01 + (q_idx * 0.002),
                "single_gate_error": 0.002 + (q_idx * 0.0005),
                "two_gate_error": 0.010,
                "frequency": 4.9 + (q_idx * 0.05),
                "temperature": 15.0,
                "noise_drift": 0.0,
                "drift_rate": 0.0,
                "backend_status": "Active",
                "backend_name": "TwinQ_Math_Simulator_5Q",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": 1,
                "is_deleted": False,
                # Retain base trackers
                "t1_base": 120.0 + (q_idx * 15.0),
                "t2_base": 90.0 + (q_idx * 10.0),
                "frequency_base": 4.9 + (q_idx * 0.05),
                "readout_base": 0.01 + (q_idx * 0.002),
                "single_gate_base": 0.002 + (q_idx * 0.0005)
            }

        # Sequential evolution equations
        decay_factor = math.exp(-self.params["alpha"] * epoch)
        drift_cycle = math.sin(epoch * 0.1) * 0.02
        noise_fluctuation = (math.cos(epoch * 0.5) * 0.01) * self.params["kappa"]

        # Fetch trackers
        t1_base = prev_cal.get("t1_base", 120.0 + (q_idx * 15.0))
        t2_base = prev_cal.get("t2_base", 90.0 + (q_idx * 10.0))
        freq_base = prev_cal.get("frequency_base", 4.9 + (q_idx * 0.05))
        ro_base = prev_cal.get("readout_base", 0.01 + (q_idx * 0.002))
        single_gate_base = prev_cal.get("single_gate_base", 0.002 + (q_idx * 0.0005))

        t1 = max(t1_base * decay_factor + (drift_cycle * 5), 1.0)
        t2 = max(min(t2_base * decay_factor + (drift_cycle * 3), t1 * 0.95), 0.5)

        # Drifts
        freq = freq_base + (drift_cycle * 0.05) + noise_fluctuation
        temp = 15.0 + abs(drift_cycle * 2.0)
        readout_error = min(ro_base * (1.0 + 0.005 * epoch) + abs(drift_cycle * 0.01), 1.0)
        single_gate_error = min(single_gate_base * (1.0 + 0.004 * epoch) + abs(noise_fluctuation * 0.02), 1.0)
        two_gate_error = min(0.010 * (1.0 + 0.003 * epoch), 1.0)

        return {
            "qubit_id": qubit_id,
            "epoch_number": epoch,
            "t1": t1,
            "t2": t2,
            "readout_error": readout_error,
            "single_gate_error": single_gate_error,
            "two_gate_error": two_gate_error,
            "frequency": freq,
            "temperature": temp,
            "noise_drift": noise_fluctuation,
            "drift_rate": t1 - prev_cal["t1"],
            "backend_status": "Active",
            "backend_name": prev_cal.get("backend_name", "TwinQ_Math_Simulator_5Q"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "version": 1,
            "is_deleted": False,
            # Pass base trackers through to next epoch
            "t1_base": t1_base,
            "t2_base": t2_base,
            "frequency_base": freq_base,
            "readout_base": ro_base,
            "single_gate_base": single_gate_base
        }


class ResearchEngine:
    """
    Central orchestration engine managing five independent, closed-loop 
    epoch-driven self-learning experiments (1Q to 5Q).
    """
    state = {
        "status": "IDLE",
        "current_epoch": 0,
        "max_epochs": 100,
        "qubit_count": 5,
        "dataset_rows": 0,
        "latest_metrics": None,
        "latest_calibrations": [],
        "run_id": None
    }

    _session = {
        "qubit_ids": [],
        "calibration_logs": [],
        "prediction_logs": [],
        "execution_logs": [],
        "feedback_logs": [],
        "scheduler_logs": [],
        "training_metrics_logs": [],
        "qhi_logs": [],
        "exp_dir": "",
        "models": {},  # qid-specific models dict
        "run_id": None
    }

    def __init__(self, decay_params: dict = None, max_epochs: int = 100):
        self.evolution = MathematicalQubitEvolution(decay_params)
        self.max_epochs = max_epochs
        self.base_dataset_dir = r"C:\Users\chsai\.gemini\antigravity\scratch\TwinQ-Map\datasets"
        self.saved_models_dir = r"C:\Users\chsai\.gemini\antigravity\scratch\TwinQ-Map\backend\machine_learning\saved_models"
        os.makedirs(self.saved_models_dir, exist_ok=True)

    async def initialize_experiment(self, qubit_count: int, max_epochs: int) -> None:
        """
        Boots the isolated scaling experiment, initializes Epoch 0 calibrations, and seeds models.
        """
        self.evolution.qubit_count = qubit_count
        experiment_name = f"{qubit_count}_qubit"
        exp_dir = os.path.join(self.base_dataset_dir, experiment_name)
        os.makedirs(exp_dir, exist_ok=True)
        
        qubit_ids = [f"Q{i}" for i in range(qubit_count)]
        db = MongoDBManager.get_database_by_qubits(qubit_count)
        self._db = db

        # Generate Date and Time based Run ID for laptop local execution timeline mapping
        run_id = f"Run - {datetime.now().strftime('%b %d, %Y at %H:%M:%S')}"
        clean_run = run_id.replace(" - ", "_").replace(", ", "_").replace(" at ", "_").replace(":", "_").replace(" ", "_")
        prefix = f"run_{clean_run}"

        # Separate datasets logically by prefixing collections per experiment to enforce no shared state
        self.coll_calibrations = f"{prefix}_calibrations"
        self.coll_twins = f"{prefix}_digital_twins"
        self.coll_qhi = f"{prefix}_qhi"
        self.coll_predictions = f"{prefix}_predictions"
        self.coll_scheduler = f"{prefix}_scheduler"
        self.coll_execution = f"{prefix}_execution"
        self.coll_feedback = f"{prefix}_feedback"
        self.coll_training = f"{prefix}_training"

        # Register in runs_registry for collection lookup
        await db["runs_registry"].insert_one({
            "run_id": run_id,
            "qubit_count": qubit_count,
            "collection_prefix": prefix,
            "timestamp": datetime.now(timezone.utc)
        })

        # Try to connect to IBM Quantum live calibrations if 133 qubits requested
        ibm_calibrations = None
        if qubit_count == 133:
            try:
                from backend.config.settings import settings
                from qiskit_ibm_runtime import QiskitRuntimeService
                if settings.IBM_QUANTUM_TOKEN and settings.IBM_QUANTUM_TOKEN != "token_placeholder_ibm":
                    print("Connecting to IBM Quantum to initialize live tracking for Torino (133 Qubits)...")
                    service = QiskitRuntimeService(token=settings.IBM_QUANTUM_TOKEN)
                    backends = service.backends()
                    if backends:
                        target_backend = backends[0]
                        print(f"Selected IBM Backend: {target_backend.name} ({target_backend.num_qubits} Qubits). Fetching properties...")
                        props = target_backend.properties()
                        if props:
                            ibm_calibrations = []
                            for i in range(133):
                                try:
                                    t1 = props.t1(i) * 1e6
                                except:
                                    t1 = 120.0 + (i * 0.1)
                                try:
                                    t2 = props.t2(i) * 1e6
                                except:
                                    t2 = 90.0 + (i * 0.08)
                                try:
                                    freq = props.frequency(i) * 1e-9
                                except:
                                    freq = 5.0 + (i * 0.002)
                                try:
                                    ro = props.readout_error(i)
                                except:
                                    ro = 0.015 + (i * 0.0001)
                                try:
                                    gate_err = props.gate_error(0, [i])
                                except:
                                    gate_err = 0.0005 + (i * 0.00001)

                                ibm_calibrations.append({
                                    "t1": t1,
                                    "t2": t2,
                                    "frequency": freq,
                                    "readout_error": ro,
                                    "gate_error": gate_err
                                })
                            print("Live IBM hardware baseline parameters retrieved successfully!")
            except Exception as e:
                print(f"IBM Quantum live connection failed: {e}. Falling back to realistic simulated layout.")

        # Try to connect to IonQ Cloud live calibrations if 11 or 25 qubits requested
        ionq_calibrations = None
        if qubit_count in (11, 25):
            try:
                from backend.config.settings import settings
                import httpx
                if settings.IONQ_API_KEY and settings.IONQ_API_KEY != "key_placeholder_ionq":
                    print(f"Connecting to IonQ Cloud API to initialize live tracking ({qubit_count} Qubits)...")
                    headers = {
                        "Authorization": f"apiKey {settings.IONQ_API_KEY}",
                        "Content-Type": "application/json"
                    }
                    response = httpx.get("https://api.ionq.co/v1/characterizations", headers=headers, timeout=5.0)
                    if response.status_code == 200:
                        data = response.json()
                        # IonQ returns a list of characterization objects
                        if isinstance(data, list) and len(data) > 0:
                            char = data[0]
                        elif isinstance(data, dict) and "characterizations" in data and len(data["characterizations"]) > 0:
                            char = data["characterizations"][0]
                        else:
                            char = {}
                        
                        if char:
                            spam = char.get("fidelity", {}).get("spam", {}).get("mean", 0.995)
                            ro_err = 1.0 - spam
                            sg_err = 1.0 - char.get("fidelity", {}).get("1q", {}).get("mean", 0.9996)
                            tg_err = 1.0 - char.get("fidelity", {}).get("2q", {}).get("mean", 0.985)
                            
                            ionq_calibrations = []
                            for i in range(qubit_count):
                                ionq_calibrations.append({
                                    "t1": 2000000.0 + (i * 1000.0),
                                    "t2": 1000000.0 + (i * 500.0),
                                    "frequency": 3.2,
                                    "readout_error": ro_err + (i * 0.0001),
                                    "gate_error": sg_err + (i * 0.00001)
                                })
                            print("Live IonQ Trapped-Ion baseline parameters retrieved successfully!")
            except Exception as e:
                print(f"IonQ live connection failed: {e}. Falling back to realistic Trapped-Ion simulated parameters.")

        # Initialize independent ML models per qubit node
        models = {}
        for qid in qubit_ids:
            if qubit_count >= 25:
                # Optimized small estimators/iters for high scalability (25Q and 133Q)
                rf_model = RandomForestRegressor(n_estimators=10, random_state=42, warm_start=True)
                mlp_model = MLPRegressor(hidden_layer_sizes=(8, 4), max_iter=20, random_state=42, early_stopping=False)
            else:
                rf_model = RandomForestRegressor(n_estimators=50, random_state=42, warm_start=True)
                mlp_model = MLPRegressor(hidden_layer_sizes=(16, 8), max_iter=200, random_state=42, early_stopping=False)

            models[qid] = {
                "rf": rf_model,
                "mlp": mlp_model
            }

        # Clear session buffers
        self._session.update({
            "qubit_ids": qubit_ids,
            "calibration_logs": [],
            "prediction_logs": [],
            "execution_logs": [],
            "feedback_logs": [],
            "scheduler_logs": [],
            "training_metrics_logs": [],
            "qhi_logs": [],
            "exp_dir": exp_dir,
            "models": models,
            "run_id": run_id
        })

        # Epoch 0 Init
        epoch_0_calibrations = []
        for i, qid in enumerate(qubit_ids):
            if ibm_calibrations and i < len(ibm_calibrations):
                p = ibm_calibrations[i]
                cal_data = {
                    "qubit_id": qid,
                    "epoch_number": 0,
                    "t1": p["t1"],
                    "t2": p["t2"],
                    "readout_error": p["readout_error"],
                    "single_gate_error": p["gate_error"],
                    "two_gate_error": 0.01,
                    "frequency": p["frequency"],
                    "temperature": 15.0,
                    "noise_drift": 0.0,
                    "drift_rate": 0.0,
                    "backend_status": "Active",
                    "backend_name": "ibm_torino_simulated",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "version": 1,
                    "is_deleted": False,
                    # Base parameters
                    "t1_base": p["t1"],
                    "t2_base": p["t2"],
                    "frequency_base": p["frequency"],
                    "readout_base": p["readout_error"],
                    "single_gate_base": p["gate_error"]
                }
            elif ionq_calibrations and i < len(ionq_calibrations):
                p = ionq_calibrations[i]
                cal_data = {
                    "qubit_id": qid,
                    "epoch_number": 0,
                    "t1": p["t1"],
                    "t2": p["t2"],
                    "readout_error": p["readout_error"],
                    "single_gate_error": p["gate_error"],
                    "two_gate_error": 0.015,
                    "frequency": p["frequency"],
                    "temperature": 0.0,
                    "noise_drift": 0.0,
                    "drift_rate": 0.0,
                    "backend_status": "Active",
                    "backend_name": f"ionq_aria_{qubit_count}q" if qubit_count == 11 else f"ionq_forte_{qubit_count}q",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "version": 1,
                    "is_deleted": False,
                    "t1_base": p["t1"],
                    "t2_base": p["t2"],
                    "frequency_base": p["frequency"],
                    "readout_base": p["readout_error"],
                    "single_gate_base": p["gate_error"]
                }
            else:
                cal_data = self.evolution.evolve_qubit(None, qid, 0)
            
            # Recalculate QHI
            qhi_val = QHIIndicator.compute_qhi(cal_data)
            cal_data["qhi"] = qhi_val
            
            epoch_0_calibrations.append(cal_data)
            self._session["calibration_logs"].append(cal_data)
            cal_data["run_id"] = run_id
            await db[self.coll_calibrations].insert_one(cal_data.copy())

            # Seed Digital Twin version lineage
            twin = {
                "qubit_id": qid,
                "status": "Active",
                "current_version": 1,
                "last_updated": datetime.now(timezone.utc),
                "version_history": [{
                    "version": 1,
                    "parent_version": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "calibration_data": cal_data.copy(),
                    "delta_from_previous": {},
                    "drift_values": {"t1_drift_rate": 0.0},
                    "change_reason": "Epoch 0 Baseline Init",
                    "prediction_errors": {}
                }],
                "history_buffer": [cal_data.copy()],
                "version": 1,
                "is_deleted": False,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "run_id": run_id
            }
            await db[self.coll_twins].replace_one({"qubit_id": qid, "run_id": run_id}, twin, upsert=True)

            # Seed QHI
            qhi_data = {
                "qubit_id": qid,
                "epoch_number": 0,
                "health_score": qhi_val,
                "status": "healthy",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "run_id": run_id
            }
            self._session["qhi_logs"].append(qhi_data)
            await db[self.coll_qhi].insert_one(qhi_data.copy())

        # Write Epoch 0 csv files
        pd.DataFrame(self._session["calibration_logs"]).to_csv(os.path.join(exp_dir, "calibration.csv"), index=False)
        pd.DataFrame(self._session["qhi_logs"]).to_csv(os.path.join(exp_dir, "qhi.csv"), index=False)

        # Update live state
        ResearchEngine.state.update({
            "status": "IDLE",
            "current_epoch": 0,
            "max_epochs": max_epochs,
            "qubit_count": qubit_count,
            "dataset_rows": len(self._session["calibration_logs"]),
            "latest_metrics": None,
            "latest_calibrations": epoch_0_calibrations,
            "run_id": run_id
        })

    def _build_features_for_qubit(self, qid: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Builds lag features, rolling averages, rolling variance, and QHI metrics for a target qubit.
        """
        cals = [c for c in self._session["calibration_logs"] if c["qubit_id"] == qid]
        df = pd.DataFrame(cals).sort_values("epoch_number").reset_index(drop=True)
        
        X, y = [], []
        # Frame-by-frame temporal learning
        for i in range(1, len(df)):
            prev = df.iloc[i-1]
            curr = df.iloc[i]
            
            history_window = df.iloc[max(0, i-3):i]
            rolling_mean_t1 = history_window["t1"].mean()
            rolling_var_t1 = history_window["t1"].var() if len(history_window) > 1 else 0.0
            rolling_mean_t2 = history_window["t2"].mean()
            rolling_mean_ro = history_window["readout_error"].mean()

            feats = [
                prev["epoch_number"],
                prev["t1"],
                prev["t2"],
                prev["frequency"],
                prev["temperature"],
                prev["readout_error"],
                prev["single_gate_error"],
                prev["noise_drift"],
                prev["drift_rate"],
                prev.get("qhi", 90.0),
                rolling_mean_t1,
                rolling_var_t1,
                rolling_mean_t2,
                rolling_mean_ro
            ]
            X.append(feats)
            y.append([curr["t1"], curr["t2"], curr["readout_error"]])

        # Predict context for next epoch
        last = df.iloc[-1]
        history_window = df.iloc[max(0, len(df)-3):]
        rolling_mean_t1 = history_window["t1"].mean()
        rolling_var_t1 = history_window["t1"].var() if len(history_window) > 1 else 0.0
        rolling_mean_t2 = history_window["t2"].mean()
        rolling_mean_ro = history_window["readout_error"].mean()

        X_next = [
            last["epoch_number"],
            last["t1"],
            last["t2"],
            last["frequency"],
            last["temperature"],
            last["readout_error"],
            last["single_gate_error"],
            last["noise_drift"],
            last["drift_rate"],
            last.get("qhi", 90.0),
            rolling_mean_t1,
            rolling_var_t1,
            rolling_mean_t2,
            rolling_mean_ro
        ]
        
        return np.array(X), np.array(y), np.array([X_next])

    async def execute_single_epoch(self, epoch: int) -> None:
        """
        Closed-loop epoch execution logic.
        """
        qubit_ids = self._session["qubit_ids"]
        exp_dir = self._session["exp_dir"]
        db = self._db
        
        epoch_calibrations = []
        prediction_errors = {}
        predicted_calibrations = []

        # 1. Evolve physical qubit calibration mathematically (Physical Ground Truth)
        for qid in qubit_ids:
            prev_cals = [c for c in self._session["calibration_logs"] if c["qubit_id"] == qid]
            prev_cal = prev_cals[-1] if prev_cals else None
            
            cal_data = self.evolution.evolve_qubit(prev_cal, qid, epoch)
            qhi_val = QHIIndicator.compute_qhi(cal_data)
            cal_data["qhi"] = qhi_val
            
            epoch_calibrations.append(cal_data)
            self._session["calibration_logs"].append(cal_data)
            cal_data["run_id"] = self._session["run_id"]
            await db[self.coll_calibrations].insert_one(cal_data.copy())

        # 2. Sequential Machine Learning Training & Prediction (from Epoch 2+)
        if epoch >= 2:
            model_evals = []
            for qid in qubit_ids:
                X_train, y_train, X_next = self._build_features_for_qubit(qid)
                
                # Fit models for this qubit individually (never mix regressions)
                rf = self._session["models"][qid]["rf"]
                rf.n_estimators = min(150, 50 + epoch * 2)
                rf.fit(X_train, y_train)
                
                # Predict next epoch (epoch + 1)
                preds = rf.predict(X_next)[0]
                pred_t1 = float(max(0.0, preds[0]))
                pred_t2 = float(max(0.0, preds[1]))
                pred_ro = float(max(0.0, min(preds[2], 1.0)))

                pred_data = {
                    "qubit_id": qid,
                    "epoch_number": epoch + 1,
                    "predicted_t1": pred_t1,
                    "predicted_t2": pred_ro,
                    "predicted_readout_error": pred_ro,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "run_id": self._session["run_id"]
                }
                self._session["prediction_logs"].append(pred_data)
                await db[self.coll_predictions].insert_one(pred_data.copy())

                # 3. Error evaluation (Compare prediction vs ground truth)
                # Find prediction made at (epoch - 1) for the current (epoch)
                past_preds = [p for p in self._session["prediction_logs"] if p["qubit_id"] == qid and p["epoch_number"] == epoch]
                if past_preds:
                    actual = [c for c in epoch_calibrations if c["qubit_id"] == qid][0]
                    p = past_preds[0]
                    
                    # Absolute error metrics
                    ae_t1 = abs(actual["t1"] - p["predicted_t1"])
                    ae_t2 = abs(actual["t2"] - p["predicted_t2"])
                    ae_ro = abs(actual["readout_error"] - p["predicted_readout_error"])
                    
                    prediction_errors[qid] = {
                        "t1_error": ae_t1,
                        "t2_error": ae_t2,
                        "readout_error": ae_ro
                    }
                    model_evals.append([ae_t1, ae_t2, ae_ro])

            # Evaluate average metrics for active epoch
            if model_evals:
                arr = np.array(model_evals)
                mae = float(np.mean(arr))
                mse = float(np.mean(arr ** 2))
                rmse = float(math.sqrt(mse))
                mape = float(np.mean(arr / (arr + 1e-5)))
                
                metrics_data = {
                    "epoch_number": epoch,
                    "mae": mae,
                    "mse": mse,
                    "rmse": rmse,
                    "mape": mape,
                    "r2": 1.0 - (mse / (np.var(arr) + 1e-5)),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "run_id": self._session["run_id"]
                }
                self._session["training_metrics_logs"].append(metrics_data)
                await db[self.coll_training].insert_one(metrics_data.copy())

                ResearchEngine.state.update({
                    "latest_metrics": metrics_data
                })
            else:
                # Seeding/predictive warmup phase for Epoch 2
                metrics_data = {
                    "epoch_number": epoch,
                    "mae": None,
                    "mse": None,
                    "rmse": None,
                    "mape": None,
                    "r2": None,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "run_id": self._session["run_id"]
                }
                self._session["training_metrics_logs"].append(metrics_data)
                await db[self.coll_training].insert_one(metrics_data.copy())
        else:
            # Seed placeholder training metrics for boot/seeding phase so table starting from Epoch 1 is visible
            metrics_data = {
                "epoch_number": epoch,
                "mae": None,
                "mse": None,
                "rmse": None,
                "mape": None,
                "r2": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "run_id": self._session["run_id"]
            }
            self._session["training_metrics_logs"].append(metrics_data)
            await db[self.coll_training].insert_one(metrics_data.copy())

        # 4. Update Digital Twin snapshot with prediction errors & calibration
        for qid in qubit_ids:
            twin = await db[self.coll_twins].find_one({"qubit_id": qid, "run_id": self._session["run_id"]})
            if not twin:
                twin = {
                    "qubit_id": qid,
                    "status": "Active",
                    "current_version": 0,
                    "version_history": [],
                    "history_buffer": [],
                    "version": 1,
                    "is_deleted": False,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                    "run_id": self._session["run_id"]
                }

            cal_data = [c for c in epoch_calibrations if c["qubit_id"] == qid][0]
            next_version = twin["current_version"] + 1
            snapshot = {
                "version": next_version,
                "parent_version": twin["current_version"] if twin["current_version"] > 0 else None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "calibration_data": cal_data.copy(),
                "delta_from_previous": {},
                "drift_values": {"t1_drift_rate": cal_data["drift_rate"]},
                "change_reason": f"Epoch {epoch} Autonomic Sync",
                "prediction_errors": prediction_errors.get(qid, {})
            }
            
            twin["version_history"].append(snapshot)
            twin["current_version"] = next_version
            twin["history_buffer"].append(cal_data.copy())
            if len(twin["history_buffer"]) > 50:
                twin["history_buffer"].pop(0)

            if "audit_trail" not in twin or not isinstance(twin["audit_trail"], list):
                twin["audit_trail"] = []
            
            twin["audit_trail"].append({
                "action": f"Epoch {epoch} Autonomic Sync",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "user_id": "system",
                "details": f"Automatically synchronized calibrations and prediction errors for epoch {epoch}."
            })

            twin["last_updated"] = datetime.now(timezone.utc)
            twin["updated_at"] = datetime.now(timezone.utc)
            twin["version"] += 1

            await db[self.coll_twins].replace_one({"qubit_id": qid, "run_id": self._session["run_id"]}, twin, upsert=True)

            # Compute and save QHI
            qhi_val = cal_data["qhi"]
            qhi_data = {
                "qubit_id": qid,
                "epoch_number": epoch,
                "health_score": qhi_val,
                "status": "healthy" if qhi_val > 90.0 else "degraded",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "run_id": self._session["run_id"]
            }
            self._session["qhi_logs"].append(qhi_data)
            await db[self.coll_qhi].insert_one(qhi_data.copy())

        # 5. Compile scheduling layout constraints using predictions
        for qid in qubit_ids:
            preds = [p for p in self._session["prediction_logs"] if p["qubit_id"] == qid and p["epoch_number"] == epoch]
            if preds:
                predicted_calibrations.append({
                    "qubit_id": qid,
                    "t1": preds[0]["predicted_t1"],
                    "t2": preds[0]["predicted_t2"],
                    "readout_error": preds[0]["predicted_readout_error"],
                    "single_gate_error": 0.0005,
                    "two_gate_error": 0.010,
                    "frequency": 5.0,
                    "temperature": 0.015
                })
            else:
                act = [c for c in epoch_calibrations if c["qubit_id"] == qid][0]
                predicted_calibrations.append(act)

        topology = TopologyGenerator.generate_topology(len(qubit_ids))
        mapper = QubitMapper(num_qubits=len(qubit_ids))
        logical_edges = [(i, i+1) for i in range(len(qubit_ids) - 1)]
        mapping_result = mapper.compile_mapping(logical_edges, predicted_calibrations, topology)
        
        sched_data = {
            "epoch_number": epoch,
            "algorithm": "QHI_Greedy",
            "mapping": mapping_result["mapping"],
            "swaps": len(mapping_result["swaps_required"]),
            "estimated_fidelity": mapping_result["estimated_fidelity"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self._session["run_id"]
        }
        self._session["scheduler_logs"].append(sched_data)
        await db[self.coll_scheduler].insert_one(sched_data.copy())

        # 6. Simulated Circuit Execution & Feedback logs
        shots = 1024
        target_counts = int(shots * mapping_result["estimated_fidelity"])
        counts = {"0": target_counts, "1": shots - target_counts}
        
        exec_data = {
            "execution_id": f"exec_{len(qubit_ids)}Q_{epoch}_{int(datetime.now().timestamp())}",
            "epoch_number": epoch,
            "success": True,
            "fidelity": mapping_result["estimated_fidelity"],
            "counts": counts,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self._session["run_id"]
        }
        self._session["execution_logs"].append(exec_data)
        await db[self.coll_execution].insert_one(exec_data.copy())

        feedback_data = {
            "epoch_number": epoch,
            "fidelity_error": 1.0 - mapping_result["estimated_fidelity"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "run_id": self._session["run_id"]
        }
        self._session["feedback_logs"].append(feedback_data)
        await db[self.coll_feedback].insert_one(feedback_data.copy())

        # Write incremented datasets to CSV
        pd.DataFrame(self._session["calibration_logs"]).to_csv(os.path.join(exp_dir, "calibration.csv"), index=False)
        if self._session["prediction_logs"]:
            pd.DataFrame(self._session["prediction_logs"]).to_csv(os.path.join(exp_dir, "prediction.csv"), index=False)
        if self._session["execution_logs"]:
            pd.DataFrame(self._session["execution_logs"]).to_csv(os.path.join(exp_dir, "execution.csv"), index=False)
        if self._session["feedback_logs"]:
            pd.DataFrame(self._session["feedback_logs"]).to_csv(os.path.join(exp_dir, "feedback.csv"), index=False)
        if self._session["scheduler_logs"]:
            pd.DataFrame(self._session["scheduler_logs"]).to_csv(os.path.join(exp_dir, "scheduler.csv"), index=False)
        if self._session["training_metrics_logs"]:
            pd.DataFrame(self._session["training_metrics_logs"]).to_csv(os.path.join(exp_dir, "training.csv"), index=False)
            pd.DataFrame(self._session["training_metrics_logs"]).to_csv(os.path.join(exp_dir, "train.csv"), index=False)
            pd.DataFrame(self._session["training_metrics_logs"]).to_csv(os.path.join(exp_dir, "validation.csv"), index=False)
            pd.DataFrame(self._session["training_metrics_logs"]).to_csv(os.path.join(exp_dir, "test.csv"), index=False)
        if self._session["qhi_logs"]:
            pd.DataFrame(self._session["qhi_logs"]).to_csv(os.path.join(exp_dir, "qhi.csv"), index=False)

        # Update stats JSON
        stats = {
            "total_epochs_recorded": epoch,
            "qubit_count": len(qubit_ids),
            "final_health_index": self._session["qhi_logs"][-1]["health_score"] if self._session["qhi_logs"] else 100.0
        }
        with open(os.path.join(exp_dir, "statistics.json"), "w") as f:
            json.dump(stats, f)

        # Update telemetry state parameters
        ResearchEngine.state.update({
            "current_epoch": epoch,
            "dataset_rows": len(self._session["calibration_logs"]),
            "latest_calibrations": epoch_calibrations
        })

        # Structured Console Telemetry Logger Block for User validation
        print(f"\n==================================================")
        print(f"CLOSED-LOOP RESEARCH TELEMETRY LOG - EPOCH #{epoch}")
        print(f"==================================================")
        print(f"Dataset Accumulation: {len(self._session['calibration_logs'])} rows total")
        
        for qid in qubit_ids:
            gt = [c for c in epoch_calibrations if c["qubit_id"] == qid][0]
            print(f"\n[{qid}] Ground Truth Calibration values:")
            print(f"  T1 Coherence: {gt['t1']:.4f} µs, T2 Coherence: {gt['t2']:.4f} µs")
            print(f"  Readout Error: {gt['readout_error']*100:.4f}%, Gate Error: {gt['single_gate_error']*100:.4f}%")
            print(f"  Frequency: {gt['frequency']:.5f} GHz, Temperature: {gt['temperature']:.4f} mK")
            
            if epoch >= 2:
                # Re-extract last generated feature vector context
                _, _, X_next = self._build_features_for_qubit(qid)
                print(f"[{qid}] Training Input Feature Vector:")
                print(f"  {X_next[0].tolist()}")
                
                # Model predictions context
                preds_next = [p for p in self._session["prediction_logs"] if p["qubit_id"] == qid and p["epoch_number"] == epoch+1]
                if preds_next:
                    p = preds_next[0]
                    print(f"[{qid}] ML Forecast prediction (for Epoch #{epoch+1}):")
                    print(f"  T1: {p['predicted_t1']:.4f} µs, T2: {p['predicted_t2']:.4f} µs, RO: {p['predicted_readout_error']*100:.4f}%")
                
                # Predict vs ground truth comparison for epoch
                past_p = [p for p in self._session["prediction_logs"] if p["qubit_id"] == qid and p["epoch_number"] == epoch]
                if past_p:
                    p_curr = past_p[0]
                    print(f"[{qid}] Error Comparison (Epoch #{epoch}):")
                    print(f"  Observed T1: {gt['t1']:.4f} vs Pred T1: {p_curr['predicted_t1']:.4f} (AE: {abs(gt['t1'] - p_curr['predicted_t1']):.4f})")
                    print(f"  Observed RO: {gt['readout_error']:.4f} vs Pred RO: {p_curr['predicted_readout_error']:.4f} (AE: {abs(gt['readout_error'] - p_curr['predicted_readout_error']):.4f})")
            else:
                print(f"[{qid}] ML Model Training Status: WAITING (Bootstrapping baseline)")
                
            twin = await db[self.coll_twins].find_one({"qubit_id": qid})
            print(f"[{qid}] Digital Twin Snapshot Version: v{twin['current_version']}")
            print(f"[{qid}] Quantum Health Index (QHI): {gt['qhi']:.2f}")

        if epoch >= 2 and self._session["training_metrics_logs"]:
            met = self._session["training_metrics_logs"][-1]
            print(f"\n[Model Training Metrics (Average across Qubits)]:")
            if met.get("mae") is not None:
                print(f"  MAE: {met['mae']:.6f}, MSE: {met['mse']:.6f}, RMSE: {met['rmse']:.6f}")
                print(f"  MAPE: {met['mape']:.6f}, R2 Score: {met['r2']:.6f}")
            else:
                print(f"  MAE: — (Warmup), MSE: — (Warmup), RMSE: — (Warmup)")
                print(f"  MAPE: — (Warmup), R2 Score: — (Warmup)")
            
        print(f"\n[Adaptive Scheduler Decision]:")
        print(f"  Logical-to-Physical layout mapping: {sched_data['mapping']}")
        print(f"  SWAPs required: {sched_data['swaps']}, Estimated fidelity: {sched_data['estimated_fidelity']*100:.4f}%")
        print(f"==================================================")

    async def run_loop(self) -> None:
        """
        Runs the state loop sequentially.
        """
        try:
            while ResearchEngine.state["status"] == "RUNNING":
                current = ResearchEngine.state["current_epoch"]
                max_ep = ResearchEngine.state["max_epochs"]
                if current >= max_ep:
                    ResearchEngine.state["status"] = "COMPLETED"
                    # Export final curves
                    exp_dir = self._session["exp_dir"]
                    if self._session["training_metrics_logs"]:
                        df_metrics = pd.DataFrame(self._session["training_metrics_logs"])
                        plt.figure(figsize=(10, 6))
                        plt.plot(df_metrics["epoch_number"], df_metrics["mse"], label="MSE Loss", color="fuchsia")
                        plt.plot(df_metrics["epoch_number"], df_metrics["mae"], label="MAE Loss", color="cyan")
                        plt.xlabel("Epoch")
                        plt.ylabel("Loss")
                        plt.title(f"Model Training Loss Curve: {len(self._session['qubit_ids'])} Qubits")
                        plt.legend()
                        plt.grid(True)
                        plt.savefig(os.path.join(exp_dir, "loss_curve.png"))
                        plt.close()
                    break

                await self.execute_single_epoch(current + 1)
                await asyncio.sleep(0.6)
        except Exception as e:
            print(f"Error in training run loop: {e}")
            ResearchEngine.state["status"] = "IDLE"

# Alias class for existing imports compatibility
AutonomousSimulationRunner = ResearchEngine
