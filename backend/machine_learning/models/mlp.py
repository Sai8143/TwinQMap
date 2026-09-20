from typing import Any
from sklearn.neural_network import MLPRegressor
from backend.machine_learning.models.base import BasePredictiveModel

class QubitDecayMLP(BasePredictiveModel):
    """
    Multi-layer Perceptron Neural Network predicting multi-target physical qubit calibrations.
    """

    def __init__(self, hidden_layer_sizes: tuple = (64, 32), max_iter: int = 500, model_version: str = "v1.0.0"):
        super().__init__(model_version)
        self.model = MLPRegressor(
            hidden_layer_sizes=hidden_layer_sizes,
            max_iter=max_iter,
            random_state=42,
            early_stopping=True
        )

    def fit(self, X: Any, y: Any) -> None:
        """
        Fits the neural network regressor.
        """
        self.model.fit(X, y)

    def predict(self, X: Any) -> Any:
        """
        Predicts future calibration parameters (T1, T2, readout error).
        """
        return self.model.predict(X)
