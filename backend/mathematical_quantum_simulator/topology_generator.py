from typing import Any, Dict, List
import networkx as nx
import numpy as np

class TopologyGenerator:
    """
    Topology generator configuring physical coupling layouts of NISQ quantum processors.
    Supports layouts for 1Q (Single), 2Q (Linear), 3Q (Triangle), 4Q (Square), and 5Q (Hybrid).
    """

    @staticmethod
    def generate_topology(num_qubits: int) -> Dict[str, Any]:
        """
        Creates graph coupling connectivity objects for the specified physical qubit configuration.
        
        Args:
            num_qubits: Qubit count, 1 to 5.
            
        Returns:
            Dict containing:
              - 'adjacency_matrix': np.ndarray representation
              - 'adjacency_list': Dict[int, List[int]]
              - 'edge_list': List[tuple[int, int]]
              - 'graph': nx.Graph object
        """
        graph = nx.Graph()
        graph.add_nodes_from(range(num_qubits))

        # Add edges based on configured layout topologies
        if num_qubits > 5:
            # Dynamically build a linear chain with periodic boundaries (ring topology)
            for i in range(num_qubits - 1):
                graph.add_edge(i, i + 1)
            graph.add_edge(num_qubits - 1, 0)
        elif num_qubits == 2:
            graph.add_edge(0, 1)
        elif num_qubits == 3:
            graph.add_edges_from([(0, 1), (1, 2), (2, 0)])
        elif num_qubits == 4:
            graph.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0)])
        elif num_qubits == 5:
            # Hybrid coupling ring with cross-talk diagonals
            graph.add_edges_from([
                (0, 1), (1, 2), (2, 3), (3, 4), (4, 0),
                (0, 2), (1, 3), (2, 4)
            ])

        # Extract matrices and lists
        adjacency_matrix = nx.to_numpy_array(graph, dtype=int)
        edge_list = list(graph.edges())
        
        adjacency_list = {}
        for node in graph.nodes():
            adjacency_list[int(node)] = [int(neighbor) for neighbor in graph.neighbors(node)]

        return {
            "adjacency_matrix": adjacency_matrix,
            "adjacency_list": adjacency_list,
            "edge_list": edge_list,
            "graph": graph
        }
