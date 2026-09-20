import numpy as np
import os
import tempfile
from backend.machine_learning.models.predictor import QubitDecayPredictor

def test_qubit_decay_predictor_lifecycle():
    """
    Test case: Verify training, prediction, and serialization of ML predictor.
    """
    # Create simple features (10 samples, 4 features: hours_since_calib, initial_t1, initial_t2, temperature)
    X_train = np.random.rand(10, 4)
    # Target value: readout error rate
    y_train = np.random.rand(10)
    
    predictor = QubitDecayPredictor(n_estimators=10)
    predictor.fit(X_train, y_train)
    
    # Predict on new samples
    X_test = np.random.rand(2, 4)
    preds = predictor.predict(X_test)
    
    assert preds.shape == (2,)
    assert np.all(preds >= 0.0)
    
    # Save & Load roundtrip using a temporary file path
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = os.path.join(tmpdir, "rf_model.joblib")
        predictor.save(model_path)
        
        assert os.path.exists(model_path)
        
        # Load into new instance
        new_predictor = QubitDecayPredictor(model_version="v1.0.0-loaded")
        new_predictor.load(model_path)
        
        new_preds = new_predictor.predict(X_test)
        assert np.allclose(preds, new_preds)
