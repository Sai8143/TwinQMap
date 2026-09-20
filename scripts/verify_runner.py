import os
import sys
import asyncio

# Ensure project root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.machine_learning.training.runner import AutonomousSimulationRunner
from backend.database.connection import MongoDBManager

async def test_execution():
    print("Initializing MongoDB client...")
    from backend.config.settings import settings
    await MongoDBManager.connect()
    
    print("\nStarting Stateful Closed-Loop Research Engine for 5-Qubit configuration (100 Epochs)...")
    runner = AutonomousSimulationRunner(max_epochs=100)
    
    # Initialize session
    await runner.initialize_experiment(qubit_count=5, max_epochs=100)
    
    # Run the loop sequentially for 10 epochs
    runner.state["status"] = "RUNNING"
    await runner.run_loop()
    
    print("\nTest execution finished successfully.")

if __name__ == "__main__":
    asyncio.run(test_execution())
