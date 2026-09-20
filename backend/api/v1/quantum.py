from fastapi import APIRouter, Depends, status
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from backend.core.dependencies import get_current_active_user
from backend.security.auth import RoleChecker
from backend.models.user import User
from backend.config.constants import UserRoles
from backend.config.settings import settings
from backend.mathematical_quantum_simulator.simulator import MathematicalQuantumSimulator
from backend.quantum.adapters.ibm import IBMQuantumAdapter

router = APIRouter(prefix="/quantum", tags=["Quantum Hardware & Simulator API"])

# Dependency to check for researcher role
researcher_only = RoleChecker([UserRoles.ADMIN, UserRoles.RESEARCHER, UserRoles.VIEWER])

class QuantumExecuteRequest(BaseModel):
    """
    Schema for quantum circuit execution requests.
    """
    circuit_representation: str = Field(..., description="QASM circuit code")
    physical_mapping: List[int] = Field(..., description="Qubit mapping list")
    shots: int = Field(default=1024, description="Number of execution shots")
    provider: str = Field(default="simulator", description="Selected provider (simulator, ibm, ionq)")


def get_quantum_provider():
    """
    Factory helper to supply pluggable provider backends.
    """
    if settings.is_simulation_mode:
        return MathematicalQuantumSimulator()
    else:
        return IBMQuantumAdapter(api_token=settings.IBM_QUANTUM_TOKEN)


@router.get(
    "/calibration",
    summary="Get current physical calibration metrics",
    response_model=List[Dict[str, Any]]
)
async def get_calibration(
    current_user: User = Depends(get_current_active_user),
    provider = Depends(get_quantum_provider)
):
    """
    Retrieves readout error, T1/T2, frequency, and gate error parameters for active qubits.
    """
    return await provider.get_calibration_data()


@router.post(
    "/execute",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit a logical quantum circuit with specific mapping",
    dependencies=[Depends(researcher_only)]
)
async def execute_circuit(
    payload: QuantumExecuteRequest
):
    """
    Dispatches a quantum circuit program to the selected backend.
    """
    from backend.quantum.adapters.ibm import IBMQuantumAdapter
    from backend.quantum.adapters.ionq import IonQQuantumAdapter
    
    prov_name = payload.provider.lower()
    if prov_name == "ibm":
        provider = IBMQuantumAdapter(api_token=settings.IBM_QUANTUM_TOKEN)
    elif prov_name == "ionq":
        provider = IonQQuantumAdapter(api_token=settings.IONQ_API_KEY)
    else:
        provider = MathematicalQuantumSimulator()

    result = await provider.execute_circuit(
        circuit_representation=payload.circuit_representation,
        physical_mapping=payload.physical_mapping,
        shots=payload.shots
    )
    return result


@router.get(
    "/status",
    summary="Retrieve active quantum processor hardware status"
)
async def get_hardware_status():
    """
    Gets operational state, queue size, and system configurations for both local and cloud providers.
    """
    from backend.quantum.adapters.ibm import IBMQuantumAdapter
    
    # 1. Simulator Status
    sim = MathematicalQuantumSimulator()
    sim_status = await sim.get_device_status()
    
    # 2. IBM Quantum Status
    ibm = IBMQuantumAdapter(api_token=settings.IBM_QUANTUM_TOKEN)
    ibm_status = await ibm.get_device_status()
    
    # Check if configured
    is_ibm_configured = settings.IBM_QUANTUM_TOKEN is not None and settings.IBM_QUANTUM_TOKEN != "token_placeholder_ibm"
    
    # 3. IonQ Cloud Status
    is_ionq_configured = settings.IONQ_API_KEY is not None and settings.IONQ_API_KEY != "key_placeholder_ionq"
    
    return {
        "simulator": {
            "status": sim_status.get("status", "ONLINE"),
            "backend_name": sim_status.get("backend_name", "TwinQ_Math_Simulator_5Q")
        },
        "ibm": {
            "configured": is_ibm_configured,
            "status": ibm_status.get("status", "UNCONFIGURED" if not is_ibm_configured else "ONLINE"),
            "backend_name": ibm_status.get("backend_name", "ibm_torino_simulated" if not is_ibm_configured else ibm_status.get("backend_name")),
            "pending_jobs": ibm_status.get("pending_jobs", 0),
            "token_masked": f"{settings.IBM_QUANTUM_TOKEN[:4]}...{settings.IBM_QUANTUM_TOKEN[-4:]}" if is_ibm_configured else "Not Configured"
        },
        "ionq": {
            "configured": is_ionq_configured,
            "status": "ONLINE" if is_ionq_configured else "UNCONFIGURED",
            "backend_name": "ionq_aria_25q" if is_ionq_configured else "ionq_aria_simulated",
            "pending_jobs": 0,
            "token_masked": f"{settings.IONQ_API_KEY[:4]}...{settings.IONQ_API_KEY[-4:]}" if is_ionq_configured else "Not Configured"
        }
    }
