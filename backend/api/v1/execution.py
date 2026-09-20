from fastapi import APIRouter, Depends, status, Query
from typing import List
from backend.schemas.execution import ExecutionCreate, ExecutionResponse
from backend.services.execution import ExecutionService
from backend.models.execution import ExecutionHistory
from backend.core.dependencies import get_execution_service, get_current_active_user
from backend.models.user import User

router = APIRouter(prefix="/quantum/execution", tags=["Execution Logging"])

@router.post(
    "",
    response_model=ExecutionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Insert a new circuit job execution log"
)
async def insert_execution(
    exec_data: ExecutionCreate,
    service: ExecutionService = Depends(get_execution_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Submits execution logs. Records timestamps.
    """
    exec_log = ExecutionHistory(
        execution_id=exec_data.execution_id,
        circuit_id=exec_data.circuit_id,
        logical_qubits=exec_data.logical_qubits,
        physical_mapping=exec_data.physical_mapping,
        execution_time=exec_data.execution_time,
        execution_result=exec_data.execution_result,
        execution_success=exec_data.execution_success,
        latency=exec_data.latency or 0.0,
        noise=exec_data.noise or 0.0,
        metadata=exec_data.metadata or {}
    )
    exec_log.record_audit("Execution Log Created", user_id=str(current_user.id))
    return await service.create(exec_log)


@router.get(
    "/history",
    response_model=List[ExecutionResponse],
    summary="Retrieve execution logs history list"
)
async def get_execution_history(
    limit: int = Query(default=50, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    service: ExecutionService = Depends(get_execution_service),
    current_user: User = Depends(get_current_active_user)
):
    """
    Returns pagination execution logs history.
    """
    return await service.get_all(
        filter_query={"is_deleted": False},
        sort_by=[("created_at", -1)],
        limit=limit,
        skip=skip
    )
