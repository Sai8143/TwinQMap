from abc import ABC, abstractmethod
from typing import Any
import joblib
from backend.core.logging import training_logger

class BasePredictiveModel(ABC):
    """
    Abstract Base Class for time-varying NISQ calibration predictive models.
    Supports standard training, inference, and serialization actions.
    """

    def __init__(self, model_version: str = "1.0.0"):
        self.model_version = model_version
        self.model = None

    @abstractmethod
    def fit(self, X: Any, y: Any) -> None:
        """
        Trains the machine learning model on custom feature datasets.
        """
        pass

    @abstractmethod
    def predict(self, X: Any) -> Any:
        """
        Predicts physical qubit health or calibration parameters.
        """
        pass

    def save(self, filepath: str) -> None:
        """
        Serializes the trained model object using Joblib.
        """
        if self.model is None:
            training_logger.warning("Attempted to save an untrained model.")
        training_logger.info(f"Saving model version {self.model_version} to {filepath}...")
        joblib.dump(self.model, filepath)

    def load(self, filepath: str) -> None:
        """
        Deserializes the model object from local storage.
        """
        training_logger.info(f"Loading model from {filepath}...")
        self.model = joblib.load(filepath)
