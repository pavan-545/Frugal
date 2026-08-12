import asyncio
import json
import math
import os
import sys
from aiohttp import web

class CanvasTestbedServer:
    def __init__(self, host="127.0.0.1", port=8000):
        self.host = host
        self.port = port
        self.app = web.Application()
        self.websockets = set()
        self.step_count = 0
        self.target_base_x = 350
        self.target_base_y = 250
        self.drift_offset = 0
        self.current_state = "loading"
        self.interaction_success = False
        self.setup_routes()

    def setup_routes(self):
        # Serve static HTML/JS files
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        self.app.router.add_static("/static/", static_dir, name="static")
        self.app.router.add_get("/", self.handle_index)
        self.app.router.add_get("/ws", self.handle_websocket)

    async def handle_index(self, request):
        index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
        return web.FileResponse(index_path)

    async def handle_websocket(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.websockets.add(ws)
        print(f"[SERVER] Client connected to WebSocket from {request.remote}")

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    print(f"[SERVER] Received client msg: {data}")
                    if data.get("type") == "interaction_result":
                        if data.get("success"):
                            self.interaction_success = True
                            print("[SERVER] Interaction verified successfully by client!")
                            await ws.send_json({"type": "ack", "status": "SUCCESS"})
                elif msg.type == web.WSMsgType.ERROR:
                    print(f"[SERVER] WebSocket connection closed with exception {ws.exception()}")
        finally:
            self.websockets.remove(ws)
            print("[SERVER] Client disconnected")

        return ws

    async def broadcast_loop(self):
        """Broadcasts state frames over WebSocket."""
        while True:
            await asyncio.sleep(0.5)
            if not self.websockets:
                continue

            self.step_count += 1
            
            # First 2 steps are 'loading' (gray state)
            if self.step_count <= 2:
                self.current_state = "loading"
                payload = {
                    "step": self.step_count,
                    "status": "loading",
                    "target": {
                        "x": self.target_base_x,
                        "y": self.target_base_y,
                        "w": 100,
                        "h": 60,
                        "color": "rgb(128,128,128)" # Loading gray
                    },
                    "balance": 1000.0
                }
            else:
                self.current_state = "active"
                # Dynamic drift calculation on active state: target moves 4px per step
                self.drift_offset = (self.step_count - 2) * 4
                curr_x = self.target_base_x + self.drift_offset
                payload = {
                    "step": self.step_count,
                    "status": "active",
                    "target": {
                        "x": curr_x,
                        "y": self.target_base_y,
                        "w": 100,
                        "h": 60,
                        "color": "rgb(0,255,0)" # Active target green
                    },
                    "balance": 1250.50
                }

            # Send payload to all connected clients
            for ws in list(self.websockets):
                try:
                    await ws.send_json(payload)
                except Exception as e:
                    print(f"[SERVER] Error broadcasting to client: {e}")

    async def start(self):
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        print(f"[SERVER] Canvas Testbed running at http://{self.host}:{self.port}")
        asyncio.create_task(self.broadcast_loop())
        return runner

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    server = CanvasTestbedServer()
    loop.run_until_complete(server.start())
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("[SERVER] Shutting down...")
