import pytest
import math
import numpy as np
from datetime import datetime, timezone
from backend.mathematical_quantum_simulator.simulator import MathematicalQuantumSimulator

def test_simulator_deterministic_decay():
    """
    Unit test to verify that the mathematical simulator computes decayed
    T1, T2, and readout error values according to deterministic exponential formulas.
    """
    # Initialize simulator with custom start epoch
    start = datetime(2026, 7, 2, 0, 0, 0, tzinfo=timezone.utc)
    sim = MathematicalQuantumSimulator(start_epoch=start)
    
    # 0 hours elapsed (epoch=0)
    calibs_t0 = [sim._simulate_qubit_calibration("Q0", 0)]
    q0_t0 = calibs_t0[0]
    
    # At epoch 0, T1 should equal baseline T1_0 (100.0)
    assert q0_t0["t1"] == 100.0
    # At epoch 0, T2 should equal baseline T2_0 (80.0)
    assert q0_t0["t2"] == 80.0
    # At epoch 0, Readout error contains Gaussian noise from seed 42
    # Base ER_0 = 0.01. Readout noise for Q0 at seed 42 = 0.0001523...
    assert pytest.approx(q0_t0["readout_error"], abs=1e-3) == 0.01015

    # Epoch 50 elapsed
    q0_t50 = sim._simulate_qubit_calibration("Q0", 50)
    
    # Check T1 = 100 * exp(-0.002 * 50) = 100 * exp(-0.1)
    expected_t1 = 100.0 * math.exp(-0.1)
    assert pytest.approx(q0_t50["t1"]) == expected_t1

    # Check T2 = 80 * exp(-0.003 * 50) = 80 * exp(-0.15)
    expected_t2 = 80.0 * math.exp(-0.15)
    assert pytest.approx(q0_t50["t2"]) == expected_t2


@pytest.mark.asyncio
async def test_simulator_adapter_interface():
    """
    Unit test to verify execution output matching correct interface specs.
    """
    sim = MathematicalQuantumSimulator()
    calibs = await sim.get_calibration_data()
    
    # Should have 5 active qubits (Q0 to Q4)
    assert len(calibs) == 5
    for c in calibs:
        assert c["qubit_id"] in ["Q0", "Q1", "Q2", "Q3", "Q4"]
        assert c["t1"] > 0.0
        assert c["t2"] > 0.0
        assert c["readout_error"] >= 0.0
        assert c["single_gate_error"] > 0.0

    # Test circuit execution
    res = await sim.execute_circuit(circuit_representation="dummy", physical_mapping=[0, 1])
    assert res["status"] == "COMPLETED"
    assert res["provider"] == "mathematical_quantum_simulator"
    assert "fidelity" in res
    assert "counts" in res
    assert res["counts"]["0"] + res["counts"]["1"] == 1024
