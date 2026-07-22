# MACCREv2 Operator Manual
**Revision:** 2026-07-21 · Law Rev 19.0

---

## Foreword: The Architect's Perspective

I am not a coder. I do not write in any languages. While I read them reasonably well and have a deep, long-term interest in electrical engineering and computer science, when it comes to math and code, I am syntactically disabled. For whatever reason, I have never been able to organize my thoughts natively into the abstract worlds of mathematics and programming languages. 

However, I highly respect the generations of worldwide frameworks and institutions that have been built and maintained via the rigorous minds dedicated to the refinement of human observation and prediction via the mathematic grindstone. My heroes include pioneers like Grace Hopper, Edsger Dijkstra, James Clerk Maxwell, and Michael Faraday. Their influence echoes heavily throughout the MACCRE design doctrine.

I believe that a person's ability to speak abstract languages and force their mind into rigid syntax structures should not determine the reach of their voice. Seven months ago, I began using AI to formalize my conceptual ontology into math and code. MACCRE is the direct result of formalizing my thoughts, my needs, and my impulses regarding AI into a usable platform—one where the user controls as much as possible, as economically as possible. 

MACCRE was built from my own inclinations and filtered through the different agents I designed after creating the `Prompt Engineer`. This system is a reflection of how I see the world, built by the agents who helped me express it.

---

## Part I — Core Architectural Concepts

### What MACCRE Is
MACCREv2 (Google Antigravity for Sovereign Edge) is an advanced multi-agent orchestration engine and TUI command center. 

**Current System State:** The system is partially functional and heavily opinionated. It is designed around deterministic orchestration of non-deterministic agents, ensuring rigid data flow while allowing maximum cognitive freedom within the agent nodes.

### 1. The "Do What You Feel" Agent Philosophy
The bundled agents in this release were created using the `Prompt Engineer` in Chat Studio sessions. The `Prompt Engineer` serves as the progenitor of all bundled agent instructions.
Rather than using standard industry practices (concise instructions at low temperatures), MACCRE leans into a "do what you feel" ethos. Instructions are dense, structured, and complex, and agents are run at high temperatures (`1.0` and above). This induces emergent behaviors (as seen in `GretchenHarwell`) and highly effective autonomous reasoning (as seen in `OSINT_Analyst`). The myriad of configuration options exist specifically to support this high-entropy approach while the physical architecture acts as the guardrails.

### 2. The 5-Tier Datacenter & Path Anchoring
All operations are strictly anchored to a globally portable project root. The `maccre_core/utils/path_resolver.py` dynamically resolves the absolute path, ensuring zero-configuration portability.
Data is federated into a strict 5-tier silo architecture per project (defaulting to `__DATACENTER\GLOBAL\`):
- **`01_Raw_Source`**: Ingestion zone for raw documents and payloads.
- **`02_Dynamic_Context`**: Project topologies, state dictionaries, and encrypted vault storage (`auth_vault.bin`).
- **`03_Agent_Ledgers`**: Cognitive audits, tool-call telemetry, and serialized execution JSONs.
- **`04_Code_Artifacts`**: Agent-generated outputs, structured schemas, and unified chat ledgers.
- **`05_Rendered_Media`**: Rendered audio/video downstream outputs.

### 3. Sovereign Auth Layer (Federated Vault)
Authentication is fully localized and headless. No `.env` files are used.
- **Autonomous Key Ingestion** (`key_ingestor.py`): Automatically regex-fingerprints API keys and natively routes them to the correct local vault without human configuration.
- **Universal Vault** (`universal_vault.py`): Utilizes Windows DPAPI OS integration to encrypt credentials natively into AES-128 `.bin` files stored on the local disk. 

### 4. Local SQLite Architecture (C-Engine Concurrency)
MACCREv2 offloads swarm orchestration to heavily optimized, WAL-mode SQLite databases.
- **`swarm_queue.db`**: Managed by `local_broker.py`. Handles scatter-gather state machines. Uses `UNIQUE(job_id, current_node)` and `INSERT OR IGNORE` to elegantly handle concurrent Fan-In node routing. Task races are serialized at the DB layer via `BEGIN EXCLUSIVE` locks.
- **`thoughts.db`**: Unified matrix for storing agent cognitive scratchpads during schema-enforced inference.
- **`agent_library.db`**: Relational store for agent profiles, personas, and assigned tool sets.
- **`macronode_registry.db`**: Repository of nested topological clusters (MacroNodes) for modular drag-and-drop flow design.

### 5. Omni CI/CD Pipeline (JIT Gatekeeper)
Execution occurs within the **OmniBuilder CI/CD Gatekeeper** runtime. Python scripts are never executed via bare `python`.
- `omni run <path>`: Hunts zombie processes, resolves the active Python engine, and cleanly executes.
- `omni qa [path] [--smart]`: Natively runs Ruff and Pyright quality gates. Zero unused imports and explicit Python 3.11+ type hints are mandated.

---

## Part II — Operational Mechanics & Flow Execution

### 1. Flow Execution & Telemetry
When a payload enters a topology, it traverses a Directed Acyclic Graph (DAG). The `LocalMessageBroker` tracks the payload's physical path on the disk, updating the SQLite state machine at each hop. Telemetry is aggressively captured at every step: cognitive reasoning, API costs, and latency are logged to JSON matrices in `03_Agent_Ledgers` and the `system_logs.db`.

### 2. Session Siloing & Canonization
Every execution run is strictly siloed into a unique `Session ID`. A session contains its own isolated payload copies and execution history. When a session is verified as successful, the operator can **Canonize** it. Canonization locks the session from further execution, marking its outputs as verified ground-truth for future context injection.

### 3. Semantic Memory & Memory Pins
MACCREv2 implements semantic memory via `memory_pins.db`. Instead of dumping massive raw text into an LLM's context window, agents "pin" dense, highly relevant semantic concepts to specific nodes or sessions. This philosophy forces the system to distill knowledge down to its structural essence, retrieving it dynamically only when mathematically relevant to the current active flow.

### 4. Bundled Topology: OSINT_Research_x3
The default release includes the `OSINT_Research_x3` MacroNode. Far beyond a simple parallel scatter, this topology is an example of advanced recursive orchestration. It utilizes a `CASCADE` node executing a dual-index exclusionary search protocol (`num_passes=2`). It then pairs the `OSINT_Analyst` with a `Regular_Joe` dialogue partner for 3 conversational rounds, forcing an epistemic synthesis of the findings. This demonstrates how a natively configured, stubborn agent like the `OSINT_Analyst` produces incredible results when given a patient, deeply planned topological structure, rather than relying on zero-shot inference.

### 5. MacroNodes & ControlNodes Theory
MACCREv2 treats workflow routing as a composition of first-class primitives. 
- **ControlNodes (`CTRL_`)**: These are the deterministic "verbs" of the system. They handle graph structure (fan-out/fan-in via `tether_ids`), flow state (pauses, conditional gates), and data transformation (cleanup, concatenation).
- **MacroNodes**: These are pre-configured topological clusters—compositions of cognitive agents and ControlNodes wired together into a reusable, drag-and-drop module. Building a MacroNode *is* building a topology.

**Architectural Nuances:**
- **Layered Map-Reduce:** By using `CTRL_SCATTER` paired with a tethered `CTRL_MERGE`, payloads fan out to parallel, isolated `flow_line` execution threads. They process independently and then wait at the merge point until all upstream targets arrive. These can be nested infinitely (tethers inside tethers) for extreme multi-layered map-reduce patterns, synchronized entirely by the SQLite WAL-mode lock engine.
- **Controlled Recursion on a DAG:** Directed Acyclic Graphs do not naturally loop. MACCRE simulates cyclic functions by unrolling them onto the DAG. A `CTRL_RECURSION` node combined with a `CTRL_ANCHOR` (a named topological waypoint) explicitly points execution backwards up the chain, while maintaining deterministic iteration limits to prevent infinite deadlocks.
- **Probabilistic vs. Deterministic Bridges:** The `CTRL_GATE` (a "floating if" evaluator) and `CTRL_CONDITIONAL_ROUTE` act as the bridge between LLM probability and system determinism. The "Quadrivector Failback" allows an agent to run free-form, perform a structured extraction to grab a routing token, and fall back to regex or score thresholds if the LLM hallucinates the route structure.

---

## Part III — The Evolution of the Control Surface

### 1. GUI/TUI Evolution
The system has gone through 4 major generations of visual control surfaces. The current Terminal User Interface (TUI) is the furthest evolution and directly drove major overhauls in the topology node structure.
Historically, MACCRE relied on massive 7-9 page Microsoft Excel workbooks to template topologies. The operator would fill out the workbook and launch it via a rudimentary CLI. Today, CSV and SQLite are the absolute backbones of topology management, enabling the rich, dynamic visual environments seen in the current era.

### 2. TopologyVisualizer & Flow Trees
The `TopologyVisualizer` renders these complex DAGs as interactive trees within the TUI.
- **Visual State Tracking**: Nodes display pulsing animations (`●`), completions (`✓`), or failures (`✗`).
- **MacroNode Expansion**: MacroNodes toggle their inner topological steps via `[+]/[-]` visual expansion.
- **Tether Badges**: Scatter/gather operations display dynamic `[tether:id]` badges linking companion nodes.

### 3. Nexus Copilot
The Nexus Copilot is a bespoke engineering subagent integrated directly into the system. It possesses native tool access, deep codebase knowledge, and an understanding of the topological structure. While it may not be perfect yet, its core purpose is to guide the operator through the staggering complexity of the system's mechanics and configuration.

---

## Part IV — Hardware & The Edge

### 1. The S25 Edge Client & Local Models
A core tenet of the MACCRE philosophy is absolute sovereignty. A major ongoing effort is the deployment of local, model-capable hardware (the "S25 Edge Client") using the NPUs in a cluster of cellphones to dynamically switch between individual models on each node of the cluster or to shard large models among them. My other major hardware goal is an M2 Pro Mac with 96GB of unified memory...  
Currently, the system is architected to abstract local vs. remote execution seamlessly. While API routing (Gemini, Anthropic) handles the heavy lifting, the infrastructure is completely primed for edge-native models (via Ollama/llama.cpp) to take over cognitive tasks as hardware capabilities scale, ensuring the system can eventually run 100% offline and off-grid. 
