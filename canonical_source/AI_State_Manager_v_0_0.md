<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI State Manager  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# AI_State_Manager_v_0.0

**Version:** v_0.0
**Status:** Production Ready (Final)
**Category:** Core Registry / Runtime Infrastructure
**Priority:** Critical
**Role:** Runtime State Tracking, Checkpoint, and Recovery Authority
**Architecture State:** Frozen

---

# Table of Contents

1. Purpose
2. Architectural Position
3. Responsibilities
4. Non-Responsibilities
5. State Object Schema
6. State Lifecycle
7. Checkpoint System
8. Rollback Protocol
9. Retry Coordination
10. Runtime Memory Model
11. Persistence Rules
12. Failure Recovery Integration
13. Interfaces
14. Governance
15. Final Specification

---

# 1. Purpose

The AI State Manager is the runtime infrastructure component responsible for tracking the execution state of every task session, recording checkpoints, and enabling recovery when an engine fails partway through processing.

It is consumed exclusively by the Execution Engine, which uses it to log, checkpoint, and recover runtime sessions per the Failure & Recovery Architecture (AI_Architecture_Overview_v_0.0.md §13C).

---

# 2. Architectural Position

```
AI_Execution_Engine
    ↓ (requests state read/write)
AI_State_Manager
    ↓ (persists)
Session State Store
```

The State Manager never initiates action. It responds only to Execution Engine requests to read, write, checkpoint, or roll back state.

---

# 3. Responsibilities

The State Manager shall:

- Track the current status of every active runtime session
- Record checkpoints at defined stage boundaries
- Store failure events with full context for recovery
- Provide rollback data on request
- Maintain state history for audit reconstruction
- Enforce state immutability once a session is archived

---

# 4. Non-Responsibilities

The State Manager shall never:

- Make scheduling decisions (Execution Engine's responsibility)
- Interpret task content
- Modify object content (TaskObject, ResearchObject, etc.)
- Retry failed operations itself (it stores retry counts; Execution Engine acts on them)
- Decide confidence, research completeness, or audit verdicts

---

# 5. State Object Schema

```yaml
StateObject:
  StateID:
  TaskID:
  SessionStatus:          # Pending | Active | Checkpointed | Completed | Failed | Archived
  CurrentStage:           # 1-7 per AI_Pipeline_Specification_v_0.0
  CheckpointHistory:
    - CheckpointID:
      Stage:
      Timestamp:
      SnapshotRef:
  FailureLog:
    - FailureID:
      Stage:
      Timestamp:
      FailureClass:       # F1 | F2 | F3 | F4 (per AI_Architecture_Overview_v_0.0.md §13C)
      RecoveryAttempt:
      FinalStatus:
  RetryCount:
  ActiveModules:
  ActiveFrameworks:
  ContextAllocationRef:   # pointer to Context Manager's allocation record
  CreatedAt:
  UpdatedAt:
  ArchivedAt:
```

---

# 6. State Lifecycle

```
Created
   ↓
Active
   ↓
Checkpointed  ←──┐
   ↓             │ (loop per stage)
[Stage complete]─┘
   ↓
Completed  ─────────→  Archived

   OR (at any point)

Failed → Recovery Attempt → [Active (resumed) | Archived (terminal failure)]
```

Once `Archived`, a `StateObject` is immutable. No field may be edited in place — corrections require a new `StateObject` version with `SupersedesStateID` reference.

---

# 7. Checkpoint System

A checkpoint is recorded at the completion of each pipeline stage (per `AI_Pipeline_Specification_v_0.0.md`):

| Checkpoint | Recorded After |
|---|---|
| CP-1 | TaskObject validated |
| CP-2 | ResearchPlanObject validated |
| CP-3 | Execution session initialized |
| CP-4 | ResearchObject + EvidenceObject produced |
| CP-5 | DecisionObject produced |
| CP-6 | AuditObject produced |
| CP-7 | OutputObject emitted |

**Recovery Rule:** On failure, the Execution Engine resumes from the nearest valid checkpoint, not from Stage 1. Only checkpoints with `SnapshotRef` fully written are considered valid resume points.

---

# 8. Rollback Protocol

Rollback restores the session to the state recorded at a specified checkpoint. Rollback affects only:

- Execution state
- Context allocation record (delegates actual reallocation to Context Manager)
- Active module/framework list

Rollback never affects already-produced validated objects (`TaskObject`, `ResearchObject`, etc.) — those are immutable once validated, per each engine's own contract. Rollback discards only in-progress, unvalidated work.

---

# 9. Retry Coordination

The State Manager tracks `RetryCount` per stage. It does not decide whether to retry — that is the Execution Engine's responsibility per its Retry Policy (Execution Engine §48). The State Manager enforces one governance rule:

> **Retry Ceiling:** If `RetryCount` for any single stage exceeds the Resource Governor's `maximum retry count` (Execution Engine §27), the State Manager marks the session `Failed` and refuses further retry recording for that stage, forcing escalation per Failure Classification F3.

---

# 10. Runtime Memory Model

State is held in two tiers:

| Tier | Scope | Lifetime |
|---|---|---|
| **Hot State** | Current active session only | Duration of task processing |
| **Archived State** | Completed/failed sessions | Persisted for audit trail; read-only |

Hot State is what Execution Engine reads/writes during processing. Archived State is what Quality Audit and downstream reviewers query for provenance reconstruction — it is never written to during active processing.

---

# 10A. State Consistency & Authority Rules

To prevent data drift and architectural fragmentation, the system enforces the following state consistency rules:

*   **Authoritative State**: The master session state (`StateObject`) stored and managed exclusively by the AI State Manager. This is the single source of truth for runtime progress.
*   **Derived State**: Temporary flags or values calculated dynamically from the authoritative state (e.g., stage durations, progress percentages, active loop counters). Derived state is never persisted.
*   **Cached State**: Local read-only copies of state held temporarily by engines to reduce query latency. Cached state must be validated using the `StateVersion` before use.
*   **StateVersion**: A monotonic integer counter included in the `StateObject` header. It starts at 1 and increments on every write operation.
*   **Expiration**: Inactive Hot State entries are marked expired after 24 hours of task inactivity and are moved to the Archived State tier.
*   **Invalidation**: When the Execution Engine writes a state change, a broadcast is sent to all engine instances to invalidate their local Cached State.
*   **Recovery**: If an engine loses synchronization, it must discard its local state and query the State Manager for the latest valid checkpoint snapshot (`CP-1` to `CP-7`).
*   **Conflict Resolution**: Enforces Optimistic Concurrency Control (OCC). If two write requests arrive with the same version, the State Manager accepts the first and rejects the second. The rejected transaction must reload the updated state and retry.
*   **Single Authority**: The AI State Manager is the sole writer of the runtime state. No engine or skill may silently maintain or act upon alternative authoritative states.

---

# 11. Persistence Rules

- Every `StateObject` write is versioned; no in-place mutation of Archived State
- CheckpointHistory is append-only
- FailureLog is append-only
- State persists independently of context window — it is not lost on context reallocation (this is precisely why it exists as a separate component from Context Manager)

---

# 12. Failure Recovery Integration

This maps directly onto the Failure & Recovery Architecture already defined in `AI_Architecture_Overview_v_0.0` §13C:

| Failure Severity | State Manager Action |
|---|---|
| F1 (Recoverable) | Log retry attempt; no checkpoint rollback needed |
| F2 (Degraded) | Log degradation flag on current `StateObject`; checkpoint preserved |
| F3 (Escalated) | Mark session `Failed`; preserve full `FailureLog` for human/audit review |
| F4 (Blocking) | Mark session `Failed`; set `SessionStatus: Archived` immediately; no retry permitted |

---

# 13. Interfaces

**Consumed by:** AI_Execution_Engine (exclusively)
**Never accessed by:** Research Engine, Reasoning Skills, Quality Audit, Output System directly — these engines' state needs are mediated through Execution Engine's coordination role, consistent with the Dependency Rules (AI_Architecture_Overview_v_0.0.md §13A: "Any Registry → Any Engine" is forbidden; the State Manager is a registry-tier component).

---

# 14. Governance

Every `StateObject` must satisfy:

- Unique `StateID`
- Valid `TaskID` reference to an existing `TaskObject`
- `SessionStatus` transitions only follow the lifecycle in Section 6 (no skipping states)
- `CheckpointHistory` entries are chronologically ordered
- Archived sessions are immutable

---

# 15. Final Specification

The AI State Manager provides the runtime memory backbone that makes the Failure & Recovery Architecture operational. Without it, failures have nowhere to be logged and no checkpoint to resume from — this document resolves that gap (Forensic Audit CV-03, State Manager component).

---

# Document Information

**Document:** AI_State_Manager_v_0.0.md
**Version:** v_0.0
**Status:** Production Ready
**Dependencies:** AI_Execution_Engine_v_0.0.md, AI_Pipeline_Specification_v_0.0.md
**Consumed By:** AI_Execution_Engine_v_0.0.md (exclusively)
**Resolves:** CV-03 (Forensic Audit — Missing State Manager)

# END OF DOCUMENT
