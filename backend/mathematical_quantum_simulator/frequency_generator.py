class FrequencyGenerator:
    """
    Frequency generator modeling linear qubit operating frequency drifts.
    """

    @staticmethod
    def generate_frequency(base_freq: float, epoch: int, linear_factor: float = 0.0002) -> float:
        """
        Calculates frequency drift over training epochs.
        
        Equation:
          Frequency(epoch) = base_freq + (linear_factor * epoch)
        """
        return base_freq + (linear_factor * epoch)
