import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from backend.main import app
from backend.core.dependencies import get_current_active_user, get_db
from backend.models.user import User
from backend.models.digital_twin import DigitalTwin

# Setup mock objects
mock_user = User(
    username="test_user",
    email="test@twinqmap.org",
    hashed_password="",
    role="admin",
    is_active=True
)
mock_user.id = "user_mock_object_id"

mock_twin = DigitalTwin(
    qubit_id="Q0",
    status="Initialized",
    current_version=1,
    version_history=[],
    history_buffer=[],
    metadata={}
)
mock_twin.id = "twin_mock_object_id"

# Mock dependencies functions
async def override_get_current_user():
    return mock_user

async def override_get_db():
    mock_db = MagicMock()
    return mock_db

# Override dependencies in app
app.dependency_overrides[get_current_active_user] = override_get_current_user
app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_api_health_endpoint():
    """
    Verifies that the health check endpoint returns 200 and expected status.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "degraded"]


def test_api_create_twin_endpoint(monkeypatch):
    """
    Verifies POST /api/v1/digital-twin returns a valid created twin response.
    """
    # Mock the DigitalTwinService methods
    mock_create = AsyncMock(return_value=mock_twin)
    
    # We must patch get_digital_twin_service dependency
    from backend.services.digital_twin import DigitalTwinService
    from backend.core.dependencies import get_digital_twin_service
    
    async def override_get_twin_service():
        svc = MagicMock(spec=DigitalTwinService)
        svc.create_twin = mock_create
        return svc
        
    app.dependency_overrides[get_digital_twin_service] = override_get_twin_service
    
    payload = {
        "qubit_id": "Q0",
        "status": "Initialized",
        "metadata": {}
    }
    
    response = client.post("/api/v1/digital-twin", json=payload)
    
    assert response.status_code == 201
    res_data = response.json()
    assert res_data["qubit_id"] == "Q0"
    assert res_data["status"] == "Initialized"
    
    # Reset app overrides to avoid interfering other tests
    app.dependency_overrides.pop(get_digital_twin_service, None)
