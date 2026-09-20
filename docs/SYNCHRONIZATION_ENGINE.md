# Synchronization Engine Documentation

This document describes the synchronization workflow and the architectural relationships of repositories and services.

## Synchronization Workflow Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as API Client / Chron Task
    participant SyncService as DigitalTwinSynchronizationService
    participant DB as MongoDB Database
    
    User->>SyncService: POST /digital-twin/Q0/sync
    SyncService->>DB: Fetch calibrations list for Q0
    DB-->>SyncService: List[CalibrationHistory]
    SyncService->>SyncService: Check duplicate calibrations
    SyncService->>SyncService: Calculate deltas & hourly drifts
    SyncService->>SyncService: Create TwinVersionSnapshot
    SyncService->>SyncService: Add to FIFO history buffer
    SyncService->>DB: Update Twin (Optimistic Concurrency Lock)
    DB-->>SyncService: Updated DigitalTwin document
    SyncService-->>User: Twin state matching version
```

## Repository & Service Architecture

```mermaid
classDiagram
    class BaseRepository {
        <<Interface>>
        +get_by_id(id)
        +get_all(filter)
        +create(entity)
        +update(id, data)
        +delete(id)
    }
    class BaseService {
        <<Interface>>
        +get_by_id(id)
        +get_all(filter)
        +create(entity)
        +update(id, data)
        +delete(id)
    }
    class QubitRepository {
        +get_active_qubits()
    }
    class QubitService {
        +create_qubit()
        +update_qubit()
        +soft_delete_qubit()
    }
    BaseRepository <|-- QubitRepository
    BaseService <|-- QubitService
    QubitService --> QubitRepository
```

## Duplicate & Conflict Detection
1. **Duplicate Calibration Detection**: Prevent double-syncing calibrations by filtering out incoming calibrations whose `epoch_number` matches existing committed snapshots.
2. **Conflict Detection**: Verify that the document version increment is checked concurrently using MongoDB optimistic locking patterns during document save updates.
