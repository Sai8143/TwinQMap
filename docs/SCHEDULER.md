# Adaptive Qubit Scheduler

This document details the greedy scheduling algorithm and path routing costs.

## 1. Mapping and Routing Formulas
- **Routing Distance Cost**:
  $$\text{RoutingCost}(M) = \sum_{(u, v) \in E_L} \left(\text{shortest\_path}(M(u), M(v)) - 1\right)$$
  Each path step greater than 1 represents a SWAP gate insertion required to make interacting logical qubits adjacent on the physical coupling graph.
- **Layout Success Estimator**:
  $$\text{LayoutError}(M) = 1.0 - \prod_{q \in \text{active}} \left(1.0 - E_R(q)\right)$$
- **Fidelity Score**:
  $$\text{Fidelity}(M) = (1.0 - \text{LayoutError}(M)) \cdot e^{-0.05 \cdot \text{RoutingCost}(M)}$$

---

## 2. IEEE-Style Algorithm Pseudocode
```text
============================================================================
Algorithm: ComputeQHIGreedyMapping(G_logical, G_physical, QHI_Scores)
============================================================================
Input:  G_logical = Graph of circuit gates interactions
        G_physical = Graph of hardware couplings
        QHI_Scores = { physical_node: score }
Output: mapping = { logical_node: physical_node }
----------------------------------------------------------------------------
1:  mapping <- Empty Map
2:  Sort logical nodes in descending order of degrees
3:  Sort physical nodes in descending order of QHI scores
4:  
5:  For Each log_node in sorted_logical_nodes Do
6:      If mapping is empty Then
7:          Assign log_node -> highest QHI physical node
8:      Else
9:          Find physical neighbors of already mapped nodes
10:         Pick neighbor node with highest QHI score which is unmapped
11:         Assign log_node -> selected physical node
12:     End If
13: End For
14: Return mapping
============================================================================
```
