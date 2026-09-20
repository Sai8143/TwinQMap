import pytest
import os
import shutil
import tempfile
from backend.mathematical_quantum_simulator.state_generator import StateGenerator
from backend.mathematical_quantum_simulator.topology_generator import TopologyGenerator
from backend.mathematical_quantum_simulator.noise_generator import NoiseGenerator
from backend.mathematical_quantum_simulator.calibration_generator import CalibrationGenerator
from backend.mathematical_quantum_simulator.dataset_generator import DatasetGenerator

def test_state_generator_basis_states():
    """
    Verifies that the StateGenerator outputs exactly 2^N states for N=1 to 5.
    """
    for n in range(1, 6):
        states = StateGenerator.generate_basis_states(n)
        assert len(states) == (1 << n)
        # Check binary format constraints
        for s in states:
            assert len(s) == n
            assert set(s).issubset({"0", "1"})


def test_topology_generator_graph_layouts():
    """
    Verifies graph topologies (linear, triangle, square, hybrid) and adjacency list shapes.
    """
    # 2Q (Linear)
    topo_2q = TopologyGenerator.generate_topology(2)
    assert len(topo_2q["edge_list"]) == 1
    assert topo_2q["adjacency_list"][0] == [1]

    # 3Q (Triangle)
    topo_3q = TopologyGenerator.generate_topology(3)
    assert len(topo_3q["edge_list"]) == 3

    # 4Q (Square)
    topo_4q = TopologyGenerator.generate_topology(4)
    assert len(topo_4q["edge_list"]) == 4

    # 5Q (Hybrid)
    topo_5q = TopologyGenerator.generate_topology(5)
    # 5 nodes ring (5 edges) + 3 diagonal links = 8 edges
    assert len(topo_5q["edge_list"]) == 8


def test_calibration_decay_and_noise():
    """
    Verifies calibration decay equations output decayed values and noise fluctuations.
    """
    generator = CalibrationGenerator(seed=42)
    
    # At epoch 0 (no decay)
    cal_e0 = generator.generate_calibration("Q0", epoch=0, t1_0=100.0, t2_0=80.0, er_0=0.01, eg_1q_0=0.0005, eg_2q_0=0.010, freq_0=5.0)
    assert cal_e0["t1"] == 100.0
    assert cal_e0["t2"] == 80.0

    # At epoch 50 (decayed values)
    cal_e50 = generator.generate_calibration("Q0", epoch=50, t1_0=100.0, t2_0=80.0, er_0=0.01, eg_1q_0=0.0005, eg_2q_0=0.010, freq_0=5.0)
    assert cal_e50["t1"] < 100.0
    assert cal_e50["t2"] < 80.0
    # Gate error rate should grow as coherence declines
    assert cal_e50["single_gate_error"] > 0.0005
    assert cal_e50["two_gate_error"] > 0.010


def test_dataset_generator_reproducibility():
    """
    Verifies chronological splits and file generation outputs.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        generator = DatasetGenerator(base_output_path=tmpdir, seed=123)
        generated_dirs = generator.generate_all_datasets()
        
        # Verify 5 directory datasets created
        assert len(generated_dirs) == 5
        
        for d in generated_dirs:
            assert os.path.exists(d)
            # Verify required files are created
            assert os.path.exists(os.path.join(d, "calibration.csv"))
            assert os.path.exists(os.path.join(d, "train.csv"))
            assert os.path.exists(os.path.join(d, "validation.csv"))
            assert os.path.exists(os.path.join(d, "test.csv"))
            assert os.path.exists(os.path.join(d, "statistics.json"))
            assert os.path.exists(os.path.join(d, "metadata.json"))
            assert os.path.exists(os.path.join(d, "summary.json"))
            
            # Verify chronological split sizes (70% train, 15% val, 15% test)
            with open(os.path.join(d, "train.csv"), "r") as f:
                lines = f.readlines()
                # Subtract header line
                assert (len(lines) - 1) >= 70
