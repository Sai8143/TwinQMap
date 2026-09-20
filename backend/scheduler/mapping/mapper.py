import networkx as nx
from typing import Dict, List, Any, Tuple
from backend.scheduler.algorithms.greedy import QHIGreedyMappingAlgorithm
from backend.scheduler.cost.evaluator import CostEvaluator
from backend.scheduler.routing.router import QubitRouter
from backend.scheduler.health.qhi import QHIIndicator

class QubitMapper:
    """
    Qubit Mapper orchestrating layout compilation, QHI evaluations,
    routing cost analyses, and compilation fidelity estimations.
    """

    def __init__(self, num_qubits: int = 5):
        self.num_qubits = num_qubits
        self.algorithm = QHIGreedyMappingAlgorithm()

    def compile_mapping(
        self,
        logical_edges: List[Tuple[int, int]],
        calibrations: List[Dict[str, Any]],
        physical_topology: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculates optimized qubit mapping, inserts SWAP routing gates,
        and estimates overall circuit execution cost.
        """
        # 1. Build logical graph
        g_log = nx.Graph()
        g_log.add_edges_from(logical_edges)
        # Ensure all nodes are represented (e.g. up to circuit width)
        logical_nodes = list(g_log.nodes())
        if not logical_nodes:
            logical_nodes = [0]
            g_log.add_node(0)

        # 2. Get physical graph
        g_phys = physical_topology["graph"]

        # 3. Calculate QHI for each physical qubit
        qhi_scores = {}
        cal_map = {}
        for c in calibrations:
            try:
                # Expecting Q0, Q1 etc. Extract index.
                q_idx = int(c["qubit_id"].replace("Q", ""))
            except ValueError:
                q_idx = 0
            
            qhi = QHIIndicator.compute_qhi(c)
            qhi_scores[q_idx] = qhi
            cal_map[q_idx] = c

        # Ensure all physical graph nodes have a default QHI if not calibrated
        for node in g_phys.nodes():
            if node not in qhi_scores:
                qhi_scores[node] = 0.5

        # 4. Run mapping algorithm
        mapping = self.algorithm.compute_mapping(g_log, g_phys, qhi_scores)

        # 5. Evaluate routing SWAPs
        all_swaps = []
        for edge in logical_edges:
            swaps = QubitRouter.generate_routing_swaps(edge, g_phys, mapping)
            all_swaps.extend(swaps)

        # 6. Evaluate costs
        routing_cost = CostEvaluator.calculate_routing_cost(logical_edges, g_phys, mapping)
        layout_error = CostEvaluator.evaluate_layout_error(list(mapping.values()), cal_map)

        # Estimate fidelity = (1.0 - layout_error) * exp(-0.1 * routing_cost)
        import numpy as np
        fidelity = (1.0 - layout_error) * np.exp(-0.05 * routing_cost)
        fidelity = float(max(0.0, min(1.0, fidelity)))

        return {
            "mapping": {str(k): int(v) for k, v in mapping.items()},
            "qhi_scores": {f"Q{k}": float(v) for k, v in qhi_scores.items()},
            "swaps_required": [[int(u), int(v)] for u, v in all_swaps],
            "routing_cost": float(routing_cost),
            "estimated_fidelity": fidelity,
            "success_rate": float(1.0 - layout_error)
        }
