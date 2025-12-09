import httpx
import logging
from typing import List, Optional, Dict, Any

# Configure logging to a file since stdout is used by the TUI
logging.basicConfig(filename='tui_debug.log', level=logging.INFO)
logger = logging.getLogger(__name__)

class AutoReflexAPI:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.client = httpx.Client(base_url=self.base_url, timeout=5.0)

    def check_health(self) -> bool:
        try:
            response = self.client.get("/status")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        try:
            response = self.client.get("/status")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get status failed: {e}")
            return {"is_running": False, "active_task_id": None}

    def get_history(self) -> List[Dict[str, Any]]:
        try:
            response = self.client.get("/history")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Get history failed: {e}")
            return []

    def start_task(self, prompt: str) -> Optional[int]:
        try:
            response = self.client.post("/start", json={"prompt": prompt})
            response.raise_for_status()
            return response.json().get("task_id")
        except Exception as e:
            logger.error(f"Start task failed: {e}")
            return None

    def stop_agent(self) -> bool:
        try:
            response = self.client.post("/stop")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Stop agent failed: {e}")
            return False
