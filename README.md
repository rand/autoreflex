# AutoReflex

AutoReflex is a local "Mission Control" for optimizing and automating your interactions with [Claude Code](https://docs.anthropic.com/claude/docs). It implements an **OODA Loop** (Observe, Orient, Decide, Act) workflow to help you write better prompts and execute autonomous coding tasks.

## 🚀 Features

*   **OODA Engine:** Structured workflow to define tasks, optimize prompts using AI strategies (inspired by DSPy), and execute them.
*   **Mission Control Dashboard:** A modern, React-based UI to monitor your autonomous agents in real-time.
*   **Live Log Streaming:** Watch Claude's internal "thought process" and CLI outputs via WebSockets.
*   **History Tracking:** Keep a local database of all your tasks, prompt iterations, and outcomes.
*   **Local First:** Fully Dockerized. Your data stays on your machine.

## 🛠️ Architecture

*   **Backend:** Python (FastAPI), SQLAlchemy (SQLite), Watchdog (File Monitoring).
*   **Frontend:** React, TypeScript, Tailwind CSS, Shadcn/UI (simulated), WebSockets.
*   **Infrastructure:** Docker Compose.

## 🏁 Getting Started

### Prerequisites

*   Docker & Docker Compose
*   (Optional) A local installation of `claude` CLI if you want to run the real agent (default is simulation mode).

### Installation

1.  Clone the repository.
2.  Start the stack:

```bash
docker-compose up --build
```

3.  Open the dashboard: [http://localhost:5173](http://localhost:5173)
4.  Open the API docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 🔧 Configuration

*   **Logs:** By default, the app looks for logs in `~/.claude`. You can mount this volume in `docker-compose.yml`.
*   **Agent Execution:** Currently runs in "Simulation Mode" for safety. To enable real execution, edit `backend/app/core/actor.py`.

## 💻 Development

If you prefer to run locally without Docker:

### Backend Setup

1.  Navigate to `backend/`.
2.  Create a virtual environment: `python3.14 -m venv ../venv`
3.  Activate it: `source ../venv/bin/activate`
4.  Install dependencies: `pip install -r requirements.txt`
5.  Run the server: `uvicorn app.main:app --reload`

### Frontend Setup

1.  Navigate to `frontend/`.
2.  Install dependencies: `npm install`
3.  Start the dev server: `npm run dev`

## 🧪 Testing

### Unit Tests

*   **Backend:**
    ```bash
    # From project root (with venv activated)
    pytest backend/tests
    ```
*   **Frontend:**
    ```bash
    # From frontend/ directory
    npm test
    ```

### End-to-End Verification

A utility script is provided to verify the backend API flow (Health -> Optimize -> Run -> Status).

```bash
# From project root (with venv activated)
python verify_e2e.py
```
This script handles starting and stopping the backend server automatically.

## 🤝 Credits

Inspired by:
*   [catsyphon](https://github.com/kulesh/catsyphon)
*   [dspydantic](https://github.com/davidberenstein1957/dspydantic)
*   [continuous-claude](https://github.com/AnandChowdhary/continuous-claude)
