from fastapi import APIRouter, Depends, status, Query
from typing import List, Optional
from backend.schemas.calibration import CalibrationCreate, CalibrationResponse
from backend.services.calibration import CalibrationService
from backend.models.calibration import CalibrationHistory
from backend.core.dependencies import get_calibration_service, get_current_active_user
from backend.models.user import User

router = APIRouter(prefix="/quantum/calibration", tags=["Calibration Engine"])

@router.post(
    "",
    response_model=CalibrationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Insert a new physical qubit calibration entry"
)
async def insert_calibration(
    calibration_data: CalibrationCreate,
    service: CalibrationService = Depends(get_calibration_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submits a new calibration log entry. Increments versions and logs.
    """
    cal = CalibrationHistory(
        qubit_id=calibration_data.qubit_id,
        epoch_number=calibration_data.epoch_number,
        t1=calibration_data.t1,
        t2=calibration_data.t2,
        readout_error=calibration_data.readout_error,
        single_gate_error=calibration_data.single_gate_error,
        two_gate_error=calibration_data.two_gate_error,
        frequency=calibration_data.frequency,
        temperature=calibration_data.temperature,
        noise_drift=calibration_data.noise_drift or 0.0,
        drift_rate=calibration_data.drift_rate or 0.0,
        backend_status=calibration_data.backend_status or "Active",
        backend_name=calibration_data.backend_name
    )
    cal.record_audit("Calibration Inserted", user_id=str(current_user.id))
    return await service.create(cal)


@router.get(
    "/history",
    response_model=List[CalibrationResponse],
    summary="Retrieve calibration history list"
)
async def get_calibration_history(
    qubit_id: str,
    limit: int = Query(default=50, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    service: CalibrationService = Depends(get_calibration_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns pagination calibration history sorted by timestamp descending.
    """
    return await service.get_history_by_qubit(qubit_id, limit=limit, skip=skip)
