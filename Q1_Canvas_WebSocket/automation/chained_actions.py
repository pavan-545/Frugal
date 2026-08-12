import time
import asyncio
from typing import Dict, Any

class RapidChainedActions:
    def __init__(self, page):
        self.page = page

    async def execute_hover_drag_click(self, viewport_x: float, viewport_y: float, drag_distance_x: float = 15.0) -> float:
        """
        Executes rapid Chained Interaction sequence:
        1. Hover to (viewport_x, viewport_y)
        2. Mouse Down & Drag +15px on X-axis
        3. Mouse Up & Click
        Measures and returns total elapsed execution time in ms.
        """
        start_time = time.perf_counter()

        print(f"[ACTION] Hovering to target viewport coordinates: ({viewport_x:.1f}, {viewport_y:.1f})")
        await self.page.mouse.move(viewport_x, viewport_y)

        print(f"[ACTION] MouseDown & Dragging +{drag_distance_x:.1f}px on X-axis...")
        await self.page.mouse.down()
        
        # Intermediate drag steps for smooth mousemove event dispatch
        drag_target_x = viewport_x + drag_distance_x
        await self.page.mouse.move(viewport_x + (drag_distance_x / 2.0), viewport_y)
        await self.page.mouse.move(drag_target_x, viewport_y)

        print(f"[ACTION] MouseUp & Click at drag endpoint ({drag_target_x:.1f}, {viewport_y:.1f})")
        await self.page.mouse.up()
        await self.page.mouse.click(drag_target_x, viewport_y)

        end_time = time.perf_counter()
        elapsed_ms = (end_time - start_time) * 1000.0

        print(f"[ACTION] Rapid Chained Interaction completed: {elapsed_ms:.2f} ms")
        return elapsed_ms
