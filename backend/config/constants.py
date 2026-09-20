class DBCollections:
    """
    Database collection names for the MongoDB repository.
    """
    USERS = "Users"
    QUBITS = "Qubits"
    CALIBRATION_HISTORY = "CalibrationHistory"
    PREDICTION_HISTORY = "PredictionHistory"
    DIGITAL_TWINS = "DigitalTwins"
    EXECUTION_HISTORY = "ExecutionHistory"
    FEEDBACK_HISTORY = "FeedbackHistory"
    SCHEDULER_HISTORY = "SchedulerHistory"
    QUANTUM_HEALTH_INDEX = "QuantumHealthIndex"
    TRAINING_HISTORY = "TrainingHistory"
    MODEL_METRICS = "ModelMetrics"
    CIRCUIT_HISTORY = "CircuitHistory"
    API_HISTORY = "APIHistory"

    @classmethod
    def get_collection_name(cls, qubit_count: int, suffix: str) -> str:
        if qubit_count == 133:
            return f"exp_ibm_torino_133Q_{suffix}"
        return f"exp_{qubit_count}Q_{suffix}"

    @classmethod
    async def get_active_collection_name(cls, db, qubit_count: int, suffix: str) -> str:
        reg = await db["runs_registry"].find_one(sort=[("timestamp", -1)])
        if reg:
            return f"{reg['collection_prefix']}_{suffix}"
        return cls.get_collection_name(qubit_count, suffix)


class QuantumFidelityThresholds:
    """
    Standard operating thresholds for NISQ physical qubits.
    Fidelity below these values flags a qubit as 'unhealthy' or high-risk.
    """
    MIN_T1_MICROSECONDS = 50.0
    MIN_T2_MICROSECONDS = 30.0
    MAX_READOUT_ERROR = 0.05       # 5% max allowable readout error
    MAX_GATE_ERROR_1Q = 0.005      # 0.5% max single qubit gate error
    MAX_GATE_ERROR_2Q = 0.05       # 5% max two-qubit gate error


class QHIWeights:
    """
    Default weight parameters for calculating the Qubit Health Index (QHI).
    The sum of weights must equal 1.0.
    """
    READOUT_ERROR_WEIGHT = 0.3
    T1_COHERENCE_WEIGHT = 0.2
    T2_COHERENCE_WEIGHT = 0.2
    GATE_ERROR_WEIGHT = 0.3


class UserRoles:
    """
    User access control roles.
    """
    ADMIN = "admin"
    RESEARCHER = "researcher"
    VIEWER = "viewer"
