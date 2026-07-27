import os
import sys
import shutil
import subprocess
import argparse
import logging
from pathlib import Path

def setup_logger():
    log_file = os.path.join(os.getcwd(), "build_pipeline.log")
    logger = logging.getLogger()
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s[%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(
                open(sys.stdout.fileno(), mode="w", encoding="utf-8", closefd=False)
            ),
        ]
    )

def get_project_name():
    return Path(os.getcwd()).name

def get_entry_point():
    for candidate in ["maccre.py", "run.py", "main.py", "app.py", f"{get_project_name()}.py"]:
        if os.path.exists(candidate):
            return candidate
    logging.error("No entry point found (maccre.py, run.py, main.py, app.py). Cannot proceed.")
    sys.exit(1)

def resolve_python_engine():
    for venv_name in [".venv", "venv", "env"]:
        py_path = os.path.abspath(os.path.join(venv_name, "Scripts", "python.exe"))
        if os.path.exists(py_path):
            logging.info(f"Auto-detected isolated engine: {py_path}")
            return py_path

    if sys.prefix != sys.base_prefix:
        logging.info(f"Using terminal's active engine: {sys.executable}")
        return sys.executable

    logging.error("FATAL: No .venv found in target directory, and terminal is not activated.")
    sys.exit(1)


def resolve_tool_binary(py_engine: str, tool_name: str) -> list[str]:
    """Resolve a venv tool binary directly, bypassing any npm/node wrapper."""
    venv_scripts = os.path.join(os.path.dirname(os.path.dirname(py_engine)), "Scripts")
    # Windows: prefer .exe, fallback to .cmd
    for ext in [".exe", ".cmd", ""]:
        candidate = os.path.join(venv_scripts, f"{tool_name}{ext}")
        if os.path.exists(candidate):
            return [candidate]
    # Last resort: python -m <tool>
    return [py_engine, "-m", tool_name]

def enforce_quality_gates(py_engine: str, target: str = ".") -> None:
    logging.info("--- ENFORCING QUALITY GATES ---")

    # ── Ruff: direct binary, full target ──────────────────────────────────────
    ruff_cmd = resolve_tool_binary(py_engine, "ruff")
    logging.info(f"Running Ruff Linter...")
    ruff_result = subprocess.run(
        ruff_cmd + ["check", target],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if ruff_result.returncode != 0:
        logging.error(f"RUFF FAILED:\n{ruff_result.stdout}")
        sys.exit(1)

    # ── Pyright: direct binary, scoped to maccre_core per pyrightconfig ───────
    # We never call `python -m pyright` — that wrapper tries to npm-install
    # a specific pyright version on every cold run and hangs indefinitely.
    pyright_cmd = resolve_tool_binary(py_engine, "pyright")
    # Scope to maccre_core to match the include list in pyrightconfig.json
    # and avoid scanning test stubs with intentional type mismatches.
    pyright_target = "maccre_core" if os.path.isdir("maccre_core") else target
    logging.info(f"Running Pyright Static Type Checker...")
    pyright_result = subprocess.run(
        pyright_cmd + [pyright_target],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if pyright_result.returncode != 0:
        logging.error(f"PYRIGHT FAILED:\n{pyright_result.stdout}")
        sys.exit(1)

    logging.info("Quality gates passed.")

def hunt_zombies(project_name: str) -> None:
    logging.info("Hunting zombies...")
    # Kill compiled binary if it exists (GUI-era artifact — usually a no-op for headless projects)
    os.system(f"taskkill /F /IM {project_name}.exe /T >nul 2>&1")
    # Kill Selenium driver zombies
    os.system("taskkill /F /IM chromedriver.exe /T >nul 2>&1")
    # Kill orphaned swarm worker python processes by cmdline pattern
    # Uses WMIC to match python processes running swarm_worker.py specifically
    os.system('wmic process where "name=\'python.exe\' and commandline like \'%swarm_worker%\'" call terminate >nul 2>&1')


def purge_cache(project_name: str) -> None:
    logging.info("Purging caches...")

    # Build cache dirs — regenerated automatically, safe to delete
    for folder in [".ruff_cache", "build", "dist", "__pycache__"]:
        shutil.rmtree(folder, ignore_errors=True)

    # PyInstaller spec file (project-specific, regenerated on next build)
    if os.path.exists(f"{project_name}.spec"):
        os.remove(f"{project_name}.spec")

    # SQLite WAL/SHM artifacts — safe to remove when no active connections
    for wal_artifact in Path(".").glob("*.db-wal"):
        try:
            wal_artifact.unlink()
            logging.info(f"Removed WAL artifact: {wal_artifact.name}")
        except Exception:
            pass
    for shm_artifact in Path(".").glob("*.db-shm"):
        try:
            shm_artifact.unlink()
        except Exception:
            pass

    # Log cleanup — EXCLUDE LIST approach: only delete logs that are clearly
    # build artifacts. Never delete telemetry or system logs.
    # Excluded (NEVER delete): maccre_system.log, build_pipeline.log, *.telemetry.log
    _LOG_EXCLUDE = {"build_pipeline.log", "maccre_system.log"}
    for log in Path(".").glob("*.log"):
        if log.name in _LOG_EXCLUDE or "telemetry" in log.name:
            continue  # Protected — skip
        try:
            os.remove(log)
            logging.info(f"Removed build log: {log.name}")
        except Exception:
            pass

def compile_binary(project_name, entry_point, py_engine):
    logging.info(f"Compiling {project_name}.exe from {entry_point}...")
    cmd =[
        py_engine, "-m", "PyInstaller",
        "--noconsole", "--onefile", "--windowed",
        "--name", project_name,
        "--clean", entry_point
    ]
    if os.path.exists("assets"):
        cmd.extend(["--add-data", "assets;assets"])
        
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        logging.info(f"SUCCESS: Binary sealed at dist/{project_name}.exe")
    else:
        logging.error(f"COMPILATION FAILED:\n{result.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="OmniBuilder — Sovereign CI/CD for MACCREv2",
    )
    parser.add_argument(
        "command",
        choices=["build", "run", "qa", "clean", "smoke"],
        help="Pipeline action: build | run | qa | clean | smoke",
    )
    parser.add_argument("path", nargs="?", default=".", help="Target project directory or file")
    parser.add_argument(
        "--smart",
        action="store_true",
        help="(qa only) Run Ruff only on git-modified files; Pyright always runs globally",
    )
    args = parser.parse_args()

    target_path = os.path.abspath(args.path)
    if not os.path.exists(target_path):
        print(f"FATAL: Path does not exist -> {target_path}")
        sys.exit(1)

    if os.path.isfile(target_path):
        work_dir = os.path.dirname(target_path)
        qa_target = os.path.basename(target_path)
    else:
        work_dir = target_path
        qa_target = "."

    os.chdir(work_dir)

    setup_logger()
    project_name = get_project_name()
    py_engine = resolve_python_engine()

    if args.command == "clean":
        hunt_zombies(project_name)
        purge_cache(project_name)
        logging.info("Project directory sterilized.")

    elif args.command == "qa":
        enforce_quality_gates(py_engine, qa_target)

    elif args.command == "smoke":
        # Delegates to the canonical smoke test — runs the full swarm machinery
        # end-to-end using the free Gemma API. $0 cost.
        logging.info("--- SMOKE TEST ---")
        result = subprocess.run(
            [py_engine, "-m", "maccre_core.tests.smoke_test"],
            cwd=work_dir,
        )
        sys.exit(result.returncode)

    elif args.command == "build":
        entry_point = get_entry_point()
        hunt_zombies(project_name)
        enforce_quality_gates(py_engine, qa_target)
        purge_cache(project_name)
        compile_binary(project_name, entry_point, py_engine)

    elif args.command == "run":
        entry_point = get_entry_point()
        hunt_zombies(project_name)
        logging.info(f"Launching {entry_point}...")
        subprocess.run([py_engine, entry_point])