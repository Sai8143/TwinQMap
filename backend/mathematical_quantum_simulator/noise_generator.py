import numpy as np

class NoiseGenerator:
    """
    Noise generator providing deterministic Gaussian readout and gate noise drifts.
    Uses a reproducible seed to ensure manually verifiable outputs.
    """

    def __init__(self, seed: int = 42):
        self.rng = np.random.default_rng(seed=seed)

    def generate_readout_noise(self, scale: float = 0.0005) -> float:
        """
        Generates a deterministic Gaussian noise perturbation for readout calibration.
        
        Equation:
          Noise = Normal(mean=0, std=scale)
        """
        return float(self.rng.normal(loc=0.0, scale=scale))

    def generate_gate_noise(self, scale: float = 0.00002) -> float:
        """
        Generates a deterministic Gaussian noise perturbation for single/two qubit gates.
        """
        return float(self.rng.normal(loc=0.0, scale=scale))
