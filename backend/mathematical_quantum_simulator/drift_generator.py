class DriftGenerator:
    """
    Drift generator computing rate of parameter change per unit time.
    Provides utility calculations for logging coherence and readout drift rates.
    """

    @staticmethod
    def calculate_drift_rate(prev_value: float, curr_value: float, elapsed_hours: float) -> float:
        """
        Computes the drift rate per hour.
        
        Equation:
          DriftRate = (curr_value - prev_value) / elapsed_hours
        """
        if elapsed_hours <= 0.0:
            return 0.0
        return (curr_value - prev_value) / elapsed_hours
