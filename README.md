# AutoReflex

AutoReflex is a local "Mission Control" for optimizing and automating your interactions with [Claude Code](https://docs.anthropic.com/claude/docs). It implements an **OODA Loop** (Observe, Orient, Decide, Act) workflow to help you write better prompts and execute autonomous coding tasks.

## 🚀 Features

*   **OODA Engine:** Structured workflow to define tasks, optimize prompts using AI strategies (inspired by DSPy), and execute them.
*   **Mission Control Dashboard:** A modern, React-based UI to monitor your autonomous agents in real-time.
*   **Live Log Streaming:** Watch Claude's internal "thought process" and CLI outputs via WebSockets.
*   **History Tracking:** Keep a local database of all your tasks, prompt iterations, and outcomes.
*   **Local First:** Fully Dockerized. Your data stays on your machine.

## 🛠️ Architecture

*   **Backend:** Python (FastAPI), SQLAlchemy (SQLite), Alembic (Migrations).
*   **Frontend:** React, TypeScript, Vite, Tailwind CSS, Custom Hooks architecture.
*   **Core Pattern:** Actor-Observer-Optimizer.
    *   **Optimizer:** Refines prompts using AI strategies.
    *   **Actor:** Executes the agent in a subprocess, writing logs to the DB.
    *   **Observer:** Event-driven monitor that streams DB logs to the Frontend via WebSockets.

## 🎮 Daily Operation (The "Happy Path")

You now have a robust local dashboard to manage autonomous tasks.

**1. Start the System**
```bash
./venv/bin/python cli.py start
```
> **Pro Tip:** Keep this terminal open. It runs both the Backend (API/Database) and Frontend (UI).

**2. Execute the OODA Loop**
*   **Observe (Input):** Go to [http://localhost:5173](http://localhost:5173). In the "Observation Phase" box, type a raw, messy objective.
*   **Orient (Optimize):** Click **"Analyze & Optimize"**. The system will restructure your request into a clear "Flight Plan".
*   **Decide (Review):** Read the generated prompt. Does it capture your intent?
*   **Act (Execute):** Click **"Execute OODA Loop"**. The "Actor" spins up, and the "Observer" streams real-time logs.

---

## ⚡ Level Up: Making it "Real"

The system currently runs in **Simulation Mode** (safe for testing). To turn this into a real power tool for coding with Claude, unlock these components:

### A. Enable the Real Actor (Replace Simulator)
Currently, `backend/app/core/actor.py` runs `simulator.py` which just prints fake logs. To run the actual Claude CLI:

1.  Ensure you have the Claude CLI installed: `npm install -g @anthropic-ai/claude-code`.
2.  Edit `backend/app/core/actor.py`:
    *   Find the `cmd` list construction in `start_task`.
    *   Replace the simulator command with the real CLI command.
    ```python
    # OLD (Simulator)
    # cmd = [sys.executable, "app/core/simulator.py", "--prompt", prompt]

    # NEW (Real Agent) - Example
    # Ensure 'claude' is in your PATH, or provide full path
    cmd = ["claude", "--prompt", prompt, "--non-interactive"]
    ```

### B. Enable the Real Optimizer (Connect LLM)
Currently, `backend/app/core/optimizer.py` uses a hardcoded template. To use AI to write better prompts:

1.  Uncomment `dspy` in `backend/requirements.txt` and reinstall (`./venv/bin/python cli.py setup`).
2.  Edit `backend/app/core/optimizer.py` to configure a real Language Model (e.g., OpenAI `gpt-4o` or Anthropic `claude-3-opus`).

---

## 💻 Developer Workflow

We provide a robust CLI tool `cli.py` to manage the development lifecycle without needing Docker.

### 1. Setup
Install dependencies (Backend pip + Frontend npm) and checks your venv. It automatically handles OpenSSL build flags for `grpcio` on macOS.
```bash
./venv/bin/python cli.py setup
```

### 2. Testing
Run the full suite. It checks types (mypy), logic (unit tests), and integration (E2E).
```bash
./venv/bin/python cli.py test
```

### 3. Database Migrations
The project uses Alembic. If you modify `backend/app/database.py` (e.g., adding a `cost` field to `Run`), you must generate a migration.

```bash
# Generate a migration
cd backend && ../venv/bin/alembic revision --autogenerate -m "add cost field"

# Apply migrations
cd backend && ../venv/bin/alembic upgrade head
```

### 4. Configuration
Adjust settings without touching code by editing `backend/app/config.py` or creating a `.env` file in the `backend/` directory:
```bash
LOG_LEVEL=DEBUG
CORS_ORIGINS=["http://localhost:5173"]
```

## 🤝 Credits

Inspired by:
*   [catsyphon](https://github.com/kulesh/catsyphon)
*   [dspydantic](https://github.com/davidberenstein1957/dspydantic)
*   [continuous-claude](https://github.com/AnandChowdhary/continuous-claude)