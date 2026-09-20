import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone, timedelta
from backend.services.digital_twin_sync import DigitalTwinSynchronizationService
from backend.models.calibration import CalibrationHistory
from backend.models.digital_twin import DigitalTwin

@pytest.mark.asyncio
async def test_synchronize_twin_drifts_and_fifo():
    """
    Verifies that synchronization computes drift rates correctly and rolls the FIFO buffer.
    """
    twin_repo = MagicMock()
    cal_repo = MagicMock()
    
    # Configure buffer size limit = 2 (for easy testing of rolling overflow)
    sync_service = DigitalTwinSynchronizationService(
        twin_repository=twin_repo,
        calibration_repository=cal_repo,
        max_buffer_size=2
    )

    # Initial mock Digital Twin state
    mock_twin = DigitalTwin(
        qubit_id="Q0",
        status="Initialized",
        current_version=0,
        version_history=[],
        history_buffer=[]
    )
    mock_twin.id = "twin_object_id"

    # Set up mock repos
    twin_repo.get_by_qubit_id = AsyncMock(return_value=mock_twin)
    twin_repo.update = AsyncMock(side_effect=lambda id_str, data: DigitalTwin(_id=id_str, **data))
    cal_repo.create = AsyncMock()

    # Create 3 sequential calibrations (epoch 1, 2, 3) to overflow the FIFO buffer of size 2
    cal1 = CalibrationHistory(
        qubit_id="Q0",
        epoch_number=1,
        t1=100.0,
        t2=80.0,
        readout_error=0.01,
        single_gate_error=0.0005,
        two_gate_error=0.01,
        frequency=5.00,
        temperature=0.015,
        timestamp=datetime.now(timezone.utc) - timedelta(hours=2),
        backend_name="ibm"
    )
    
    cal2 = CalibrationHistory(
        qubit_id="Q0",
        epoch_number=2,
        t1=98.0,  # Decay -2.0 over 1 hour -> T1 drift rate = -2.0 / hour
        t2=78.0,
        readout_error=0.012,
        single_gate_error=0.0006,
        two_gate_error=0.011,
        frequency=5.01,
        temperature=0.015,
        timestamp=datetime.now(timezone.utc) - timedelta(hours=1),
        backend_name="ibm"
    )

    cal3 = CalibrationHistory(
        qubit_id="Q0",
        epoch_number=3,
        t1=95.0,
        t2=75.0,
        readout_error=0.015,
        single_gate_error=0.0008,
        two_gate_error=0.013,
        frequency=5.02,
        temperature=0.015,
        timestamp=datetime.now(timezone.utc),
        backend_name="ibm"
    )

    # Sync calibrations
    updated_twin = await sync_service.synchronize_qubit_twin("Q0", [cal1, cal2, cal3])

    # Assertions
    # 1. Total committed versions should be 3
    assert updated_twin.current_version == 3
    assert len(updated_twin.version_history) == 3
    
    # 2. FIFO Buffer size should be capped at max_buffer_size (2), discarding epoch 1 details
    assert len(updated_twin.history_buffer) == 2
    assert updated_twin.history_buffer[0]["epoch_number"] == 2
    assert updated_twin.history_buffer[1]["epoch_number"] == 3

    # 3. T1 drift rate calculation validation:
    # Epoch 2 drift = (T1_curr - T1_prev) / 1 hour = (98 - 100) / 1 = -2.0
    epoch2_snapshot = updated_twin.version_history[1]
    assert pytest.approx(epoch2_snapshot.drift_values["t1_drift_rate"]) == -2.0


@pytest.mark.asyncio
async def test_rollback_twin_state():
    """
    Verifies rolling back twin to a target historical configuration version.
    """
    twin_repo = MagicMock()
    cal_repo = MagicMock()
    sync_service = DigitalTwinSynchronizationService(twin_repo, cal_repo)

    # Mock Twin containing version snapshots
    mock_twin = DigitalTwin(
        qubit_id="Q0",
        status="Active",
        current_version=2,
        version_history=[
            # Version 1 Snapshot
            {
                "version": 1,
                "timestamp": datetime.now(timezone.utc) - timedelta(hours=1),
                "calibration_data": {"epoch_number": 1, "t1": 100.0, "timestamp": datetime.now(timezone.utc).isoformat()},
                "delta_from_previous": {},
                "drift_values": {},
                "change_reason": "Epoch 1 Sync"
            },
            # Version 2 Snapshot
            {
                "version": 2,
                "timestamp": datetime.now(timezone.utc),
                "calibration_data": {"epoch_number": 2, "t1": 95.0, "timestamp": datetime.now(timezone.utc).isoformat()},
                "delta_from_previous": {"t1_delta": -5.0},
                "drift_values": {"t1_drift_rate": -5.0},
                "change_reason": "Epoch 2 Sync"
            }
        ],
        history_buffer=[{"epoch_number": 1, "t1": 100.0}, {"epoch_number": 2, "t1": 95.0}]
    )
    mock_twin.id = "twin_object_id"

    twin_repo.get_by_qubit_id = AsyncMock(return_value=mock_twin)
    twin_repo.update = AsyncMock(side_effect=lambda id_str, data: DigitalTwin(_id=id_str, **data))

    # Trigger rollback to version 1
    rolled_twin = await sync_service.rollback_twin_version("Q0", target_version=1)

    # Assertions
    assert rolled_twin.current_version == 1
    assert len(rolled_twin.version_history) == 1
    assert len(rolled_twin.history_buffer) == 1
    assert rolled_twin.history_buffer[0]["t1"] == 100.0
