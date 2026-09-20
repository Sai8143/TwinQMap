import math
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.repositories.digital_twin import DigitalTwinRepository
from backend.repositories.calibration import CalibrationRepository
from backend.models.digital_twin import DigitalTwin, TwinVersionSnapshot
from backend.models.calibration import CalibrationHistory
from backend.core.logging import digital_twin_logger
from backend.core.exceptions import ValidationException, DatabaseException, NotFoundException

class DigitalTwinSynchronizationService:
    """
    Core Synchronization Engine coordinating physical calibration updates,
    delta computations, drift calculations, FIFO buffer cleanups, and rollbacks.
    """

    def __init__(
        self,
        twin_repository: DigitalTwinRepository,
        calibration_repository: CalibrationRepository,
        max_buffer_size: int = 50
    ):
        self.twin_repo = twin_repository
        self.cal_repo = calibration_repository
        self.max_buffer_size = max_buffer_size

    def _verify_calibration_integrity(self, calibrations: List[CalibrationHistory]) -> None:
        """
        Validates chronological order and reasonable ranges of calibration parameters.
        """
        if not calibrations:
            return
            
        # Check chronological ordering
        for i in range(1, len(calibrations)):
            if calibrations[i].timestamp < calibrations[i-1].timestamp:
                raise ValidationException("Calibrations list is not chronologically ordered.")
                
        # Range checking
        for c in calibrations:
            if c.t1 <= 0.0 or c.t2 <= 0.0:
                raise ValidationException(f"Invalid coherence time for qubit {c.qubit_id}: T1={c.t1}, T2={c.t2}")
            if not (0.0 <= c.readout_error <= 1.0):
                raise ValidationException(f"Invalid readout error rate for qubit {c.qubit_id}: {c.readout_error}")

    def _compute_delta_and_drift(
        self,
        prev_data: Dict[str, Any],
        curr_data: Dict[str, Any],
        elapsed_hours: float
    ) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Calculates numerical deltas and drift rates (change per hour) between two calibration points.
        """
        deltas = {}
        drifts = {}
        
        target_keys = ["t1", "t2", "readout_error", "single_gate_error", "two_gate_error", "frequency"]
        for key in target_keys:
            prev_val = prev_data.get(key, 0.0)
            curr_val = curr_data.get(key, 0.0)
            
            delta = curr_val - prev_val
            deltas[f"{key}_delta"] = delta
            
            # Avoid division by zero
            if elapsed_hours > 0.0:
                drifts[f"{key}_drift_rate"] = delta / elapsed_hours
            else:
                drifts[f"{key}_drift_rate"] = 0.0
                
        return deltas, drifts

    async def synchronize_qubit_twin(
        self,
        qubit_id: str,
        new_calibrations: List[CalibrationHistory],
        user_id: Optional[str] = None,
        is_full_sync: bool = False
    ) -> DigitalTwin:
        """
        Synchronizes new calibrations into the qubit's Digital Twin.
        Supports full rebuilds (is_full_sync=True) or incremental syncing.
        """
        digital_twin_logger.info(f"Starting sync for twin '{qubit_id}' (Full: {is_full_sync})...")
        
        # 1. Integrity check
        self._verify_calibration_integrity(new_calibrations)

        # 2. Retrieve or create Digital Twin
        twin = await self.twin_repo.get_by_qubit_id(qubit_id)
        if not twin:
            digital_twin_logger.info(f"No digital twin found for qubit {qubit_id}. Creating new twin.")
            twin = DigitalTwin(
                qubit_id=qubit_id,
                status="Initialized",
                current_version=0,
                version_history=[],
                history_buffer=[]
            )
            twin.record_audit("Twin Initialized", user_id)
            twin = await self.twin_repo.create(twin)

        if is_full_sync:
            # Rebuild version history and buffer completely
            twin.version_history = []
            twin.history_buffer = []
            twin.current_version = 0

        # Filter out duplicates
        existing_epochs = {s.calibration_data.get("epoch_number") for s in twin.version_history}
        filtered_calibrations = [
            c for c in new_calibrations 
            if c.epoch_number not in existing_epochs
        ]

        if not filtered_calibrations:
            digital_twin_logger.info(f"No new calibrations to synchronize for qubit {qubit_id}.")
            return twin

        # 3. Process calibrations sequentially
        for cal in filtered_calibrations:
            # Get previous calibration data if it exists
            prev_cal = None
            if twin.version_history:
                prev_cal = twin.version_history[-1].calibration_data

            curr_data = {
                "epoch_number": cal.epoch_number,
                "timestamp": cal.timestamp.isoformat(),
                "t1": cal.t1,
                "t2": cal.t2,
                "readout_error": cal.readout_error,
                "single_gate_error": cal.single_gate_error,
                "two_gate_error": cal.two_gate_error,
                "frequency": cal.frequency,
                "temperature": cal.temperature,
                "backend_status": cal.backend_status
            }

            deltas = {}
            drifts = {}
            if prev_cal:
                # Calculate elapsed time in hours
                prev_time = datetime.fromisoformat(prev_cal["timestamp"])
                curr_time = cal.timestamp
                time_delta = (curr_time - prev_time).total_seconds() / 3600.0
                deltas, drifts = self._compute_delta_and_drift(prev_cal, curr_data, time_delta)

            # Update calibration history with computed drifts
            cal.noise_drift = deltas.get("readout_error_delta", 0.0)
            cal.drift_rate = drifts.get("t1_drift_rate", 0.0)
            if cal.id:
                await self.cal_repo.update(str(cal.id), {"noise_drift": cal.noise_drift, "drift_rate": cal.drift_rate})
            else:
                await self.cal_repo.create(cal)

            # 4. Version increment & snapshot commit
            next_version = twin.current_version + 1
            snapshot = TwinVersionSnapshot(
                version=next_version,
                parent_version=twin.current_version if twin.current_version > 0 else None,
                timestamp=datetime.now(timezone.utc),
                calibration_data=curr_data,
                delta_from_previous=deltas,
                drift_values=drifts,
                change_reason=f"Epoch {cal.epoch_number} Sync"
            )

            twin.version_history.append(snapshot)
            twin.current_version = next_version
            
            # FIFO history buffer update
            twin.history_buffer.append(curr_data)
            if len(twin.history_buffer) > self.max_buffer_size:
                twin.history_buffer.pop(0)  # Remove oldest entry (FIFO)

        # 5. Save changes to DB with optimistic concurrency conflict detection
        twin.status = "Active"
        twin.last_updated = datetime.now(timezone.utc)
        twin.version += 1
        twin.record_audit("Twin Synchronized", user_id)
        
        # Concurrency verification
        updated_twin = await self.twin_repo.update(
            str(twin.id),
            twin.model_dump(by_alias=True, exclude={"id"})
        )
        if not updated_twin:
            raise DatabaseException("Concurrency Conflict detected: Digital Twin was modified in another session.")
            
        digital_twin_logger.info(f"Twin '{qubit_id}' successfully synchronized to version {twin.current_version}.")
        return updated_twin

    async def rollback_twin_version(
        self,
        qubit_id: str,
        target_version: int,
        user_id: Optional[str] = None
    ) -> DigitalTwin:
        """
        Rolls back the Digital Twin state configuration to a target historical version.
        """
        digital_twin_logger.info(f"Requesting rollback of twin '{qubit_id}' to version {target_version}...")
        twin = await self.twin_repo.get_by_qubit_id(qubit_id)
        if not twin:
            raise NotFoundException(f"Digital Twin for qubit {qubit_id} does not exist.")

        # Find target version snapshot
        target_snapshot = None
        for snapshot in twin.version_history:
            if snapshot.version == target_version:
                target_snapshot = snapshot
                break

        if not target_snapshot:
            raise ValidationException(f"Version {target_version} is not found in history lineage of twin {qubit_id}.")

        # Truncate version history after target_version
        twin.version_history = [s for s in twin.version_history if s.version <= target_version]
        twin.current_version = target_version
        
        # Re-populate FIFO buffer from truncated version history
        twin.history_buffer = [s.calibration_data for s in twin.version_history[-self.max_buffer_size:]]
        
        twin.status = "Initialized" if target_version == 0 else "Active"
        twin.last_updated = datetime.now(timezone.utc)
        twin.version += 1
        twin.record_audit(f"Twin Rolled Back to version {target_version}", user_id)

        updated_twin = await self.twin_repo.update(
            str(twin.id),
            twin.model_dump(by_alias=True, exclude={"id"})
        )
        digital_twin_logger.info(f"Twin '{qubit_id}' successfully rolled back to version {target_version}.")
        return updated_twin
