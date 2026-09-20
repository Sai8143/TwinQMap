# Qubit Health Index (QHI) Weighted Indicator

This document describes the Qubit Health Index formulation.

## 1. QHI Weighted Evaluation Formula
QHI evaluates hardware quality indices by combining coherence, readout, and gate fidelities:

$$\text{QHI}(v_p) = w_r \cdot (1 - E_R) + w_1 \cdot \min\left(1.0, \frac{T_1}{T_{1,\text{thresh}}}\right) + w_2 \cdot \min\left(1.0, \frac{T_2}{T_{2,\text{thresh}}}\right) + w_g \cdot (1 - E_G)$$

where:
- $E_R$ is Readout measurement error.
- $E_G$ is Single-qubit gate error.
- $T_1$ and $T_2$ are relaxation and dephasing lifetimes.
- $T_{1,\text{thresh}} = 50.0\ \mu\text{s}$, $T_{2,\text{thresh}} = 30.0\ \mu\text{s}$ are baseline constants.
- weights $w_r = 0.3$, $w_1 = 0.2$, $w_2 = 0.2$, $w_g = 0.3$ sum to 1.0.

---

## 2. IEEE-Style Algorithm Pseudocode
```text
============================================================================
Algorithm: EvaluateQHI(calibrationData, thresholds, weights)
============================================================================
Input:  calibrationData = { t1, t2, readout_error, single_gate_error }
        thresholds = { t1_min, t2_min }
        weights = { w_readout, w_t1, w_t2, w_gate }
Output: QHI health score in [0.0, 1.0]
----------------------------------------------------------------------------
1:  t1_norm <- Minimum(1.0, calibrationData.t1 / thresholds.t1_min)
2:  t2_norm <- Minimum(1.0, calibrationData.t2 / thresholds.t2_min)
3:  
4:  readout_fidelity <- Maximum(0.0, 1.0 - calibrationData.readout_error)
5:  gate_fidelity <- Maximum(0.0, 1.0 - calibrationData.single_gate_error)
6:  
7:  qhi <- weights.w_readout * readout_fidelity 
8:       + weights.w_t1 * t1_norm 
9:       + weights.w_t2 * t2_norm 
10:      + weights.w_gate * gate_fidelity
11: 
12: Return Maximum(0.0, Minimum(1.0, qhi))
============================================================================
```
