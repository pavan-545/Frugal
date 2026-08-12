import os
import socket
import pytest
import pytest_asyncio
from aiohttp import web
from playwright.async_api import async_playwright

def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

@pytest_asyncio.fixture(scope="function")
async def live_server():
    """Starts a local HTTP server serving the Q3 testbed on a dynamic free port."""
    port = find_free_port()
    testbed_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "testbed")
    
    app = web.Application()
    app.router.add_static('/', path=testbed_dir, show_index=True)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '127.0.0.1', port)
    await site.start()
    
    server_url = f"http://127.0.0.1:{port}/index.html"
    yield server_url
    
    await runner.cleanup()

@pytest_asyncio.fixture(scope="function")
async def browser_page(live_server):
    """Launches Playwright headless Chromium and yields a fresh page instance."""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(live_server, wait_until="networkidle")
        yield page
        await context.close()
        await browser.close()
