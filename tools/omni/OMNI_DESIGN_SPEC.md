# OmniBuilder — Sovereign CI/CD Engine
## Design Specification & Roadmap
**Revision:** 2026-04-29

---

## What Omni Is

Omni is a globally-installed Python CI/CD engine (`C:\OmniBuilder\omni.py`) invoked
as `omni <command> [path]` from any project directory. It is deliberately NOT a project
dependency — it lives outside every venv and governs them all.

Its mandate is threefold:
1. **Quality enforcement** — Hard-gate every execution path behind Ruff + Pyright
2. **Process hygiene** — Zombie hunting, WAL cleanup, cache purge
3. **Script security** — Controlled execution via fingerprint ledger + agentic greylist

Omni sits *in front of* Windows as a pre-flight layer. It does not replace Windows UAC
or PowerShell Execution Policy — those remain as a second backstop. Defense in depth.

---

## Current Capabilities (Implemented)

### `omni qa [path] [--smart]`
Enforces the quality gate. Always the first command before any execution.

- **Ruff** (linter): Runs against modified files only in `--smart` mode (git-differential),
  full scan in normal mode. Uses direct binary resolution to bypass npm/node wrappers.
- **Pyright** (type checker): Always runs globally. Scoped to `maccre_core/` when that
  directory exists. Never called via `python -m pyright` — that wrapper re-downloads a
  specific version on every cold run and hangs indefinitely. Binary resolved directly from
  the project venv's `Scripts/` directory.
- **Smart mode logic**: `git diff --name-only HEAD` + `git ls-files --others` to build
  the modified file list. Falls back to full scan if not a git repo.

### `omni build [path]`
Full pipeline: zombie hunt → QA → cache purge → PyInstaller compile.
Primarily useful for non-headless projects. MACCREv2 (headless CLI) rarely uses this.

### `omni run [path]`
Resolves entry point (`main.py`, `app.py`, `run.py`, `<project>.py`) → hunts zombies
→ launches via the project venv's Python engine.

### `omni clean [path]`
Zombie hunt + cache purge. Removes: `.ruff_cache/`, `build/`, `dist/`, `__pycache__/`,
WAL/SHM SQLite artifacts, and non-protected log files.
Protected (never deleted): `maccre_system.log`, `build_pipeline.log`, `*.telemetry.log`

### `omni smoke [path]`
Delegates to `maccre_core.tests.smoke_test` for end-to-end swarm validation.

### Core Infrastructure

**`resolve_python_engine()`** — Auto-detects the correct Python interpreter:
1. Looks for `.venv/Scripts/python.exe`, then `venv/`, then `env/`
2. Falls back to the currently active terminal interpreter
3. Hard-exits if neither is found (no silent global Python pollution)

**`resolve_tool_binary(py_engine, tool_name)`** — Resolves venv tool binaries
directly from `Scripts/`, preventing npm/node wrappers from intercepting Pyright calls.
Falls back to `python -m <tool>` as last resort.

**`hunt_zombies(project_name)`** — Terminates:
- `<project>.exe` (frozen binary, if any)
- `chromedriver.exe` (Selenium artifacts)
- Python processes running `swarm_worker.py` by WMIC cmdline match

---

## Phase 2: Script Security Layer (Roadmap)

### Design Philosophy

> Omni controls *when* scripts execute. Windows controls *whether* they can escalate.
> These are complementary, not competing.

The security layer intercepts all script execution requests before they reach Windows.
Windows Execution Policy and UAC remain active as a second gate. This matters because
AI agents can be prompt-injected; Windows UAC cannot — it has no language model to
manipulate.

### The Three-Tier Classification System

```
WHITELIST  — Fingerprint-verified, pre-approved. Instant execution, zero analysis.
GREYLIST   — Unknown or modified. Held for agentic analysis before execution.
BLACKLIST  — Explicitly prohibited. Hard block, logged, operator notified.
```

### The Fingerprint Ledger

A local SQLite database (`C:\OmniBuilder\omni_ledger.db`) storing approved script records:

```
fingerprint_ledger
  ├── sha256_hash       TEXT PRIMARY KEY   -- SHA-256 of the script content
  ├── script_path       TEXT               -- Last known path (informational only)
  ├── script_name       TEXT               -- Basename
  ├── approved_by       TEXT               -- 'operator' | 'agentic_analysis'
  ├── approved_at       TEXT               -- ISO timestamp
  ├── execution_count   INTEGER            -- Times executed under this fingerprint
  └── last_executed     TEXT               -- ISO timestamp

blacklist
  ├── sha256_hash       TEXT PRIMARY KEY
  ├── reason            TEXT
  └── flagged_at        TEXT

greylist_log
  ├── sha256_hash       TEXT
  ├── script_path       TEXT
  ├── analysis_result   TEXT               -- JSON from agentic review
  ├── decision          TEXT               -- 'approved' | 'blocked'
  └── reviewed_at       TEXT
```

**The fast path:** `omni exec script.ps1` computes SHA-256 → checks ledger → if match,
executes instantly. Zero analysis cost. This is the normal case for known scripts.

**The fingerprint lifecycle:**
```
First run  → greylist pipeline → operator approves → fingerprint written to ledger
Every run after → SHA-256 match → instant execute
Script modified → new SHA-256 → fingerprint miss → greylist pipeline again
```

### Execution Gate Flow

```
omni exec <script> [args]
        │
        ▼
  Compute SHA-256 of script content
        │
        ├── BLACKLIST match? ──────────────────────► HARD BLOCK + log event
        │
        ├── WHITELIST match (ledger hit)? ─────────► EXECUTE via venv Python engine
        │
        └── No match (unknown/modified)
                │
                ▼
        [GREYLIST PIPELINE]
        1. Dependency pre-check
           └── Parse imports → verify against known-safe package list
               If unknown package → escalate, do not auto-approve
        2. Static analysis
           └── Run Ruff on script content (in-memory, no disk write)
               Hard block on any critical rule violation
        3. Agentic content review (optional, configurable)
           └── Route to local Gemma (Ollama) for script intent analysis
               Prompt: "Does this script perform any destructive, exfiltrating,
               or privilege-escalating operations? Answer YES/NO with reason."
               Temperature: 0.0 (deterministic critic mode)
        4. Operator gate (if agentic review is inconclusive)
           └── Print script + analysis to terminal
               Prompt: "Approve for execution? [y/N/blacklist]: "
        5. On approval:
           └── Write fingerprint to ledger → EXECUTE
        6. On rejection:
           └── Optionally write to blacklist → LOG
```

### New Commands

**`omni exec <script> [-- args...]`**
Controlled script execution through the security gate. Replaces bare `python script.py`
or `powershell -File script.ps1` for any non-trivial execution.

**`omni ledger list [--project <name>]`**
Show all fingerprint-verified scripts with execution counts and last-run timestamps.

**`omni ledger revoke <sha256|script_name>`**
Remove a script from the whitelist. Forces it back through the greylist pipeline on next run.

**`omni ledger blacklist <script_name> --reason "<text>"`**
Manually add a script to the blacklist.

**`omni ledger import <path>`**
Bulk-import a directory of pre-approved scripts into the fingerprint ledger
(for bootstrapping a new machine from a trusted source).

---

## Integration with Antigravity

Antigravity already classifies every command with `SafeToAutoRun: true/false`.
That classification is model-decided — probabilistic reasoning on each invocation.

The omni fingerprint ledger provides the **deterministic layer** that complements this:

| Layer | Mechanism | Failure Mode |
|---|---|---|
| Antigravity `SafeToAutoRun` | LLM reasoning | Prompt injection, reasoning error |
| omni fingerprint gate | SHA-256 match | Script tampered between approval and execution |
| Windows UAC | Elevation prompt | N/A — not bypassable by LLM |

For Antigravity sessions specifically, the workflow becomes:
```
Antigravity proposes a command
    │
    ├── SafeToAutoRun=true AND fingerprint in ledger ──► auto-execute
    ├── SafeToAutoRun=true AND NOT in ledger ──────────► greylist pipeline → operator gate
    ├── SafeToAutoRun=false ────────────────────────────► operator approval (current behavior)
    └── Any path: Windows UAC catches any privilege escalation attempt
```

The practical benefit: scripts you run regularly (build_blank_copy.ps1, maccre.py launch
commands, omni qa) get fingerprinted on first approval and then execute without friction.
Novel or modified scripts always stop for review, regardless of what the model says.

---

## Coexistence with Windows — The Explicit Boundary

| Concern | Handled By | Notes |
|---|---|---|
| Script content analysis | omni greylist | Windows has no equivalent |
| Script fingerprinting | omni ledger | Windows tracks by publisher cert, not content |
| Dependency graph pre-check | omni | Not a Windows feature |
| Code quality (Ruff/Pyright) | omni qa | Not a Windows feature |
| Privilege escalation | Windows UAC | Keep active — immune to prompt injection |
| Execution policy | Windows (Bypass explicit) | omni controls when bypass is granted |
| Unknown binary reputation | Windows Smart App Control | Keep active as parallel gate |

**Do not disable Windows Execution Policy system-wide.** Keep `-ExecutionPolicy Bypass`
as an explicit invocation flag controlled by omni. This means omni decides when bypass
is granted — Windows still holds the default.

**Do not disable UAC.** It is immune to the exact attack vector (prompt injection → AI
manipulation) that your other gates are most vulnerable to. The cost of keeping it is zero.

---

## Implementation Priority

```
Phase 1 (Current): qa, qa --smart, clean, build, run, smoke
Phase 2A:          omni exec + fingerprint ledger (SQLite, SHA-256, operator gate)
Phase 2B:          Dependency pre-check (import parsing against known-safe list)
Phase 2C:          Agentic greylist (local Gemma via Ollama, temp=0.0, critic mode)
Phase 2D:          ledger list/revoke/blacklist/import commands
Phase 3:           Antigravity native integration (SafeToAutoRun feeds from ledger)
```

---

## Design Constraints

- **No project dependencies.** Omni must run from its own Python install, not any
  project venv. Security tooling that depends on the thing it secures is circular.
- **No network calls in the security gate.** Fingerprint check must be fully local.
  Agentic analysis uses local Gemma only — no cloud API in the exec path.
- **Ledger portability.** `omni ledger import` allows a trusted administrator to seed
  a new machine's whitelist from a known-good source without re-running every script.
- **Audit trail mandatory.** Every exec decision (fast-path or gate) is written to
  `C:\OmniBuilder\omni_audit.jsonl` with timestamp, script hash, decision, and path.
- **Windows as backstop, not target.** Omni is additive over Windows security.
  It does not require any Windows security features to be disabled to function.
