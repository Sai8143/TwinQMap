import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application-wide configuration settings loaded from environment variables
    and the .env file using Pydantic Settings.
    """
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Project Settings
    PROJECT_NAME: str = "TwinQ-Map"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Security Settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", os.getenv("JWT_SECRET_KEY", "supersecretjwtkeythatshouldbechangedinproduction123!"))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    # Database Settings
    MONGODB_URL: str = os.getenv("MONGODB_URL", os.getenv("MONGODB_URI", "mongodb://localhost:27017"))
    MONGODB_DB_NAME: str = "twinq_map"

    # Operation Mode
    # Valid values: "simulation", "real"
    OPERATION_MODE: str = "simulation"

    # Quantum Provider SDK API Tokens
    IBM_QUANTUM_TOKEN: Optional[str] = None
    IONQ_API_KEY: Optional[str] = None
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AZURE_QUANTUM_CONNECTION_STRING: Optional[str] = None
    RIGETTI_API_KEY: Optional[str] = None

    @property
    def is_simulation_mode(self) -> bool:
        """
        Helper property to determine if simulator is active.
        """
        return self.OPERATION_MODE.lower() == "simulation"


settings = Settings()
