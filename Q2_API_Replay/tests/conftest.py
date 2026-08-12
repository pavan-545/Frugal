import pytest
import pytest_asyncio
import uvicorn
import socket
import threading
import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mock_server.server import app, reset_server_state
from automation.api_client import TransactionAPIClient

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

class ServerThread(threading.Thread):
    def __init__(self, host: str, port: int):
        super().__init__(daemon=True)
        config = uvicorn.Config(app, host=host, port=port, log_level="warning")
        self.server = uvicorn.Server(config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True

@pytest.fixture(scope="function")
def api_server():
    reset_server_state()
    port = get_free_port()
    thread = ServerThread("127.0.0.1", port)
    thread.start()
    time.sleep(0.5) # Allow server thread to initialize socket
    base_url = f"http://127.0.0.1:{port}"
    yield base_url
    thread.stop()

@pytest.fixture(scope="function")
def api_client(api_server):
    return TransactionAPIClient(base_url=api_server)
