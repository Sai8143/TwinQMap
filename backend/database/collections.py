from motor.motor_asyncio import AsyncIOMotorDatabase
from backend.config.constants import DBCollections
from backend.core.logging import mongodb_logger
from backend.core.exceptions import DatabaseException

# JSON validators for core collections to enforce integrity
USER_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["username", "email", "hashed_password", "role", "is_active", "version", "is_deleted", "created_at", "updated_at"],
        "properties": {
            "username": {"bsonType": "string", "minLength": 3, "maxLength": 50},
            "email": {"bsonType": "string", "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"},
            "hashed_password": {"bsonType": "string"},
            "role": {"enum": ["admin", "researcher", "viewer"]},
            "is_active": {"bsonType": "bool"},
            "version": {"bsonType": "int"},
            "is_deleted": {"bsonType": "bool"}
        }
    }
}

QUBIT_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["qubit_id", "physical_qubit_number", "backend_name", "backend_type", "status", "version", "is_deleted", "created_at", "updated_at"],
        "properties": {
            "qubit_id": {"bsonType": "string"},
            "physical_qubit_number": {"bsonType": "int"},
            "logical_qubit_number": {"bsonType": ["int", "null"]},
            "backend_name": {"bsonType": "string"},
            "backend_type": {"bsonType": "string"},
            "status": {"enum": ["Dormant", "Initialized", "Active", "Idle", "Degraded", "Predicted", "Scheduled", "Executed", "Feedback Updated", "Archived"]},
            "frequency": {"bsonType": "double"},
            "temperature": {"bsonType": "double"},
            "version": {"bsonType": "int"},
            "is_deleted": {"bsonType": "bool"}
        }
    }
}

CALIBRATION_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["qubit_id", "epoch_number", "t1", "t2", "readout_error", "single_gate_error", "two_gate_error", "frequency", "temperature", "timestamp", "backend_name", "version", "is_deleted"],
        "properties": {
            "qubit_id": {"bsonType": "string"},
            "epoch_number": {"bsonType": "int"},
            "t1": {"bsonType": "double"},
            "t2": {"bsonType": "double"},
            "readout_error": {"bsonType": "double"},
            "single_gate_error": {"bsonType": "double"},
            "two_gate_error": {"bsonType": "double"},
            "frequency": {"bsonType": "double"},
            "temperature": {"bsonType": "double"},
            "noise_drift": {"bsonType": "double"},
            "drift_rate": {"bsonType": "double"},
            "backend_status": {"bsonType": "string"},
            "version": {"bsonType": "int"},
            "is_deleted": {"bsonType": "bool"}
        }
    }
}

DIGITAL_TWIN_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["qubit_id", "status", "current_version", "last_updated", "version_history", "history_buffer", "is_deleted", "version"],
        "properties": {
            "qubit_id": {"bsonType": "string"},
            "status": {"enum": ["Dormant", "Initialized", "Active", "Idle", "Degraded", "Predicted", "Scheduled", "Executed", "Feedback Updated", "Archived"]},
            "current_version": {"bsonType": "int"},
            "last_updated": {"bsonType": "date"},
            "version_history": {"bsonType": "array"},
            "history_buffer": {"bsonType": "array"},
            "version": {"bsonType": "int"},
            "is_deleted": {"bsonType": "bool"}
        }
    }
}


async def initialize_collections(db: AsyncIOMotorDatabase):
    """
    Initializes all database collections, applies validation schemas, and builds indexes.
    """
    try:
        existing_collections = await db.list_collection_names()

        # Helper to create collection if missing, and update validators
        async def setup_collection(name: str, validator: dict = None):
            if name not in existing_collections:
                mongodb_logger.info(f"Creating collection '{name}'...")
                await db.create_collection(name)
            
            if validator:
                mongodb_logger.info(f"Setting JSON Schema Validator on '{name}'...")
                await db.command({
                    "collMod": name,
                    "validator": validator,
                    "validationLevel": "moderate"
                })

        # Set up collections with schema validation
        await setup_collection(DBCollections.USERS, USER_VALIDATOR)
        await setup_collection(DBCollections.QUBITS, QUBIT_VALIDATOR)
        await setup_collection(DBCollections.CALIBRATION_HISTORY, CALIBRATION_VALIDATOR)
        await setup_collection(DBCollections.DIGITAL_TWINS, DIGITAL_TWIN_VALIDATOR)
        
        # Set up rest of collections
        for coll in [
            DBCollections.PREDICTION_HISTORY, DBCollections.EXECUTION_HISTORY, 
            DBCollections.FEEDBACK_HISTORY, DBCollections.SCHEDULER_HISTORY, 
            DBCollections.QUANTUM_HEALTH_INDEX, DBCollections.TRAINING_HISTORY, 
            DBCollections.MODEL_METRICS, DBCollections.CIRCUIT_HISTORY, 
            DBCollections.API_HISTORY
        ]:
            await setup_collection(coll)

        # BUILD INDEXES
        mongodb_logger.info("Building database indexes...")
        
        # Users indexes
        await db[DBCollections.USERS].create_index("username", unique=True)
        await db[DBCollections.USERS].create_index("email", unique=True)
        
        # Qubits indexes
        await db[DBCollections.QUBITS].create_index("qubit_id", unique=True)
        await db[DBCollections.QUBITS].create_index("physical_qubit_number", unique=False)

        # CalibrationHistory indexes (Qubit + Epoch + Timestamp queries)
        await db[DBCollections.CALIBRATION_HISTORY].create_index(
            [("qubit_id", 1), ("epoch_number", 1)],
            unique=True
        )
        await db[DBCollections.CALIBRATION_HISTORY].create_index("timestamp")

        # PredictionHistory indexes
        await db[DBCollections.PREDICTION_HISTORY].create_index(
            [("qubit_id", 1), ("prediction_time", -1)]
        )
        
        # DigitalTwins indexes
        await db[DBCollections.DIGITAL_TWINS].create_index("qubit_id", unique=True)

        # ExecutionHistory indexes
        await db[DBCollections.EXECUTION_HISTORY].create_index("execution_id", unique=True)
        await db[DBCollections.EXECUTION_HISTORY].create_index("circuit_id")
        
        # FeedbackHistory indexes
        await db[DBCollections.FEEDBACK_HISTORY].create_index("feedback_timestamp")

        # APIHistory (TTL Index to clean up log history after 30 days)
        await db[DBCollections.API_HISTORY].create_index("timestamp", expireAfterSeconds=2592000)

        mongodb_logger.info("All collections initialized and indexes created successfully.")
    except Exception as e:
        mongodb_logger.error(f"Error during database initialization: {str(e)}")
        raise DatabaseException("Database initialization failed", detail={"error": str(e)})


# AGGREGATION PIPELINES
def get_average_drift_pipeline(qubit_id: str) -> list:
    """
    Returns an aggregation pipeline to compute Qubit average, max, and min drifts.
    """
    return [
        {"$match": {"qubit_id": qubit_id, "is_deleted": False}},
        {"$group": {
            "_id": "$qubit_id",
            "avg_t1_drift": {"$avg": "$drift_rate"},
            "max_t1_drift": {"$max": "$drift_rate"},
            "min_t1_drift": {"$min": "$drift_rate"},
            "avg_readout_error": {"$avg": "$readout_error"},
            "avg_gate_error_1q": {"$avg": "$single_gate_error"},
            "avg_gate_error_2q": {"$avg": "$two_gate_error"},
            "count": {"$sum": 1}
        }}
    ]
