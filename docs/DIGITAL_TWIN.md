# Digital Twin Synchronization Lineage

This document describes the state machine lifecycle and synchronization engine implementation.

## 1. Physical Qubit Lifecycle State Diagram (Mermaid)
```mermaid
stateDiagram-v2
    [*] --> Dormant : Initialized
    Dormant --> Active : Calibrations Synced
    Active --> Idle : No Circuit Active
    Active --> Degraded : Parameter Out of Limits
    Degraded --> Active : Recalibrated
    Active --> Scheduled : Selected by Mapper
    Scheduled --> Executed : Circuit Run Complete
    Executed --> FeedbackUpdated : Delta error calculated
    Active --> Archived : Soft Deleted / Replaced
    Archived --> [*]
```

## 2. Synchronization Sequence Workflow (Mermaid)
```mermaid
sequenceDiagram
    participant API as REST API Router
    participant Sync as Sync Service
    participant Repo as Twin Repository
    participant DB as MongoDB

    API ->> Sync: synchronize_qubit_twin(qubit_id, calibrations)
    Sync ->> Repo: get_by_qubit_id(qubit_id)
    Repo ->> DB: Query digital_twins
    DB -->> Repo: Current twin document
    Repo -->> Sync: Twin state object (V1)
    
    loop For each calibration in chronological list
        Sync ->> Sync: Compute T1/T2 hourly drift rate
        Sync ->> Sync: Check duplicate calibration timestamps
        Sync ->> Sync: Increment version count to V2
        Sync ->> Sync: Append snapshot to version history
        Sync ->> Sync: Push calibration to FIFO buffer (rolls if size > 10)
    end
    
    Sync ->> Repo: update(qubit_id, updated_data)
    Repo ->> DB: Update digital_twins
    DB -->> API: Returns synchronized Twin V2
```

## 3. Rollback Lineage Truncation
Rollback allows restoring the state machine to a prior version `V_target`.
When a rollback is requested:
1. The service reads the version history list of the Digital Twin.
2. It filters out all snapshots with `version > V_target`.
3. It resets `current_version` to `V_target`.
4. It updates the database record and appends a `"Rollback Performed"` action to the audit trail log list.
5. Invalidation or replacement of subsequent records is logged.
