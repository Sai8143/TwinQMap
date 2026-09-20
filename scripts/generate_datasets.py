import os
import sys
import asyncio

# Ensure project root is in python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.machine_learning.training.runner import AutonomousSimulationRunner
from backend.database.connection import MongoDBManager

async def generate_all_closed_loop_datasets():
    print("Connecting to MongoDB database...")
    from backend.config.settings import settings
    await MongoDBManager.connect()
    db = MongoDBManager.get_database()
    
    qubit_configs = [1, 2, 3, 4, 5]
    
    for count in qubit_configs:
        print("\n" + "="*80)
        print(f"Executing Stateful Closed-Loop Research Engine for {count}-Qubit Experiment...")
        print("="*80)
        
        # Initialize runner with 100 max epochs
        runner = AutonomousSimulationRunner(max_epochs=100)
        
        # 1. Initialize experiment (seeds Epoch 0 ground truth & resets collections)
        await runner.initialize_experiment(qubit_count=count, max_epochs=100)
        
        # 2. Run stateful learning loop (performs math evolution, twin update, ML fit, predictions, scheduler mapping, swaps evaluation, feedback delta)
        runner.state["status"] = "RUNNING"
        await runner.run_loop()
        
        print(f"Closed-loop simulation completed successfully for {count}-Qubit Experiment.")
        print(f"Data saved to: C:\\Users\\chsai\\.gemini\\antigravity\\scratch\\TwinQ-Map\\datasets\\{count}_qubit\\")

if __name__ == "__main__":
    asyncio.run(generate_all_closed_loop_datasets())
    print("\nAll 5 Qubit Experiment datasets generated dynamically via stateful closed-loop ML pipelines.")
