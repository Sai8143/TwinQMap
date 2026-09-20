import pytest
from unittest.mock import AsyncMock, MagicMock
from bson import ObjectId
from backend.models.qubit import Qubit
from backend.models.calibration import CalibrationHistory
from backend.models.digital_twin import DigitalTwin

def test_qubit_model_validation():
    """
    Verifies that the Qubit Pydantic model validates fields correctly.
    """
    qubit_dict = {
        "qubit_id": "Q0",
        "physical_qubit_number": 0,
        "backend_name": "ibm_sherbrooke",
        "backend_type": "superconducting",
        "status": "Initialized",
        "frequency": 5.12,
        "temperature": 0.015,
        "metadata": {}
    }
    
    q = Qubit(**qubit_dict)
    assert q.qubit_id == "Q0"
    assert q.physical_qubit_number == 0
    assert q.status == "Initialized"
    assert q.version == 1
    assert q.is_deleted is False


def test_qubit_audit_logging():
    """
    Verifies that record_audit appends messages to the audit trail.
    """
    q = Qubit(
        qubit_id="Q0",
        physical_qubit_number=0,
        backend_name="ibm",
        backend_type="superconducting",
        status="Dormant"
    )
    
    assert len(q.audit_trail) == 0
    q.record_audit("Qubit Activated", user_id="user_admin")
    
    assert len(q.audit_trail) == 1
    assert q.audit_trail[0]["action"] == "Qubit Activated"
    assert q.audit_trail[0]["user_id"] == "user_admin"
    assert q.version == 1
