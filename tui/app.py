from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Static, DataTable, TabbedContent, TabPane, RichLog, Button, Input, Label
from textual.worker import Worker, WorkerState
from textual.reactive import reactive
from textual import work
import asyncio
import websockets
import json
from datetime import datetime

from .api import AutoReflexAPI

class LogWorker(Static):
    """Hidden widget to manage the websocket connection and stream updates."""
    
    def __init__(self, base_url: str = "ws://localhost:8000/ws"):
        super().__init__()
        self.base_url = base_url
        self.running = True

    @work(exclusive=True)
    async def run_websocket(self) -> None:
        log_view = self.app.query_one("#log-view", RichLog)
        status_label = self.app.query_one("#agent-status-value", Label)

        while self.running:
            try:
                async with websockets.connect(self.base_url) as websocket:
                    log_view.write("[green]Connected to log stream...[/]")
                    while self.running:
                        message = await websocket.recv()
                        data = json.loads(message)
                        
                        # Format based on message type
                        if data.get("type") == "log":
                            content = data.get("content", "")
                            log_view.write(content)
                        elif data.get("type") == "status":
                            status = data.get("data", "unknown")
                            log_view.write(f"[blue][STATUS] {status}[/]")
                            
                            # Update the dashboard status label as well
                            is_running = status == "running"
                            status_label.update(status.upper())
                            status_label.styles.color = "green" if is_running else "yellow"

            except Exception as e:
                log_view.write(f"[red]Connection lost: {e}. Retrying in 3s...[/]")
                await asyncio.sleep(3)

    def on_mount(self) -> None:
        self.run_websocket()

    def on_unmount(self) -> None:
        self.running = False

class Dashboard(Container):
    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal(classes="status-bar"):
                yield Label("Agent Status: ", classes="status-label")
                yield Label("Unknown", id="agent-status-value")
                yield Button("Refresh", id="refresh-btn", variant="primary")
            
            yield Label("Recent Tasks", classes="section-title")
            yield DataTable(id="tasks-table")

class AutoReflexTUI(App):
    CSS = """
    .status-bar {
        height: 3;
        margin: 1;
        background: $surface;
        padding: 1;
        align-vertical: middle;
    }
    .status-label {
        text-style: bold;
    }
    #agent-status-value {
        width: 1fr;
        color: $success;
    }
    .section-title {
        margin: 1;
        text-style: bold;
        color: $accent;
    }
    RichLog {
        background: $surface;
        border: solid $primary;
        height: 1fr;
    }
    DataTable {
        height: 1fr;
        border: solid $primary;
    }
    """

    BINDINGS = [("q", "quit", "Quit"), ("r", "refresh_data", "Refresh")]

    def __init__(self):
        super().__init__()
        self.api = AutoReflexAPI()

    def compose(self) -> ComposeResult:
        yield Header()
        with TabbedContent():
            with TabPane("Dashboard", id="tab-dashboard"):
                yield Dashboard()
            with TabPane("Live Logs", id="tab-logs"):
                yield RichLog(id="log-view", highlight=True, markup=True)
        
        # Worker is invisible but part of the tree to access app context
        yield LogWorker()
        yield Footer()

    async def on_mount(self) -> None:
        table = self.query_one("#tasks-table", DataTable)
        table.add_columns("ID", "Status", "Prompt", "Created At")
        
        # Initial data fetch
        await self.action_refresh_data()

    async def action_refresh_data(self) -> None:
        """Fetch latest data from API."""
        # 1. Status
        status_data = self.api.get_status()
        status_str = status_data.get("status", "unknown")
        is_running = status_str == "running"
        
        status_label = self.query_one("#agent-status-value", Label)
        status_label.update(status_str.upper())
        status_label.styles.color = "green" if is_running else "yellow"

        # 2. History
        history = self.api.get_history()
        table = self.query_one("#tasks-table", DataTable)
        table.clear()
        
        for task in history:
            t_id = task.get("id", "N/A")
            t_status = task.get("status", "unknown")
            t_prompt = task.get("description", "")[:50] + "..." # Note: API uses 'description' usually, let's check schema
            # Fallback if 'prompt' was used in some versions, but TaskRequest has 'description'
            if not task.get("description") and task.get("prompt"):
                 t_prompt = task.get("prompt", "")[:50] + "..."

            t_date = task.get("created_at", "")
            table.add_row(str(t_id), t_status, t_prompt, str(t_date))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh-btn":
            self.run_worker(self.action_refresh_data())

if __name__ == "__main__":
    app = AutoReflexTUI()
    app.run()