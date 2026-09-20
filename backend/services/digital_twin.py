from typing import Any, Dict, List, Optional
import numpy as np
from datetime import datetime, timezone
from backend.repositories.digital_twin import DigitalTwinRepository
from backend.models.digital_twin import DigitalTwin
from backend.services.base import BaseService
from backend.core.exceptions import NotFoundException

class DigitalTwinService(BaseService[DigitalTwin, DigitalTwinRepository]):
    """
    Service class managing business logic for Digital Twins,
    enforcing audit trails, soft deletes, and computed state analytics.
    """

    def __init__(self, repository: DigitalTwinRepository):
        super().__init__(repository)

    async def get_by_qubit_id(self, qubit_id: str) -> DigitalTwin:
        """
        Retrieves the active twin configuration for a qubit.
        """
        twin = await self.repository.get_by_qubit_id(qubit_id)
        if not twin:
            raise NotFoundException(f"Digital Twin for qubit {qubit_id} not found.")
        return twin

    async def create_twin(self, twin: DigitalTwin, user_id: Optional[str] = None) -> DigitalTwin:
        """
        Initializes a Digital Twin document with audit logging.
        """
        twin.record_audit("Digital Twin Created", user_id)
        return await self.create(twin)

    async def update_twin(self, id_str: str, update_data: Dict[str, Any], user_id: Optional[str] = None) -> DigitalTwin:
        """
        Updates Twin fields, incrementing version numbers.
        """
        current = await self.get_by_id(id_str)
        update_data["version"] = current.version + 1
        current.version += 1
        current.record_audit("Twin Metadata Updated", user_id)
        update_data["audit_trail"] = current.audit_trail
        return await self.update(id_str, update_data)

    async def soft_delete_twin(self, id_str: str, user_id: Optional[str] = None) -> None:
        """
        Marks Digital Twin as deleted (soft delete).
        """
        current = await self.get_by_id(id_str)
        current.version += 1
        current.record_audit("Twin Soft Deleted", user_id)
        update_data = {
            "is_deleted": True,
            "version": current.version,
            "audit_trail": current.audit_trail
        }
        await self.update(id_str, update_data)

    async def get_twin_analytics(self, qubit_id: str) -> Dict[str, Any]:
        """
        Computes Digital Twin trends, stability, and historical drifts.
        """
        twin = await self.get_by_qubit_id(qubit_id)
        snapshots = twin.version_history
        
        if not snapshots:
            return {
                "qubit_id": qubit_id,
                "sync_count": 0,
                "msg": "No synchronization history to compute analytics."
            }

        # Drifts collection
        drifts = [s.drift_values.get("t1_drift_rate", 0.0) for s in snapshots if s.drift_values]
        avg_drift = float(np.mean(drifts)) if drifts else 0.0
        max_drift = float(np.max(drifts)) if drifts else 0.0
        min_drift = float(np.min(drifts)) if drifts else 0.0

        # Trends evaluation (percentage change between oldest and newest version)
        oldest_cal = snapshots[0].calibration_data
        newest_cal = snapshots[-1].calibration_data

        def compute_percentage_change(old_val, new_val):
            if old_val == 0.0:
                return 0.0
            return ((new_val - old_val) / old_val) * 100.0

        coherence_trend = compute_percentage_change(oldest_cal.get("t1", 0.0), newest_cal.get("t1", 0.0))
        frequency_trend = compute_percentage_change(oldest_cal.get("frequency", 0.0), newest_cal.get("frequency", 0.0))
        error_trend = compute_percentage_change(oldest_cal.get("readout_error", 0.0), newest_cal.get("readout_error", 0.0))

        # Stability evaluation (standard deviation of T1 values)
        t1_vals = [s.calibration_data.get("t1", 0.0) for s in snapshots]
        stability = float(np.std(t1_vals)) if t1_vals else 0.0

        return {
            "qubit_id": qubit_id,
            "synchronization_count": len(snapshots),
            "average_drift": avg_drift,
            "maximum_drift": max_drift,
            "minimum_drift": min_drift,
            "coherence_trend_percent": coherence_trend,
            "frequency_trend_percent": frequency_trend,
            "error_trend_percent": error_trend,
            "calibration_stability_std": stability
        }
