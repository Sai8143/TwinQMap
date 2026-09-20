# Mathematical Quantum Simulator Engine

This document details the equations and pseudo-codes driving the hardware simulator.

## 1. Coherence, Readout, and Gate Decay Formulas
- **Longitudinal Relaxation Decay ($T_1$)**:
  $$T_1(t) = T_{1,0} \cdot e^{-\alpha_{T1} \cdot t}$$
  where $\alpha_{T1} = 0.002$ is the decay constant, $T_{1,0}$ is baseline relaxation time, and $t$ is the elapsed epoch time index.
- **Transverse Dephasing Decay ($T_2$)**:
  $$T_2(t) = T_{2,0} \cdot e^{-\beta_{T2} \cdot t}$$
  where $\beta_{T2} = 0.003$ is the decay constant, $T_{2,0}$ is baseline dephasing time, and $t$ is the elapsed epoch time index.
- **Readout Measurement Error Rate ($E_R$)**:
  $$E_R(t) = E_{R,0} + \sigma_{\text{drift}} \cdot t + \mathcal{N}(0, \sigma^2)$$
  where $E_{R,0}$ is the baseline readout error rate, $\sigma_{\text{drift}} = 0.0001$ is linear drift factor, and $\mathcal{N}$ represents Gaussian noise.
- **Single-Qubit Gate Error Growth ($E_{1Q}$)**:
  $$E_{1Q}(t) = E_{1Q,0} \cdot \left(\frac{T_{1,0}}{T_1(t)}\right) + \text{noise}$$
  The gate error grows inversely proportional to the relaxation time decay.

---

## 2. IEEE-Style Algorithm Pseudocode
```text
============================================================================
Algorithm: GenerateCalibrationEpochs(QubitList, baselineParameters, MaxEpochs)
============================================================================
Input:  QubitList = [Q0, Q1, ..., QN]
        baselineParameters = { Q0: [T1_0, T2_0, ER_0, EG_0], ... }
        MaxEpochs = 100
Output: CalibrationHistoryRecords
----------------------------------------------------------------------------
1:  CalibrationHistoryRecords <- Empty List
2:  For epoch <- 0 To MaxEpochs - 1 Do
3:      For Each qubit in QubitList Do
4:          Let params = baselineParameters[qubit]
5:          t1 <- params.T1_0 * exp(-0.002 * epoch)
6:          t2 <- params.T2_0 * exp(-0.003 * epoch)
7:          noise <- SampleNormalDistribution(mean=0, std=0.0005)
8:          readout_err <- params.ER_0 + (0.0001 * epoch) + noise
9:          single_gate_err <- params.EG_0 * (params.T1_0 / t1) + noise
10:         Append [epoch, qubit, t1, t2, readout_err, single_gate_err] 
11:                To CalibrationHistoryRecords
12:     End For
13: End For
14: Return CalibrationHistoryRecords
============================================================================
```
