from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.database.connection import get_db
from backend.repositories.user import UserRepository
from backend.repositories.qubit import QubitRepository
from backend.repositories.calibration import CalibrationRepository
from backend.repositories.digital_twin import DigitalTwinRepository
from backend.repositories.execution import ExecutionRepository
from backend.repositories.feedback import FeedbackRepository
from backend.repositories.prediction import PredictionRepository
from backend.services.user import UserService
from backend.services.qubit import QubitService
from backend.services.calibration import CalibrationService
from backend.services.digital_twin import DigitalTwinService
from backend.services.digital_twin_sync import DigitalTwinSynchronizationService
from backend.services.execution import ExecutionService
from backend.services.feedback import FeedbackService
from backend.security.auth import get_current_user
from backend.models.user import User

# Repository Injections
async def get_user_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> UserRepository:
    return UserRepository(db)

async def get_qubit_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> QubitRepository:
    return QubitRepository(db)

async def get_calibration_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> CalibrationRepository:
    return CalibrationRepository(db)

async def get_digital_twin_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> DigitalTwinRepository:
    return DigitalTwinRepository(db)

async def get_execution_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> ExecutionRepository:
    return ExecutionRepository(db)

async def get_feedback_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> FeedbackRepository:
    return FeedbackRepository(db)

async def get_prediction_repository(db: AsyncIOMotorDatabase = Depends(get_db)) -> PredictionRepository:
    return PredictionRepository(db)


# Service Injections
async def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)

async def get_qubit_service(repo: QubitRepository = Depends(get_qubit_repository)) -> QubitService:
    return QubitService(repo)

async def get_calibration_service(repo: CalibrationRepository = Depends(get_calibration_repository)) -> CalibrationService:
    return CalibrationService(repo)

async def get_digital_twin_service(repo: DigitalTwinRepository = Depends(get_digital_twin_repository)) -> DigitalTwinService:
    return DigitalTwinService(repo)

async def get_digital_twin_sync_service(
    twin_repo: DigitalTwinRepository = Depends(get_digital_twin_repository),
    cal_repo: CalibrationRepository = Depends(get_calibration_repository)
) -> DigitalTwinSynchronizationService:
    return DigitalTwinSynchronizationService(twin_repo, cal_repo)

async def get_execution_service(repo: ExecutionRepository = Depends(get_execution_repository)) -> ExecutionService:
    return ExecutionService(repo)

async def get_feedback_service(repo: FeedbackRepository = Depends(get_feedback_repository)) -> FeedbackService:
    return FeedbackService(repo)


# User Auth Dependency
async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user
