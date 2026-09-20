from abc import ABC, abstractmethod
from typing import Any, Dict, List
import networkx as nx

class BaseQubitMappingAlgorithm(ABC):
    """
    Abstract Base Class for Qubit mapping and routing algorithms.
    
    ============================================================================
    MATHEMATICAL FORMULATION: OPTIMIZED QUBIT MAPPING
    ============================================================================
    Given:
      - A logical circuit coupling graph G_L = (V_L, E_L), where V_L represents
        logical qubits and E_L represents two-qubit gate interactions.
      - A physical processor coupling graph G_P = (V_P, E_P), where V_P represents
        physical qubits and E_P represents available links.
      - A set of forecasted Qubit Health Indices QHI(v_p) for all v_p in V_P.
      
    Objective:
      Find an injective mapping function M: V_L -> V_P that maximizes layout health
      and minimizes routing distance (SWAP cost):
      
      Maximize Objective(M) = w_h * [ Sum_{v_l in V_L} ( QHI(M(v_l)) ) / |V_L| ]
                              - w_d * [ Sum_{(u_l, v_l) in E_L} ( dist_{G_P}(M(u_l), M(v_l)) - 1 ) ]
                              
      where:
        - dist_{G_P}(p_1, p_2) is the shortest path distance between physical qubits p_1 and p_2.
        - w_h, w_d are weights parameters (e.g. w_h = 0.6, w_d = 0.4).

    ============================================================================
    IEEE-STYLE PSEUDOCODE: QHI-AWARE MAPPING (GREEDY HEURISTIC)
    ============================================================================
    Algorithm: QHI_Greedy_Mapping(G_L, G_P, QHI)
    ----------------------------------------------------------------------------
    Input:  G_L (Logical graph), G_P (Physical graph), QHI (list of health scores)
    Output: Mapping dictionary M: V_L -> V_P
    ----------------------------------------------------------------------------
    1: Sort logical qubits v_l in V_L by degree in G_L descending -> Sorted_V_L
    2: Sort physical qubits v_p in V_P by health QHI(v_p) descending -> Sorted_V_P
    3: Initialize M <- empty mapping
    4: for each logical qubit u_l in Sorted_V_L do:
    5:     if M is empty then:
    6:         Select best physical qubit p_0 <- Sorted_V_P[0]
    7:         M[u_l] <- p_0
    8:         Remove p_0 from Sorted_V_P
    9:     else:
    10:        Find an unmapped physical qubit p_x adjacent to already mapped physical qubits,
               minimizing distance cost to logical neighbors of u_l, and maximizing QHI(p_x).
    11:        M[u_l] <- p_x
    12:        Remove p_x from Sorted_V_P
    13: return M
    ----------------------------------------------------------------------------

    ============================================================================
    COMPLEXITY ANALYSIS
    ============================================================================
    Time Complexity:
      - Sorting: O(|V_L| log |V_L| + |V_P| log |V_P|)
      - Placement Loop: O(|V_L| * |V_P|)
      - Total: O(|V_L| * |V_P| + |V_P| log |V_P|)
    Space Complexity:
      - O(|V_L|) to store mapping configurations.
    """

    @abstractmethod
    def get_algorithm_name(self) -> str:
        """
        Returns the unique algorithm identifier string.
        """
        pass

    @abstractmethod
    def compute_mapping(
        self,
        logical_graph: nx.Graph,
        physical_graph: nx.Graph,
        qubit_health_indices: Dict[int, float]
    ) -> Dict[int, int]:
        """
        Computes the mapping configuration mapping logical qubit IDs -> physical qubit IDs.
        
        Args:
            logical_graph: Graph of logical qubit interactions (NetworkX).
            physical_graph: Coupling topology of the target processor (NetworkX).
            qubit_health_indices: Map from physical qubit indices -> QHI scores (0.0 - 1.0).
            
        Returns:
            Dictionary mapping logical index -> physical index (e.g. {0: 3, 1: 0, 2: 1}).
        """
        pass
