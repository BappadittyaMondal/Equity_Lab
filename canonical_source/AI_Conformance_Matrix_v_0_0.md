<!-- IERL-CANONICAL-METADATA v1.2 -->
> **Canonical retrieval label:** AI Conformance Matrix  
> **Role:** Operating-system governance or contract  
> **Use when:** Use to govern task routing, contracts, evidence handling, confidence, or output quality.  
> **Cognitive mode:** Control-plane reasoning: decompose the task, enforce evidence discipline, and escalate material uncertainty rather than masking it.  
> **Evidence rule:** Date material facts, distinguish fact/calculation/assumption/inference, and disclose missing inputs.  
> **Handoff: apply alongside the most specific workflow skill and relevant knowledge domain.**

# AI Conformance Matrix

**Version:** v_0.0  
**Status:** Production Ready (Final)  
**Category:** Governance & Compliance  
**Priority:** Critical  
**Role:** Machine-Readable Engine Interface Conformance Matrix  
**Architecture State:** Frozen

---

## 1. Conformance Matrix Table

Below is the authoritative conformance matrix mapping inputs, outputs, access rules, allowed dependencies, and relative hierarchy for each core engine in the IERL AI Operating System:

| Component | Input Objects | Output Objects | Registry Access | State Access | Context Access | Allowed Dependencies | Authority |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **AI_Task_Orchestrator** | User Request | `TaskObject` | None | None | None | `AI_Project_Instructions_v_0.0.md` | Rank 1 |
| **AI_Intelligence_Engine** | `TaskObject` | `ResearchPlanObject` | `Module Registry`, `Framework Registry`, `Dependency Map` | None | None | `AI_Task_Orchestrator_v_0.0.md` | Rank 2 |
| **AI_Execution_Engine** | `ResearchPlanObject` | `StateObject`, `ContextAllocationObject` | `Module Registry`, `Framework Registry`, `Dependency Map` | Write / Read | Write / Read | `AI_State_Manager_v_0.0.md`, `AI_Context_Manager_v_0_0.md`, `AI_Dependency_Map_v_0.0.md` | Rank 2 |
| **AI_Research_Engine** | `ResearchPlanObject` | `ResearchObject`, `EvidenceObject` | None | Read | Read | `AI_Execution_Engine_v_0.0.md`, `Knowledge_Packs` | Rank 3 |
| **AI_Reasoning_Skills** | `ResearchObject`, `EvidenceObject` | `DecisionObject` | None | Read | Read | `AI_Research_Engine_v_0_0.md`, `AI_Confidence_Standard_v_0.0.md`, `AI_Explainability_Standard_v_0.0.md`, `Skill_Packs` | Rank 3 |
| **AI_Quality_Audit** | `DecisionObject` | `AuditObject` | None | Read | Read | `AI_Reasoning_Skills_v_0_0.md`, `AI_Confidence_Standard_v_0.0.md`, `AI_Explainability_Standard_v_0.0.md`, `AI_Project_Instructions_v_0.0.md` | Rank 1 |
| **AI_Output_System** | `AuditObject`, `DecisionObject` | `OutputObject` | None | Read | Read | `AI_Quality_Audit_v_0.0.md`, `AI_Reasoning_Skills_v_0_0.md` | Rank 2 |

---

## 2. Compliance Rules

1.  **Strict Data Boundary**: No engine may process inputs or produce outputs that deviate from their defined schemas in `AI_Object_Schemas_v_0.0.md`.
2.  **No Direct Inter-Engine Calls**: Engines must only communicate by passing validated objects through the scheduling queue of the `AI_Execution_Engine`.
3.  **Registry Restriction**: Direct access to registries is forbidden for downstream engines (`Research`, `Reasoning`, `Audit`, `Output`). Their parameters and setups must be resolved and passed as execution context by the `AI_Execution_Engine`.
4.  **State Write Restriction**: Only the `AI_State_Manager` (under direction of the `AI_Execution_Engine`) is permitted to write to the `StateObject`. All other engines have read-only access.
5.  **Context Write Restriction**: Only the `AI_Context_Manager` is permitted to allocate and write to `ContextAllocationObject`.

---

## 3. Machine-Readable JSON Definition

```json
{
  "conformance_matrix_version": "v_0.0",
  "engines": {
    "AI_Task_Orchestrator": {
      "inputs": ["User Request"],
      "outputs": ["TaskObject"],
      "registries": [],
      "state_access": "NONE",
      "context_access": "NONE",
      "allowed_dependencies": ["AI_Project_Instructions_v_0.0.md"],
      "authority_rank": 1
    },
    "AI_Intelligence_Engine": {
      "inputs": ["TaskObject"],
      "outputs": ["ResearchPlanObject"],
      "registries": ["Module Registry", "Framework Registry", "Dependency Map"],
      "state_access": "NONE",
      "context_access": "NONE",
      "allowed_dependencies": ["AI_Task_Orchestrator_v_0.0.md"],
      "authority_rank": 2
    },
    "AI_Execution_Engine": {
      "inputs": ["ResearchPlanObject"],
      "outputs": ["StateObject", "ContextAllocationObject"],
      "registries": ["Module Registry", "Framework Registry", "Dependency Map"],
      "state_access": "WRITE_READ",
      "context_access": "WRITE_READ",
      "allowed_dependencies": ["AI_State_Manager_v_0.0.md", "AI_Context_Manager_v_0_0.md", "AI_Dependency_Map_v_0.0.md"],
      "authority_rank": 2
    },
    "AI_Research_Engine": {
      "inputs": ["ResearchPlanObject"],
      "outputs": ["ResearchObject", "EvidenceObject"],
      "registries": [],
      "state_access": "READ",
      "context_access": "READ",
      "allowed_dependencies": ["AI_Execution_Engine_v_0.0.md", "Knowledge_Packs"],
      "authority_rank": 3
    },
    "AI_Reasoning_Skills": {
      "inputs": ["ResearchObject", "EvidenceObject"],
      "outputs": ["DecisionObject"],
      "registries": [],
      "state_access": "READ",
      "context_access": "READ",
      "allowed_dependencies": ["AI_Research_Engine_v_0_0.md", "AI_Confidence_Standard_v_0.0.md", "AI_Explainability_Standard_v_0.0.md", "Skill_Packs"],
      "authority_rank": 3
    },
    "AI_Quality_Audit": {
      "inputs": ["DecisionObject"],
      "outputs": ["AuditObject"],
      "registries": [],
      "state_access": "READ",
      "context_access": "READ",
      "allowed_dependencies": ["AI_Reasoning_Skills_v_0_0.md", "AI_Confidence_Standard_v_0.0.md", "AI_Explainability_Standard_v_0.0.md", "AI_Project_Instructions_v_0.0.md"],
      "authority_rank": 1
    },
    "AI_Output_System": {
      "inputs": ["AuditObject", "DecisionObject"],
      "outputs": ["OutputObject"],
      "registries": [],
      "state_access": "READ",
      "context_access": "READ",
      "allowed_dependencies": ["AI_Quality_Audit_v_0.0.md", "AI_Reasoning_Skills_v_0_0.md"],
      "authority_rank": 2
    }
  }
}
```

---

## Document Information

**Document:** AI_Conformance_Matrix_v_0.0.md  
**Version:** v_0.0  
**Status:** Production Ready  
**Dependencies:** AI_Object_Schemas_v_0.0.md, AI_Pipeline_Specification_v_0.0.md  
**Consumed By:** IRA_Project_Validator_v1.0.py  
