import os
from typing import Dict, Any

class CanvasStateDetector:
    def __init__(self):
        script_path = os.path.join(os.path.dirname(__file__), "scripts", "canvas_detector.js")
        with open(script_path, "r", encoding="utf-8") as f:
            self.detector_script = f.read()

    async def detect_active_target(self, page, timeout_ms: int = 15000) -> Dict[str, Any]:
        """
        Executes requestAnimationFrame-based Canvas pixel detector.
        Waits until canvas transitions to active state and returns target coordinates.
        """
        print("[CANVAS] Running requestAnimationFrame pixel state detector...")
        result = await page.evaluate(self.detector_script)
        
        if result and result.get("detected"):
            canvas_x = result["canvasX"]
            canvas_y = result["canvasY"]
            vp_x = result["viewportX"]
            vp_y = result["viewportY"]
            print(f"[CANVAS] Active state detected via RAF getImageData()!")
            print(f"[CANVAS] Target canvas center: ({canvas_x:.1f}, {canvas_y:.1f}), Viewport: ({vp_x:.1f}, {vp_y:.1f})")
            return result
        else:
            raise RuntimeError("Canvas active state detection failed or returned invalid data.")

    async def get_current_pixel_color_at(self, page, canvas_x: float, canvas_y: float) -> Dict[str, int]:
        """
        Quickly inspects pixel color at canvas coordinates using getImageData.
        Used by Circuit Breaker to validate coordinate freshness pre-interaction.
        """
        js_code = f"""
        (function() {{
            const canvas = document.getElementById('app-canvas');
            if (!canvas) return null;
            const ctx = canvas.getContext('2d');
            const imageData = ctx.getImageData(Math.floor({canvas_x}), Math.floor({canvas_y}), 1, 1);
            return {{
                r: imageData.data[0],
                g: imageData.data[1],
                b: imageData.data[2],
                a: imageData.data[3]
            }};
        }})()
        """
        color = await page.evaluate(js_code)
        return color or {"r": 0, "g": 0, "b": 0, "a": 0}
