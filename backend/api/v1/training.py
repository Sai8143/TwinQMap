from fastapi import APIRouter, Depends, BackgroundTasks, status, Response, Query
from typing import Dict, Any, List
from backend.core.dependencies import get_current_active_user
from backend.models.user import User
from backend.machine_learning.training.runner import AutonomousSimulationRunner
from backend.database.connection import MongoDBManager
from backend.config.constants import DBCollections

router = APIRouter(prefix="/training", tags=["Autonomous Simulation & Model Training"])

# Global runner instance
runner = AutonomousSimulationRunner()

@router.post(
    "/start",
    summary="Initialize self-learning simulation experiment session (Epoch 0)"
)
async def start_simulation(
    qubit_count: int = 5,
    max_epochs: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """
    Clears database collections, seeds Epoch 0 mathematically, and readies the simulation session.
    """
    await runner.initialize_experiment(qubit_count, max_epochs)
    return runner.state


@router.post(
    "/run",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger local epoch-based self-learning quantum simulation experiment (alias)"
)
async def run_simulation_alias(
    background_tasks: BackgroundTasks,
    qubit_count: int = 5,
    max_epochs: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """
    Spawns an offline mathematical simulation run in the background.
    """
    await runner.initialize_experiment(qubit_count, max_epochs)
    runner.state["status"] = "RUNNING"
    background_tasks.add_task(runner.run_loop)
    return {"status": "QUEUED", "qubit_count": qubit_count, "max_epochs": max_epochs, "run_id": runner.state["run_id"]}


@router.post(
    "/pause",
    summary="Pause active self-learning running loop"
)
async def pause_simulation(
    current_user: User = Depends(get_current_active_user)
):
    """
    Freezes the simulation engine loop, retaining intermediate results.
    """
    runner.state["status"] = "PAUSED"
    return runner.state


@router.post(
    "/resume",
    summary="Resume paused self-learning simulation loop"
)
async def resume_simulation(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """
    Resumes running the simulation loop in the background.
    """
    runner.state["status"] = "RUNNING"
    background_tasks.add_task(runner.run_loop)
    return runner.state


@router.post(
    "/step",
    summary="Advance self-learning loop by exactly one epoch"
)
async def step_simulation(
    current_user: User = Depends(get_current_active_user)
):
    """
    Executes a single epoch run, updates database calibration and digital twins, and sets status to PAUSED.
    """
    current = runner.state["current_epoch"]
    max_ep = runner.state["max_epochs"]
    if current >= max_ep:
        runner.state["status"] = "COMPLETED"
        return runner.state

    runner.state["status"] = "PAUSED"
    await runner.execute_single_epoch(current + 1)
    
    if runner.state["current_epoch"] >= max_ep:
        runner.state["status"] = "COMPLETED"

    return runner.state


@router.get(
    "/metrics",
    summary="Get autonomous simulation metrics history"
)
async def get_metrics(
    run_id: str = Query(default=None),
    qubit_count: int = Query(default=5),
    limit: int = 100,
    current_user: User = Depends(get_current_active_user)
):
    """
    Retrieves the metrics compiled during self-learning training epochs.
    """
    db = MongoDBManager.get_database_by_qubits(qubit_count)
    
    # Resolve collection name via runs_registry
    if run_id:
        reg = await db["runs_registry"].find_one({"run_id": run_id})
    else:
        reg = await db["runs_registry"].find_one(sort=[("timestamp", -1)])
        
    if not reg:
        return []
        
    coll_name = f"{reg['collection_prefix']}_training"
    cursor = db[coll_name].find().sort("epoch_number", 1).limit(limit)
    res = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])
        res.append(doc)
    return res


@router.get(
    "/runs",
    summary="Retrieve all historical experiment run IDs"
)
async def get_all_runs(
    qubit_count: int = Query(default=5),
    current_user: User = Depends(get_current_active_user)
):
    db = MongoDBManager.get_database_by_qubits(qubit_count)
    runs = await db["runs_registry"].distinct("run_id", {"qubit_count": qubit_count})
    # Sort runs alphabetically descending (places latest dates first)
    runs = sorted([r for r in runs if r], reverse=True)
    return {"runs": runs}


@router.get(
    "/status",
    summary="Get active self-learning simulation status and progress parameters"
)
async def get_simulation_status(
    current_user: User = Depends(get_current_active_user)
):
    """
    Exposes in-memory execution parameters (current epoch, generated parameters, metrics)
    of the running mathematical qubit evolution pipeline.
    """
    return runner.state


@router.post(
    "/reset",
    summary="Force reset the training simulation runner to IDLE"
)
async def reset_simulation(
    current_user: User = Depends(get_current_active_user)
):
    """
    Forcefully resets the active runner's state parameters to IDLE.
    """
    runner.state["status"] = "IDLE"
    runner.state["current_epoch"] = 0
    return runner.state
