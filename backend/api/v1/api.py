from fastapi import APIRouter
from backend.api.v1.auth import router as auth_router
from backend.api.v1.quantum import router as quantum_router
from backend.api.v1.predictions import router as predictions_router
from backend.api.v1.scheduler import router as scheduler_router
from backend.api.v1.digital_twin import router as digital_twin_router
from backend.api.v1.calibration import router as calibration_router
from backend.api.v1.execution import router as execution_router
from backend.api.v1.feedback import router as feedback_router
from backend.api.v1.reports import router as reports_router
from backend.api.v1.training import router as training_router

api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth_router)
api_router.include_router(quantum_router)
api_router.include_router(predictions_router)
api_router.include_router(scheduler_router)
api_router.include_router(digital_twin_router)
api_router.include_router(calibration_router)
api_router.include_router(execution_router)
api_router.include_router(feedback_router)
api_router.include_router(reports_router)
api_router.include_router(training_router)

@api_router.get("/calibrations/history")
async def get_calibrations_history_alias(
    qubit_id: str,
    limit: int = 50
):
    """
    Returns pagination calibration history for the active experiment configuration.
    """
    from backend.database.connection import MongoDBManager
    from backend.machine_learning.training.runner import AutonomousSimulationRunner
    qubit_count = AutonomousSimulationRunner.state.get("qubit_count", 5)
    db = MongoDBManager.get_database_by_qubits(qubit_count)
    from backend.config.constants import DBCollections
    coll_name = await DBCollections.get_active_collection_name(db, qubit_count, "calibrations")
    
    cursor = db[coll_name].find({"qubit_id": qubit_id}).sort("epoch_number", -1).limit(limit)
    res = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        res.append(doc)
    return res
