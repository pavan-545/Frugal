import asyncio
import pytest
import pytest_asyncio
import sys
import os
import socket

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from testbed.server import CanvasTestbedServer
from playwright.async_api import async_playwright

def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

@pytest_asyncio.fixture(scope="function")
async def testbed_server():
    port = get_free_port()
    server = CanvasTestbedServer(host="127.0.0.1", port=port)
    runner = await server.start()
    yield server
    await runner.cleanup()

@pytest_asyncio.fixture(scope="function")
async def browser_page(testbed_server):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1024, "height": 768})
        page = await context.new_page()
        page.server_port = testbed_server.port
        yield page
        await context.close()
        await browser.close()
