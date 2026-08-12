import math
from enum import Enum, auto
from typing import Dict, Any, Optional
from automation.detector import CanvasStateDetector
from automation.chained_actions import RapidChainedActions

class CircuitState(Enum):
    READY = auto()
    VALIDATING = auto()
    STALE = auto()
    RECALCULATING = auto()
    EXECUTING = auto()
    SUCCESS = auto()
    ABORTED = auto()

class CanvasCircuitBreaker:
    def __init__(self, page, drift_threshold_px: float = 5.0, max_retries: int = 3):
        self.page = page
        self.drift_threshold_px = drift_threshold_px
        self.max_retries = max_retries
        self.state = CircuitState.READY
        self.detector = CanvasStateDetector()
        self.chained_actions = RapidChainedActions(page)
        self.execution_time_ms = 0.0

    def calculate_distance(self, x1: float, y1: float, x2: float, y2: float) -> float:
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    async def execute_safe_chained_interaction(self, initial_target: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes interaction under Circuit-Breaker protection:
        Pre-validates target coordinates, detects dynamic drift / frame lag,
        recalculates coordinates if stale, and executes rapid chained action safely.
        """
        current_target = initial_target
        attempts = 0

        while attempts < self.max_retries:
            attempts += 1
            self.state = CircuitState.VALIDATING
            print(f"\n[CIRCUIT] Circuit Breaker state: {self.state.name} (Attempt {attempts}/{self.max_retries})")

            # 1. Pre-execution Freshness & Pixel Color Verification
            canvas_x = current_target["canvasX"]
            canvas_y = current_target["canvasY"]
            
            pixel_color = await self.detector.get_current_pixel_color_at(self.page, canvas_x, canvas_y)
            # Active green: G > 200, R < 50, B < 50
            is_color_valid = (pixel_color["g"] > 200 and pixel_color["r"] < 50 and pixel_color["b"] < 50)

            # 2. Re-scan current active position to detect coordinate drift
            fresh_scan = await self.detector.detect_active_target(self.page)
            drift_dist = self.calculate_distance(
                current_target["canvasX"], current_target["canvasY"],
                fresh_scan["canvasX"], fresh_scan["canvasY"]
            )

            if not is_color_valid or drift_dist > self.drift_threshold_px:
                print(f"[RACE] Target moved or stale frame detected!")
                print(f"[CIRCUIT] Stale coordinate detected (Drift delta: {drift_dist:.2f}px > threshold {self.drift_threshold_px}px)")
                self.state = CircuitState.STALE

                # 3. Recalculate Target Coordinates
                self.state = CircuitState.RECALCULATING
                print(f"[CIRCUIT] Recalculating target coordinates via RAF scan...")
                current_target = fresh_scan
                print(f"[CIRCUIT] Target validated at fresh coords: ({current_target['canvasX']:.1f}, {current_target['canvasY']:.1f})")

            else:
                print(f"[CIRCUIT] Target validated (Drift delta: {drift_dist:.2f}px <= threshold {self.drift_threshold_px}px)")
                current_target = fresh_scan

            # 4. Safe Execution of Chained Action
            try:
                self.state = CircuitState.EXECUTING
                print(f"[CIRCUIT] Circuit Breaker state: {self.state.name}")

                vp_x = current_target["viewportX"]
                vp_y = current_target["viewportY"]

                self.execution_time_ms = await self.chained_actions.execute_hover_drag_click(vp_x, vp_y)
                
                # Check if interaction succeeded in canvas application
                success = await self.page.evaluate("window.__canvasState ? window.__canvasState.interactionCompleted : false")
                if success:
                    self.state = CircuitState.SUCCESS
                    print(f"[CIRCUIT] Circuit Breaker state: {self.state.name}")
                    return {
                        "status": "SUCCESS",
                        "attempts": attempts,
                        "execution_time_ms": self.execution_time_ms,
                        "final_target": current_target
                    }
                else:
                    print(f"[CIRCUIT WARNING] Interaction did not set success flag on canvas. Retrying...")
            except Exception as e:
                print(f"[CIRCUIT ERROR] Interaction error: {e}")

        self.state = CircuitState.ABORTED
        print(f"[CIRCUIT] Circuit Breaker state: {self.state.name}")
        raise RuntimeError(f"Circuit breaker failed after {self.max_retries} attempts.")
