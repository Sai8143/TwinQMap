import networkx as nx
from backend.scheduler.algorithms.greedy import QHIGreedyMappingAlgorithm

def test_greedy_mapping_avoids_unhealthy_qubits():
    """
    Test case: Verify that greedy mapping puts nodes on healthier qubits.
    """
    # Create logical circuit interaction graph: 3 qubits in a line (0-1-2)
    # Node 1 has degree 2 (highest), nodes 0 and 2 have degree 1.
    g_log = nx.Graph()
    g_log.add_edges_from([(0, 1), (1, 2)])
    
    # Create physical processor coupling graph: 5 qubits in line
    g_phys = nx.Graph()
    g_phys.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4)])
    
    # Qubit health scores: Q2 is highly unhealthy (0.3), others are healthy
    health_scores = {
        0: 0.95,
        1: 0.99,
        2: 0.30,  # Unhealthy!
        3: 0.92,
        4: 0.88
    }
    
    algo = QHIGreedyMappingAlgorithm()
    mapping = algo.compute_mapping(g_log, g_phys, health_scores)
    
    # Verification
    # Mapping must include logical keys 0, 1, 2
    assert len(mapping) == 3
    assert set(mapping.keys()) == {0, 1, 2}
    
    # The highest degree logical qubit (1) should be mapped to the healthiest physical qubit (1)
    assert mapping[1] == 1
    
    # Q2 is unhealthy (0.30), so none of our active logical qubits should map to physical qubit 2
    # Healthy qubits are: 1 (0.99), 0 (0.95), 3 (0.92), 4 (0.88).
    # Since we sort physical qubits by health, we pick: 1, 0, 3 (order of health).
    # Physical 2 should not be in the values of mapping.
    assert 2 not in mapping.values()
    assert mapping[0] in [0, 3]
    assert mapping[2] in [0, 3]
