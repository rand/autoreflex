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
    """Hidden widget to manage the websocket connection."""
    
    def __init__(self, log_widget: RichLog, base_url: str = "ws://localhost:8000/ws"):
        super().__init__()
        self.log_widget = log_widget
        self.base_url = base_url
        self.running = True

    @work(exclusive=True)
    async def run_websocket(self) -> None:
        while self.running:
            try:
                async with websockets.connect(self.base_url) as websocket:
                    self.log_widget.write("[green]Connected to log stream...[/]")
                    while self.running:
                        message = await websocket.recv()
                        data = json.loads(message)
                        # Format based on message type
                        if data.get("type") == "log":
                            content = data.get("content", "")
                            self.log_widget.write(content)
                        elif data.get("type") == "status":
                            # Could emit event to update status, for now just log
                            status = data.get("data", "")
                            self.log_widget.write(f"[blue][STATUS] {status}[/]")
            except Exception as e:
                self.log_widget.write(f"[red]Connection lost: {e}. Retrying in 3s...[/]")
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
                # Hidden worker to drive the logs
                yield LogWorker(log_widget=None) # Will be set in on_mount
        yield Footer()

    def on_mount(self) -> None:
        # Link the worker to the widget explicitly since we created them separately
        log_view = self.query_one("#log-view", RichLog)
        # Re-compose LogWorker properly or just pass it in?
        # Actually, let's just find the worker widget we yielded and set the prop
        # But wait, we can't easily find it by type if it's generic Static.
        # Let's fix the composition.
        pass

    async def on_mount(self) -> None:
        table = self.query_one("#tasks-table", DataTable)
        table.add_columns("ID", "Status", "Prompt", "Created At")
        
        # Initialize LogWorker correctly
        log_view = self.query_one("#log-view", RichLog)
        # We need to remove the placeholder and add the real worker
        # Or better: Just instantiate the worker with the log_view in compose?
        # No, compose is called before nodes exist.
        # Let's just start the worker manually here or use a dedicated method.
        self.run_worker(self.start_log_stream(log_view))
        
        await self.action_refresh_data()

    async def start_log_stream(self, log_widget: RichLog):
        """Worker method to stream logs."""
        url = "ws://localhost:8000/ws"
        while True:
            try:
                async with websockets.connect(url) as websocket:
                    log_widget.write("[green]Connected to log stream...[/]")
                    while True:
                        message = await websocket.recv()
                        data = json.loads(message)
                        if data.get("type") == "log":
                            content = data.get("content", "")
                            log_widget.write(content)
                        elif data.get("type") == "status":
                            # Update status bar if possible?
                            pass
            except Exception:
                # log_widget.write(f"[red]Connection error: {e}[/]")
                await asyncio.sleep(2)

    async def action_refresh_data(self) -> None:
        """Fetch latest data from API."""
        status_data = self.api.get_status()
        status_str = status_data.get("status", "unknown")
        is_running = status_str == "running"
        
        status_label = self.query_one("#agent-status-value", Label)
        status_label.update(status_str.upper())
        status_label.styles.color = "green" if is_running else "yellow"

        history = self.api.get_history()
        table = self.query_one("#tasks-table", DataTable)
        table.clear()
        
        for task in history:
            # Safely handle missing keys if schema changes
            t_id = task.get("id", "N/A")
            t_status = task.get("status", "unknown")
            t_prompt = task.get("prompt", "")[:50] + "..."
            t_date = task.get("created_at", "")
            table.add_row(str(t_id), t_status, t_prompt, str(t_date))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "refresh-btn":
            self.run_worker(self.action_refresh_data())

if __name__ == "__main__":
    app = AutoReflexTUI()
    app.run()
