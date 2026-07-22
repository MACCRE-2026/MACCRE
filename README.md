# MACCRE (Sovereign Edge Orchestrator)

> **v0.1.0-alpha** — *Active Solo Development*

MACCRE is a Sovereign Edge multi-agent orchestrator built around a strict deterministic control flow architecture. 

It was built to solve a fundamental problem in modern agentic software: as AI models become more capable, the frameworks built around them increasingly cede control *to* the non-deterministic intelligence. MACCRE rejects this. It acts as an iron-clad General Contractor, providing rigid, auditable, deterministic scaffolding around highly specialized AI sub-contractors.

## Core Philosophy: The OmniBuilder Doctrine

1. **Deterministic Control:** Agents do not route themselves. The `FlowEngine` governs all execution paths using explicit `CTRL_` primitives (Gate, Scatter, Merge, Pause).
2. **Zero-Dependency Core:** The core backend does not rely on third-party SDKs (no `langchain`, no `google-genai` wrapper). All routing happens via standard library REST bindings to ensure true edge portability.
3. **Sovereign Execution:** The system is designed to run locally, on metal, with local state (SQLite WAL) and complete hardware independence.

## Key Features

- **Textual TUI (Nexus Plex):** A complete terminal user interface for designing topologies, configuring agents, and monitoring flow execution in real-time.
- **Topology Visualizer:** Real-time directed acyclic graph (DAG) visualization of agent routing and state.
- **MacroNode Workshop:** Compose complex, multi-agent topologies (e.g., `CTRL_SCATTER` fan-outs to 8 parallel agents converging on a `CTRL_MERGE`) using a visual node editor.
- **Telemetric Memory (Time-Travel Replay):** Every node traversal is tracked via `flow_vector` lineage in SQLite, enabling full deterministic replay of non-deterministic execution paths.

## Project Status & Contributing

This project is in active, daily solo development. 
It is highly opinionated and tailored to a specific architectural vision.

- **Issues:** Bug reports and architectural discussions are welcome.
- **Pull Requests:** Please do not submit unsolicited PRs. Open an issue to discuss your proposed changes first. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Licensing (AGPLv3 Dual-License)

This software is released under the **GNU Affero General Public License v3.0 (AGPLv3)**. 

### Why AGPLv3?
MACCRE is designed to be free and open for developers, researchers, and hobbyists to use, modify, and learn from. However, if a commercial entity wishes to run this software over a network (e.g., as a backend SaaS or internal proprietary infrastructure), the AGPL requires them to open-source their entire modified stack.

**Commercial Licensing:**
If your organization's legal policies prohibit the use of AGPL-licensed code, or if you wish to use MACCRE in a proprietary commercial product without open-sourcing your stack, a commercial license is required. Please contact the author directly to negotiate commercial terms.
