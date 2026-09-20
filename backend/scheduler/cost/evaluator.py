import networkx as nx
from typing import Dict, List, Any

class CostEvaluator:
    """
    Evaluator calculating path routing distances (SWAPs) and physical gate/readout errors.
    """

    @staticmethod
    def calculate_routing_cost(
        logical_edges: List[tuple],
        physical_graph: nx.Graph,
        mapping: Dict[int, int]
    ) -> float:
        """
        Calculates distance-based routing cost. Each additional step in the shortest path
        represents necessary SWAP gates insertion.
        
        Equation:
          Cost = Sum_{ (u, v) in E_logical } ( shortest_path_length(M(u), M(v)) - 1 )
        """
        cost = 0.0
        for u, v in logical_edges:
            phys_u = mapping.get(u)
            phys_v = mapping.get(v)
            
            if phys_u is None or phys_v is None:
                continue
                
            try:
                # Find length of shortest path in physical layout coupling
                path_len = nx.shortest_path_length(physical_graph, source=phys_u, target=phys_v)
                cost += float(path_len - 1)
            except nx.NetworkXNoPath:
                # Disconnected physical node represents infinite cost
                cost += 999.0
        return cost

    @staticmethod
    def evaluate_layout_error(
        active_qubits: List[int],
        calibrations: Dict[int, Dict[str, Any]]
    ) -> float:
        """
        Estimates total error expectation of the selected mapping layout.
        
        Equation:
          TotalError = 1.0 - Product_{ q in active } ( 1.0 - ReadoutError(q) )
        """
        success_prob = 1.0
        for phys_idx in active_qubits:
            cal = calibrations.get(phys_idx, {})
            readout_err = cal.get("readout_error", 0.02)
            success_prob *= (1.0 - readout_err)
        return float(1.0 - success_prob)
