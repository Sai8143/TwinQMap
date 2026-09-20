import networkx as nx
from typing import Dict, List, Tuple

class QubitRouter:
    """
    Qubit Router simulating routing paths and generating list of required SWAP gate insertions.
    """

    @staticmethod
    def generate_routing_swaps(
        logical_edge: Tuple[int, int],
        physical_graph: nx.Graph,
        mapping: Dict[int, int]
    ) -> List[Tuple[int, int]]:
        """
        Generates the sequence of SWAP gates required to make two interacting qubits adjacent.
        
        Args:
            logical_edge: Tuple (u_l, v_l) of interacting logical qubits.
            physical_graph: Coupling topology of physical processor.
            mapping: Logical-to-physical qubit mapping.
            
        Returns:
            List of physical SWAP gate pairs, e.g. [(0, 1), (1, 2)].
        """
        phys_u = mapping.get(logical_edge[0])
        phys_v = mapping.get(logical_edge[1])
        
        if phys_u is None or phys_v is None:
            return []
            
        try:
            # Shortest path: [p_u, p_1, ..., p_v]
            path = nx.shortest_path(physical_graph, source=phys_u, target=phys_v)
        except nx.NetworkXNoPath:
            return []

        # If already adjacent, no SWAPs needed
        if len(path) <= 2:
            return []

        swaps = []
        # Bring path[0] next to path[-1]
        # Example: path is [0, 1, 2]. SWAP (0, 1) makes node 1 hold logical 0.
        # Now logical 0 (on 1) and logical 1 (on 2) are adjacent.
        for i in range(len(path) - 2):
            swaps.append((path[i], path[i+1]))
            
        return swaps
