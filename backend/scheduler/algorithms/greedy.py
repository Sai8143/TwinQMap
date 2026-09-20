from typing import Dict
import networkx as nx
from backend.scheduler.algorithms.base import BaseQubitMappingAlgorithm

class QHIGreedyMappingAlgorithm(BaseQubitMappingAlgorithm):
    """
    Greedy layout mapping algorithm that places high-degree logical nodes
    on high-health physical qubits.
    """

    def get_algorithm_name(self) -> str:
        return "QHI_Greedy"

    def compute_mapping(
        self,
        logical_graph: nx.Graph,
        physical_graph: nx.Graph,
        qubit_health_indices: Dict[int, float]
    ) -> Dict[int, int]:
        """
        Implementation of greedy mapping algorithm.
        """
        # Sort logical qubits by degree (most connected first)
        sorted_logical = sorted(
            logical_graph.nodes(),
            key=lambda x: logical_graph.degree(x),
            reverse=True
        )
        
        # Sort physical qubits by health (highest health first)
        sorted_physical = sorted(
            qubit_health_indices.keys(),
            key=lambda x: qubit_health_indices[x],
            reverse=True
        )
        
        mapping = {}
        for i, log_q in enumerate(sorted_logical):
            if i < len(sorted_physical):
                mapping[log_q] = sorted_physical[i]
                
        return mapping
