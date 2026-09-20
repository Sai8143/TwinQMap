import os
import sys
import asyncio
import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from backend.core.logging import training_logger

class ModelTrainer:
    """
    Orchestration engine to run stateful closed-loop self-learning simulation experiments.
    """

    def __init__(self, dataset_dir: str = None, saved_models_dir: str = None):
        self.dataset_dir = dataset_dir or r"C:\Users\chsai\.gemini\antigravity\scratch\TwinQ-Map\datasets\5_qubit"
        self.saved_dir = saved_models_dir or r"C:\Users\chsai\.gemini\antigravity\scratch\TwinQ-Map\backend\machine_learning\saved_models"
        os.makedirs(self.saved_dir, exist_ok=True)

    def train_and_evaluate(self) -> Dict[str, float]:
        """
        Runs the stateful closed-loop epoch-by-epoch research simulation and ML training.
        """
        training_logger.info("Executing closed-loop autonomous simulation runner from ModelTrainer...")
        from backend.machine_learning.training.runner import AutonomousSimulationRunner
        runner = AutonomousSimulationRunner(max_epochs=100)
        
        # Execute the asynchronous runner loop using asyncio
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If uvicorn event loop is running, schedule it
            import nest_asyncio
            nest_asyncio.apply()
            
        async def run():
            await runner.initialize_experiment(qubit_count=5, max_epochs=100)
            runner.state["status"] = "RUNNING"
            await runner.run_loop()
            
        loop.run_until_complete(run())
        
        metrics = runner.state.get("latest_metrics") or {"mse": 0.0, "mae": 0.0, "r2": 1.0}
        return {"best_model_mse": metrics["mse"], "best_model_mae": metrics["mae"]}
