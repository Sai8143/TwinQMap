import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Dict, Any, List

class QubitFeatureEngineer:
    """
    Feature engineering pipeline for NISQ calibration time-series datasets.
    Prepares lag features, rolling windows, and normalizes tabular data.
    """

    def __init__(self, rolling_window: int = 5):
        self.rolling_window = rolling_window
        self.scaler = StandardScaler()

    def build_features(self, df: pd.DataFrame, is_training: bool = True) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """
        Processes historical calibration logs to extract time-series features.
        
        Features:
          - Lagged values (T1, T2, Readout error)
          - Rolling mean and std deviation over self.rolling_window epochs
          - Epoch number, Frequency, and Temperature
        """
        # Ensure correct sorting
        df = df.sort_values(by=["qubit_id", "epoch_number"]).copy()
        
        feature_cols = []
        
        # 1. Create rolling window features
        for col in ["t1", "t2", "readout_error", "single_gate_error", "two_gate_error"]:
            df[f"{col}_roll_mean"] = df.groupby("qubit_id")[col].transform(lambda x: x.rolling(self.rolling_window, min_periods=1).mean())
            df[f"{col}_roll_std"] = df.groupby("qubit_id")[col].transform(lambda x: x.rolling(self.rolling_window, min_periods=1).std().fillna(0.0))
            feature_cols.extend([f"{col}_roll_mean", f"{col}_roll_std"])

        # 2. Lag features
        for col in ["t1", "t2", "readout_error"]:
            df[f"{col}_lag_1"] = df.groupby("qubit_id")[col].shift(1).bfill()
            feature_cols.append(f"{col}_lag_1")

        # Base features
        feature_cols.extend(["epoch_number", "frequency", "temperature"])
        
        X = df[feature_cols].values
        
        # Target: predict T1, T2, and Readout error at next state
        y = df[["t1", "t2", "readout_error"]].values

        if is_training:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)

        return X_scaled, y, feature_cols

    def get_scaler_params(self) -> Dict[str, Any]:
        """
        Returns scaler parameters for saving/reloading.
        """
        return {
            "mean": self.scaler.mean_.tolist() if hasattr(self.scaler, "mean_") else [],
            "var": self.scaler.var_.tolist() if hasattr(self.scaler, "var_") else []
        }
