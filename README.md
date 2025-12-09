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

The system currently runs in **Simulation Mode** (safe for testing). To turn this into a real power tool for coding with Claude, use the following configuration options. You do **not** need to edit the code.

### A. Enable the Real Actor (Replace Simulator)
To run the actual Claude CLI (or any other command):

1.  Ensure you have the Claude CLI installed: `npm install -g @anthropic-ai/claude-code`.
2.  Set the `AUTOREFLEX_AGENT_CMD` environment variable in `backend/.env`:
    ```bash
    # Example: Run Claude in non-interactive mode
    AUTOREFLEX_AGENT_CMD=["claude", "--non-interactive", "--prompt"]
    ```
    *Note: The prompt text will be appended to this command.*

### B. Enable the Real Optimizer (Connect LLM)
To use a real LLM (via DSPy) for prompt optimization instead of the mock template:

1.  Set `USE_REAL_OPTIMIZER=True` in `backend/.env`.
2.  Ensure you have the necessary API keys set (e.g., `OPENAI_API_KEY`) for DSPy to work.

## 💻 Developer Workflow

We provide a robust CLI tool `cli.py` to manage the development lifecycle.

### 1. Setup
Install dependencies (Backend pip + Frontend npm) and checks your venv. It automatically handles OpenSSL build flags for `grpcio` on macOS.
```bash
./venv/bin/python cli.py setup
```

### 2. TUI (Terminal User Interface)
Run the text-based dashboard to monitor tasks and logs directly in your terminal.
```bash
./venv/bin/python cli.py tui
```

### 3. Background Service (Daemon)
Run AutoReflex as a background service (Systemd on Linux, Launchd on macOS).

```bash
# Generate and install service config
./venv/bin/python cli.py service install

# Check status
./venv/bin/python cli.py service status
```

### 4. Testing
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