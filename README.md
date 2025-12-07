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

## 💻 Development

We provide a robust CLI tool to manage the development lifecycle.

### Prerequisites
*   Python 3.14+
*   Node.js & npm

### Quick Start

1.  **Setup:** Install dependencies and initialize the environment.
    ```bash
    ./venv/bin/python cli.py setup
    ```

2.  **Start:** Run the full stack (Backend + Frontend).
    ```bash
    ./venv/bin/python cli.py start
    ```
    Access the dashboard at [http://localhost:5173](http://localhost:5173).

3.  **Test:** Run Backend Unit Tests, Frontend Component Tests, and End-to-End Verification.
    ```bash
    ./venv/bin/python cli.py test
    ```

### Database Migrations

The project uses Alembic for database migrations.

```bash
# Apply migrations
cd backend && ../venv/bin/alembic upgrade head

# Create a new migration (after model changes)
cd backend && ../venv/bin/alembic revision --autogenerate -m "Description"
```

## 🔧 Configuration

*   **Logs:** Stored in `backend/autoreflex.db` (Log table).
*   **Settings:** Managed via `backend/app/config.py`. Environment variables can be set in a `.env` file in `backend/`.

## 🤝 Credits

Inspired by:
*   [catsyphon](https://github.com/kulesh/catsyphon)
*   [dspydantic](https://github.com/davidberenstein1957/dspydantic)
*   [continuous-claude](https://github.com/AnandChowdhary/continuous-claude)
