# Calibration Engine

The Calibration Engine models time-varying decay characteristics of NISQ physical processors.

## Drift Calculations
When a new calibration epoch $T_n$ is synchronized, the engine matches it against the previous epoch $T_{n-1}$ to determine hourly drift values:

$$DriftRate = \frac{T1(T_n) - T1(T_{n-1})}{T_n - T_{n-1}}$$

$$NoiseDrift = ReadoutError(T_n) - ReadoutError(T_{n-1})$$

These computations are stored inside `CalibrationHistory` and mapped to the Digital Twin commit lineage.

## Deterministic Noise Model
The simulator models drift parameters using:
1. **Exponential Coherence Decay**:
   $$T_1(t) = T_{1,0} \cdot e^{-\alpha t}$$
   $$T_2(t) = T_{2,0} \cdot e^{-\beta t}$$
2. **Linear Frequency Drift**:
   $$f(t) = f_0 + \gamma t$$
3. **Gaussian Readout Noise**:
   $$E_R(t) = E_{R,0} + \delta \cdot \text{Normal}(0, 1) \text{ (with reproducible seed)}$$
