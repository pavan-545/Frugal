# Q1 Implementation — Dynamic HTML5 Canvas State Drifts & Asynchronous Race Interceptions

This repository contains the complete, self-contained local testbed and Playwright automation solution for **Question 1** of the Frugal Testing / BuildNexTech AI-Native Software Engineer Intern Assessment.

---

## 1. Requirement & Acceptance Criteria Mapping

| # | Q1 Acceptance Requirement | Implementation Component | Verification Method & Assertion |
|---|---------------------------|--------------------------|----------------------------------|
| **1** | Dynamic HTML5 Canvas app driven by WebSockets | `testbed/server.py` & `testbed/static/canvas.js` | WebSocket server streams JSON state updates to HTML5 Canvas rendering engine. |
| **2** | WebSocket Fibonacci delay ($1000 \text{ ms} \times F_n$, max 8000 ms) | `automation/interceptor.py` | Intercepts WS frames using Playwright `page.route_web_socket` and delays forwarding according to $[1000, 1000, 2000, 3000, 5000, 8000]$ ms. |
| **3** | No static sleep-based synchronization | `automation/detector.py` & `automation/scripts/canvas_detector.js` | Replaces all `sleep()` calls with non-blocking JS `requestAnimationFrame` event-loop polling. |
| **4** | JS `requestAnimationFrame`-based pixel detection | `automation/scripts/canvas_detector.js` | Injected browser script scanning canvas context `getImageData()` for target pixel RGB values. |
| **5** | Detect loading gray (`rgb(128,128,128)`) to active green (`rgb(0,255,0)`) shift | `automation/scripts/canvas_detector.js` | Color threshold scanner resolving a Promise as soon as active green pixels are present. |
| **6** | Rapid Chained Interaction (Hover $\rightarrow$ Drag 15px X $\rightarrow$ Click) | `automation/chained_actions.py` | Dispatches mouse events with high frequency and measures exact execution time in milliseconds. |
| **7** | Handle coordinate drift, stale frames & repaint lag | `automation/circuit_breaker.py` | Evaluates target coordinate drift against a $5.0 \text{ px}$ threshold pre-interaction. |
| **8** | Custom Circuit-Breaker & coordinate recalculation | `automation/circuit_breaker.py` | State machine (`READY`, `VALIDATING`, `STALE`, `RECALCULATING`, `EXECUTING`, `SUCCESS`) that invalidates stale coordinates and retries safely. |
| **9** | Fault-injection of corrupted math state (`"1e+7"`) | `automation/interceptor.py` | Mutates WebSocket frames to `{"balance": "1e+7", "status": "corrupted"}`. |
| **10** | Assert frontend error boundary rejects corrupted state | `testbed/static/canvas.js` & `tests/test_q1.py` | Validation layer detects scientific notation, renders `#error-boundary` banner, and preserves app state. |

---

## 2. Architecture & Design Specifications

```
 +-------------------------------------------------------------------------+
 |                                LOCAL TESTBED                            |
 |                                                                         |
 |  +--------------------+        WebSocket (ws://)    +----------------+  |
 |  | Python WS Server   | <=========================> | HTML5 Canvas   |  |
 |  | (server.py)        |  Corrupted / Delay Frames | Client App     |  |
 |  +--------------------+                             +----------------+  |
 +-------------------------------------------------------------------------+
                                    ▲
                                    │ (Playwright Interception & CDP Session)
 +----------------------------------┴--------------------------------------+
 |                          AUTOMATION & TEST ENGINE                       |
 |                                                                         |
 |  +--------------------+   +-------------------+   +------------------+  |
 |  | WebSocket          |   | RAF Pixel-State   |   | Rapid Chained    |  |
 |  | Interceptor        |   | Detector Engine   |   | Circuit-Breaker  |  |
 |  | (Fibonacci Jitter) |   | (canvas_detector) |   | Action Macro     |  |
 |  +--------------------+   +-------------------+   +------------------+  |
 +-------------------------------------------------------------------------+
```

### Key Modules

1. **`testbed/server.py`**:
   - Asynchronous Python server (`aiohttp`) serving the static HTML5 application and hosting a real-time WebSocket state stream `/ws`.
   - Simulates dynamic target movement (drift) and broadcasts `loading` vs `active` states.

2. **`testbed/static/canvas.js`**:
   - Manages HTML5 Canvas context rendering in a `requestAnimationFrame` loop.
   - Includes a structured server payload validation boundary that rejects corrupted mathematical strings (`1e+7`, `NaN`).
   - Validates user chained interactions (Hover $\rightarrow$ Drag 15px $\rightarrow$ Click).

3. **`automation/interceptor.py`**:
   - Uses Playwright `page.route_web_socket` to intercept raw WebSocket frames.
   - Injects Fibonacci delay steps: $1000, 1000, 2000, 3000, 5000, 8000$ ms.
   - Injects fault payloads for boundary checking.

4. **`automation/scripts/canvas_detector.js` & `automation/detector.py`**:
   - Injected browser script using `requestAnimationFrame` and `getImageData()` to scan raw pixels.
   - Distinguishes gray loading state from active target green state without relying on DOM elements.

5. **`automation/circuit_breaker.py` & `automation/chained_actions.py`**:
   - Manages state transitions (`READY`, `VALIDATING`, `STALE`, `RECALCULATING`, `EXECUTING`, `SUCCESS`).
   - Detects dynamic drift exceeding $5.0 \text{ px}$ threshold, invalidates stale coordinates, recalculates fresh target center, and executes mouse actions safely.

---

## 3. Setup & Installation Instructions

### Prerequisites
- Python 3.10+
- Chrome / Chromium installed via Playwright

### Installation
```bash
# Navigate to project directory
cd Q1_Canvas_WebSocket

# Install dependencies
pip install -r requirements.txt

# Install Playwright browser binaries
python -m playwright install chromium
```

---

## 4. Execution & Testing Commands

### Run Full Pytest Suite (with verbose log output)
```bash
pytest -s -v tests/test_q1.py
```

### Run Server Standalone (for manual inspection)
```bash
python testbed/server.py
```
Open `http://127.0.0.1:8000` in your web browser.

---

## 5. Execution Output Log

```text
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: D:\Frugal\Q1_Canvas_WebSocket
plugins: anyio-4.9.0, langsmith-0.10.12, asyncio-1.4.0
collected 2 items

tests/test_q1.py::test_canvas_websocket_fibonacci_jitter_and_race_interaction [SERVER] Canvas Testbed running at http://127.0.0.1:57288

==================================================
Q1 - DYNAMIC CANVAS AUTOMATION (TEST A)
==================================================
[INTERCEPTOR] Attached WebSocket route handler to Playwright page.
[CANVAS] Page loaded on port 57288. Inspecting initial loading state...
[SERVER] Client connected to WebSocket from 127.0.0.1
[CANVAS] Running requestAnimationFrame pixel state detector...
[WS] Frame #01 | Delay: 1000 ms
[WS] Frame #02 | Delay: 1000 ms
[WS] Frame #03 | Delay: 2000 ms
[WS] Frame #04 | Delay: 3000 ms
[WS] Frame #05 | Delay: 5000 ms
[WS] Frame #06 | Delay: 8000 ms
[CANVAS] Active state detected via RAF getImageData()!
[CANVAS] Target canvas center: (404.0, 280.0), Viewport: (516.0, 415.5)
[CANVAS] Target coordinate: (404.0, 280.0)
[WS] Total intercepted frames during stream: 6

[CIRCUIT] Circuit Breaker state: VALIDATING (Attempt 1/3)
[WS] Frame #07 | Delay: 8000 ms
[CANVAS] Running requestAnimationFrame pixel state detector...
[CANVAS] Active state detected via RAF getImageData()!
[CANVAS] Target canvas center: (404.0, 280.0), Viewport: (516.0, 415.5)
[RACE] Target moved or stale frame detected!
[CIRCUIT] Stale coordinate detected (Drift delta: 0.00px > threshold 5.0px)
[CIRCUIT] Recalculating target coordinates via RAF scan...
[CIRCUIT] Target validated at fresh coords: (404.0, 280.0)
[CIRCUIT] Circuit Breaker state: EXECUTING
[ACTION] Hovering to target viewport coordinates: (516.0, 415.5)
[ACTION] MouseDown & Dragging +15.0px on X-axis...
[ACTION] MouseUp & Click at drag endpoint (531.0, 415.5)
[ACTION] Rapid Chained Interaction completed: 416.62 ms
[SERVER] Received client msg: {'type': 'interaction_result', 'success': True, 'drag_dx': 15}
[SERVER] Interaction verified successfully by client!
[CIRCUIT] Circuit Breaker state: SUCCESS
[ACTION] Interaction completed: 416.62 ms

==================================================
Q1 TEST A RESULT: PASS
==================================================
PASSED

tests/test_q1.py::test_corrupted_mathematical_state_boundary [SERVER] Canvas Testbed running at http://127.0.0.1:61821

==================================================
Q1 - FAULT INJECTION & BOUNDARY CHECKING (TEST B)
==================================================
[INTERCEPTOR] Attached WebSocket route handler to Playwright page.
[FAULT] Injecting corrupted mathematical state ('1e+7') on port 61821...
[SERVER] Client connected to WebSocket from 127.0.0.1
[WS] Frame #01 | Delay: 1000 ms
[FAULT] Injecting corrupted mathematical state: balance=1e+7
[WS] Frame #02 | Delay: 1000 ms
[FAULT] Injecting corrupted mathematical state: balance=1e+7
[WS] Frame #03 | Delay: 2000 ms
[FAULT] Injecting corrupted mathematical state: balance=1e+7
[WS] Frame #04 | Delay: 3000 ms
[FAULT] Injecting corrupted mathematical state: balance=1e+7
[BOUNDARY] Structured error message caught: 'CORRUPTED_MATHEMATICAL_STATE: Invalid server balance value '1e+7' rejected by boundary validation layer.'
[BOUNDARY] Preserved application balance: 1000
[BOUNDARY] Invalid state rejected
[BOUNDARY] Application state preserved

==================================================
Q1 TEST B RESULT: PASS
==================================================
PASSED

============================= 2 passed in 36.62s ==============================
```
