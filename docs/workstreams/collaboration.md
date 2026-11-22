# Collaboration model

The project was built with two visible workstreams. The current run is **solo**:
the bus remains the visible handoff surface, but no session is polling it.

## Roles

| Role | Owns | Does not own |
| --- | --- | --- |
| `script` / integrator | bulk scans, extraction, tools, docs, integration | high-cost architecture calls |
| `data` / model | overall picture, hypotheses, priorities, validation | long scans |
| `operator` | direction, interrupts, arbitration | hidden RPC |

## Worktrees

```mermaid
flowchart TB
    MAIN["main<br/>REPO_ROOT<br/>integration · docs · extraction"]
    BUS["bus (historical)<br/>BUS_DIR/messages.jsonl"]

    MAIN -.-> BUS
```

The script/data worktrees were archived after consolidation; the dual-session
sequence below is retained as protocol history.

## Dual-session sequence

```mermaid
sequenceDiagram
    autonumber
    participant S as script
    participant B as bus
    participant D as data
    participant N as operator

    N->>S: task
    N->>D: task
    S->>B: request / answer
    D->>B: request / answer
    S->>B: working + ETA (long work)
    D->>B: working + ETA (long work)
    B-->>S: delivery
    B-->>D: delivery
    S->>N: compact result
    D->>N: compact result
```

## Session state

```mermaid
stateDiagram-v2
    [*] --> Active
    Active --> Working: receives task
    Working --> Standby: result posted
    Standby --> Working: new message
    Standby --> Suspended: operator suspends
    Suspended --> Active: operator resumes
    Active --> TimedOut: no ACK/working/result
    TimedOut --> [*]
```

## Handoff contract

```mermaid
classDiagram
    class Handoff {
        +path: handoff/
        +status: script-status.md
        +artifacts: TSV
        +does_not_own: source of truth
    }
    class ScriptArtifacts {
        +script_roots_tsv
        +script_types_tsv
        +script_bones_tsv
        +script_bone_points_tsv
    }
    class DataArtifacts {
        +data_model_bones_tsv
        +data_layouts_tsv
        +data_names_tsv
        +data_localization_tsv
    }
    Handoff "1" *-- "0..*" ScriptArtifacts
    Handoff "1" *-- "0..*" DataArtifacts
```

## Dual-protocol status

- `main` is clean; the recent analysis commits are integrated.
- `#0054` is closed by script in `17cc1c2`.
- `#0067` is open: **owner data** maps the 16 skeleton families to
  `data.rpf`; script continues geometry/array decode in parallel.
- `#0067` closed with a negative in `#0071`. The vehicle-curve test closed in
  `#0081`; names/units stay open. Data returned to direct-inotify standby. No
  requests remain open; no polling is running.
- `handoff/` is the stable exchange surface. A data reply can resume the
  handoff without restarting the script work.

!!! note "No hidden RPC"
    Every cross-session message is a JSON line in `messages.jsonl`. The user can
    read, tail, or inject messages as `operator`.
