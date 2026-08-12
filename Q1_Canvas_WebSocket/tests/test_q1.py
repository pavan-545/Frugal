import pytest
import asyncio
from automation.interceptor import FibonacciWebSocketInterceptor
from automation.detector import CanvasStateDetector
from automation.circuit_breaker import CanvasCircuitBreaker

@pytest.mark.asyncio
async def test_canvas_websocket_fibonacci_jitter_and_race_interaction(browser_page):
    """
    Test A: Validates WebSocket stream interception with Fibonacci delay,
    RAF canvas pixel state detection (loading -> active), circuit-breaker coordinate recalculation
    under dynamic drift, and rapid chained interaction execution (Hover -> Drag 15px -> Click).
    """
    print("\n" + "=" * 50)
    print("Q1 - DYNAMIC CANVAS AUTOMATION (TEST A)")
    print("=" * 50)

    port = browser_page.server_port
    url = f"http://127.0.0.1:{port}"

    # 1. Attach WebSocket Interceptor & Fibonacci Jitter Engine
    interceptor = FibonacciWebSocketInterceptor()
    await interceptor.attach_to_page(browser_page)

    # 2. Navigate to local canvas application
    await browser_page.goto(url, wait_until="commit")
    print(f"[CANVAS] Page loaded on port {port}. Inspecting initial loading state...")

    # Wait for canvas element to mount
    await browser_page.wait_for_selector("#app-canvas")

    # 3. RAF Pixel-State Detector Engine: Scan for transition from gray loading to active target green
    detector = CanvasStateDetector()
    target_info = await detector.detect_active_target(browser_page)

    assert target_info["detected"] is True
    assert target_info["state"] == "active"
    print(f"[CANVAS] Target coordinate: ({target_info['canvasX']:.1f}, {target_info['canvasY']:.1f})")

    # Verify Fibonacci interceptor logged frame delays
    assert len(interceptor.intercepted_logs) > 0, "No WebSocket frames were intercepted!"
    print(f"[WS] Total intercepted frames during stream: {len(interceptor.intercepted_logs)}")

    # 4. Circuit Breaker Protection & Dynamic Drift Interaction
    circuit_breaker = CanvasCircuitBreaker(browser_page, drift_threshold_px=5.0, max_retries=3)
    result = await circuit_breaker.execute_safe_chained_interaction(target_info)

    # Assert Circuit Breaker execution success
    assert result["status"] == "SUCCESS"
    assert result["execution_time_ms"] > 0
    print(f"[ACTION] Interaction completed: {result['execution_time_ms']:.2f} ms")

    # Assert client canvas app state recorded interaction completion
    final_completed = await browser_page.evaluate("window.__canvasState.interactionCompleted")
    assert final_completed is True, "Client canvas application failed to record completed interaction!"

    print("\n" + "=" * 50)
    print("Q1 TEST A RESULT: PASS")
    print("=" * 50)


@pytest.mark.asyncio
async def test_corrupted_mathematical_state_boundary(browser_page):
    """
    Test B: Intercepts WebSocket stream and injects a corrupted mathematical state (balance: "1e+7").
    Asserts that the frontend validation layer catches the corruption, activates the UI Error Boundary,
    and prevents application state corruption or crash.
    """
    print("\n" + "=" * 50)
    print("Q1 - FAULT INJECTION & BOUNDARY CHECKING (TEST B)")
    print("=" * 50)

    port = browser_page.server_port
    url = f"http://127.0.0.1:{port}"

    # 1. Attach Interceptor and enable fault injection
    interceptor = FibonacciWebSocketInterceptor()
    interceptor.mutate_payload = True
    interceptor.corrupted_value = "1e+7"
    await interceptor.attach_to_page(browser_page)

    # 2. Navigate to page
    await browser_page.goto(url, wait_until="commit")
    print(f"[FAULT] Injecting corrupted mathematical state ('1e+7') on port {port}...")

    # 3. Wait for UI Error Boundary element to become visible
    error_boundary = await browser_page.wait_for_selector("#error-boundary:not(.hidden)", timeout=15000)
    assert error_boundary is not None, "UI Error Boundary element was not triggered!"

    error_msg = await browser_page.inner_text("#error-message")
    print(f"[BOUNDARY] Structured error message caught: '{error_msg}'")
    assert "CORRUPTED_MATHEMATICAL_STATE" in error_msg or "1e+7" in error_msg

    # 4. Assert that corrupted scientific-notation string was NOT set as numerical active balance
    app_balance = await browser_page.evaluate("window.__canvasState.balance")
    print(f"[BOUNDARY] Preserved application balance: {app_balance}")
    assert app_balance != "1e+7"
    assert isinstance(app_balance, (int, float))

    error_state = await browser_page.evaluate("window.__canvasState.errorState")
    assert error_state is True, "Application failed to register error state boundary flag!"

    print("[BOUNDARY] Invalid state rejected")
    print("[BOUNDARY] Application state preserved")
    print("\n" + "=" * 50)
    print("Q1 TEST B RESULT: PASS")
    print("=" * 50)
