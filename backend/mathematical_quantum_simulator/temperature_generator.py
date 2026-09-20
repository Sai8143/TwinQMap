import numpy as np

class TemperatureGenerator:
    """
    Temperature generator modeling cryostat temperature fluctuations.
    """

    def __init__(self, base_temp: float = 0.015):
        self.base_temp = base_temp

    def generate_temperature(self, epoch: int) -> float:
        """
        Calculates temperature drift over epochs.
        Uses a deterministic sinusoidal function to model dilution refrigerator temperature oscillations.
        
        Equation:
          Temperature(epoch) = base_temp + 0.001 * sin(epoch * pi / 10)
        """
        # Periodic oscillation representing cryostat cycles
        oscillation = 0.001 * np.sin(epoch * np.pi / 10.0)
        return self.base_temp + oscillation
