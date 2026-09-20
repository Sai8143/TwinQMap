from fastapi import APIRouter, Depends, status, Query
from typing import Any, Dict, List
from backend.core.dependencies import get_current_active_user, get_calibration_repository
from backend.repositories.calibration import CalibrationRepository
from backend.models.user import User
from backend.scheduler.mapping.mapper import QubitMapper
from backend.mathematical_quantum_simulator.topology_generator import TopologyGenerator
from backend.scheduler.health.qhi import QHIIndicator

from fastapi import APIRouter, Depends, status, Query, Body

router = APIRouter(prefix="/scheduler", tags=["Adaptive Qubit Scheduler"])

@router.post(
    "/schedule",
    summary="Compute optimized physical mapping and schedule execution"
)
async def schedule_job(
    logical_circuit_size: int,
    coupling_constraints: List[List[int]] = Body(...),
    algorithm: str = "QHI_Greedy",
    current_user: User = Depends(get_current_active_user)
):
    """
    Computes the ideal physical qubit mapping based on current database calibration records,
    determining layouts, routing SWAPs, and compilation metrics.
    """
    from backend.database.connection import MongoDBManager
    from backend.machine_learning.training.runner import AutonomousSimulationRunner
    from datetime import datetime, timezone
    
    qubit_count = AutonomousSimulationRunner.state.get("qubit_count", 5)
    db = MongoDBManager.get_database_by_qubits(qubit_count)
    from backend.config.constants import DBCollections
    coll_name = await DBCollections.get_active_collection_name(db, qubit_count, "calibrations")

    # 1. Fetch latest calibrations for all active qubits (Q0 to Q{qubit_count-1})
    calibrations = []
    for i in range(qubit_count):
        doc = await db[coll_name].find_one({"qubit_id": f"Q{i}"}, sort=[("epoch_number", -1)])
        if doc:
            doc["_id"] = str(doc["_id"])
            calibrations.append(doc)
        else:
            # Fallback mock/defaults if not initialized in database
            calibrations.append({
                "qubit_id": f"Q{i}",
                "t1": 100.0,
                "t2": 80.0,
                "readout_error": 0.015,
                "single_gate_error": 0.0005,
                "two_gate_error": 0.010,
                "frequency": 5.0,
                "temperature": 0.015,
                "timestamp": datetime.now(timezone.utc).isoformat()
            })

    # 2. Get physical graph topology matching the active qubit count
    topology = TopologyGenerator.generate_topology(qubit_count)

    # 3. Run mapping compilation
    mapper = QubitMapper(num_qubits=logical_circuit_size)
    logical_edges = [tuple(edge) for edge in coupling_constraints]
    result = mapper.compile_mapping(logical_edges, calibrations, topology)

    return {
        "job_id": f"job_sched_{int(datetime.now().timestamp())}",
        "algorithm": algorithm,
        "logical_circuit_size": logical_circuit_size,
        "mapping_selected": result["mapping"],
        "swaps_required": result["swaps_required"],
        "estimated_coupling_cost": result["routing_cost"],
        "estimated_mapping_fidelity": result["estimated_fidelity"],
        "execution_status": "READY"
    }


@router.get(
    "/health-indices",
    summary="Fetch Qubit Health Indices (QHI) for all hardware qubits"
)
async def get_health_indices(
    current_user: User = Depends(get_current_active_user)
):
    """
    Computes and retrieves current QHI health index indicators based on database records.
    """
    from backend.database.connection import MongoDBManager
    from backend.machine_learning.training.runner import AutonomousSimulationRunner
    qubit_count = AutonomousSimulationRunner.state.get("qubit_count", 5)
    db = MongoDBManager.get_database_by_qubits(qubit_count)
    from backend.config.constants import DBCollections
    coll_name = await DBCollections.get_active_collection_name(db, qubit_count, "calibrations")
    health_indices = []
    for i in range(qubit_count):
        cal = await db[coll_name].find_one({"qubit_id": f"Q{i}"}, sort=[("epoch_number", -1)])
        if not cal:
            cal = {
                "t1": 100.0,
                "t2": 80.0,
                "readout_error": 0.015,
                "single_gate_error": 0.0005
            }
            
        qhi = QHIIndicator.compute_qhi(cal)
        health_indices.append({
            "qubit_id": f"Q{i}",
            "health_index": qhi,
            "weights": {
                "readout": 0.3,
                "t1": 0.2,
                "t2": 0.2,
                "gate": 0.3
            },
            "status": "healthy" if qhi > 0.90 else "degraded"
        })
    return health_indices
