import asyncio
import json
from typing import List, Dict, Any, Optional

class FibonacciWebSocketInterceptor:
    def __init__(self):
        # Sequence: 1000, 1000, 2000, 3000, 5000, 8000, capped at 8000
        self.fib_sequence = [1000, 1000, 2000, 3000, 5000, 8000]
        self.fib_index = 0
        self.frame_count = 0
        self.mutate_payload = False
        self.corrupted_value = "1e+7"
        self.intercepted_logs: List[str] = []

    def reset(self):
        self.fib_index = 0
        self.frame_count = 0
        self.mutate_payload = False
        self.intercepted_logs.clear()

    def get_next_delay(self) -> int:
        if self.fib_index < len(self.fib_sequence):
            delay = self.fib_sequence[self.fib_index]
            self.fib_index += 1
        else:
            delay = 8000
        return delay

    async def attach_to_page(self, page):
        """Attaches route_web_socket handler to Playwright page."""
        await page.route_web_socket("**/ws", self.handle_websocket_route)
        print("[INTERCEPTOR] Attached WebSocket route handler to Playwright page.")

    def handle_websocket_route(self, ws_route):
        """Playwright route_web_socket handler for frame interception & delay injection."""
        server = ws_route.connect_to_server()

        def on_server_message(message):
            self.frame_count += 1
            delay_ms = self.get_next_delay()
            
            log_str = f"[WS] Frame #{self.frame_count:02d} | Delay: {delay_ms} ms"
            self.intercepted_logs.append(log_str)
            print(log_str)

            # Mutate payload if fault injection is active
            if self.mutate_payload:
                try:
                    if isinstance(message, str):
                        data = json.loads(message)
                        data["balance"] = self.corrupted_value
                        data["status"] = "corrupted"
                        message = json.dumps(data)
                        print(f"[FAULT] Injecting corrupted mathematical state: balance={self.corrupted_value}")
                except Exception as e:
                    print(f"[INTERCEPTOR ERROR] Payload mutation error: {e}")

            # Forward to browser client with injected delay
            asyncio.create_task(self._forward_to_client(ws_route, message, delay_ms))

        server.on_message(on_server_message)
        ws_route.on_message(lambda msg: server.send(msg))

    async def _forward_to_client(self, ws_route, message, delay_ms: int):
        if delay_ms > 0:
            await asyncio.sleep(delay_ms / 1000.0)
        try:
            ws_route.send(message)
        except Exception as e:
            print(f"[INTERCEPTOR] Client send error: {e}")
