# Architecture Documentation

This document describes the software design layout and structural models of TwinQ-Map.

## 1. System Component Diagram (Mermaid)
```mermaid
classDiagram
    class FastAPI {
        +app: FastAPI
        +include_router()
    }
    class MongoDBManager {
        +connect()
        +disconnect()
    }
    class BaseRepository {
        +create()
        +get_by_id()
        +update()
        +delete()
    }
    class DigitalTwinSynchronizationService {
        +synchronize_qubit_twin()
        +rollback_twin_state()
    }
    class QubitMapper {
        +compile_mapping()
    }
    class ModelTrainer {
        +train_and_evaluate()
    }

    FastAPI --> MongoDBManager
    BaseRepository <|-- UserRepository
    BaseRepository <|-- CalibrationRepository
    BaseRepository <|-- DigitalTwinRepository
    DigitalTwinSynchronizationService --> DigitalTwinRepository
    DigitalTwinSynchronizationService --> CalibrationRepository
    QubitMapper --> QHIGreedyMappingAlgorithm
```

## 2. Sequence Workflow: Qubit Scheduling (PlantUML)
```plantuml
@startuml
actor Researcher
entity FastAPI
database MongoDB
entity Mapper
entity MLPredictor

Researcher -> FastAPI : POST /scheduler/schedule
activate FastAPI

FastAPI -> MongoDB : get_history_by_qubit(Q0-Q4)
activate MongoDB
MongoDB --> FastAPI : calibration history list
deactivate MongoDB

FastAPI -> MLPredictor : predict(features)
activate MLPredictor
MLPredictor --> FastAPI : forecasted calibrations
deactivate MLPredictor

FastAPI -> Mapper : compile_mapping(constraints, calibrations)
activate Mapper
Mapper --> FastAPI : mappings, SWAPs, estimated fidelity
deactivate Mapper

FastAPI --> Researcher : schedule results payload
deactivate FastAPI
@endum
```

## 3. Deployment Topology (PlantUML)
```plantuml
@startuml
package "Client Console (React)" {
  [Web Browser]
}
package "Cloud Services Gateway" {
  [FastAPI Backend Server]
  [MongoDB Database Container]
}
package "Quantum Cloud Hardware" {
  [IBM Quantum Runtime]
  [IonQ API]
}

[Web Browser] --> [FastAPI Backend Server] : REST / JWT
[FastAPI Backend Server] --> [MongoDB Database Container] : Async Driver
[FastAPI Backend Server] --> [IBM Quantum Runtime] : Fallback/Retry HTTP
[FastAPI Backend Server] --> [IonQ API] : HTTP
@endum
```
