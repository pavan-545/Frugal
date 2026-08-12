// Dynamic HTML5 Canvas Application Script

(function () {
    const canvas = document.getElementById('app-canvas');
    const ctx = canvas.getContext('2d');

    // UI Elements
    const wsStatusEl = document.getElementById('ws-status');
    const appStateEl = document.getElementById('app-state');
    const appBalanceEl = document.getElementById('app-balance');
    const interactionStatusEl = document.getElementById('interaction-status');
    const errorBoundaryEl = document.getElementById('error-boundary');
    const errorMessageEl = document.getElementById('error-message');
    const successBannerEl = document.getElementById('success-banner');

    // Application State Object (Exposed for inspection)
    window.__canvasState = {
        status: 'INITIALIZING',
        target: { x: 350, y: 250, w: 100, h: 60, color: 'rgb(128,128,128)' },
        balance: 1000.00,
        interactionCompleted: false,
        errorState: false
    };

    // Interaction tracking state
    let isMouseDown = false;
    let dragStartX = 0;
    let maxDragDx = 0;
    let hoverDetected = false;

    // Connect WebSocket
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        wsStatusEl.textContent = 'CONNECTED';
        wsStatusEl.style.color = '#10b981';
    };

    ws.onclose = () => {
        wsStatusEl.textContent = 'DISCONNECTED';
        wsStatusEl.style.color = '#ef4444';
    };

    ws.onerror = (err) => {
        console.error('[WS Error]', err);
    };

    // Structured Server Payload Validation Layer
    function validateAndProcessPayload(data) {
        // 1. Check for corrupted mathematical state (e.g. "1e+7", scientific notation, NaN, status='corrupted')
        if (data.status === 'corrupted' || (typeof data.balance === 'string' && (data.balance.includes('e') || data.balance.includes('E') || isNaN(Number(data.balance))))) {
            triggerErrorBoundary(`CORRUPTED_MATHEMATICAL_STATE: Invalid server balance value '${data.balance}' rejected by boundary validation layer.`);
            return false;
        }

        // 2. Validate numeric balance boundaries
        const numBalance = Number(data.balance);
        if (!isFinite(numBalance) || numBalance < 0) {
            triggerErrorBoundary(`BOUNDARY_VIOLATION: Negative or infinite balance value '${data.balance}' rejected.`);
            return false;
        }

        // Hide error boundary if valid state payload
        if (window.__canvasState.errorState) {
            clearErrorBoundary();
        }

        // Update application state
        window.__canvasState.status = data.status;
        window.__canvasState.balance = numBalance;
        if (data.target) {
            window.__canvasState.target = data.target;
        }

        // Update UI status displays
        appStateEl.textContent = data.status.toUpperCase();
        appStateEl.style.color = data.status === 'active' ? '#10b981' : '#f59e0b';
        appBalanceEl.textContent = numBalance.toFixed(2);

        return true;
    }

    function triggerErrorBoundary(message) {
        console.warn('[ERROR BOUNDARY TRIGGERED]', message);
        window.__canvasState.errorState = true;
        errorMessageEl.textContent = message;
        errorBoundaryEl.classList.remove('hidden');
        appStateEl.textContent = 'ERROR_BOUNDARY';
        appStateEl.style.color = '#ef4444';
    }

    function clearErrorBoundary() {
        window.__canvasState.errorState = false;
        errorBoundaryEl.classList.add('hidden');
    }

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            validateAndProcessPayload(data);
        } catch (e) {
            triggerErrorBoundary(`MALFORMED_JSON_PAYLOAD: Unparseable WebSocket packet.`);
        }
    };

    // Canvas Rendering Loop via requestAnimationFrame
    function render() {
        // Clear canvas frame
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        // Draw grid lines for dynamic visual inspection
        ctx.strokeStyle = '#334155';
        ctx.lineWidth = 1;
        for (let x = 0; x < canvas.width; x += 50) {
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, canvas.height);
            ctx.stroke();
        }
        for (let y = 0; y < canvas.height; y += 50) {
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(canvas.width, y);
            ctx.stroke();
        }

        // Draw target element from window.__canvasState
        const t = window.__canvasState.target;
        if (t) {
            ctx.save();
            ctx.fillStyle = window.__canvasState.interactionCompleted ? 'rgb(0,200,255)' : t.color;
            ctx.shadowColor = 'rgba(0, 0, 0, 0.4)';
            ctx.shadowBlur = 10;
            ctx.shadowOffsetX = 3;
            ctx.shadowOffsetY = 3;

            ctx.fillRect(t.x, t.y, t.w, t.h);
            ctx.restore();

            // Label text inside target box
            ctx.fillStyle = '#000000';
            ctx.font = 'bold 14px sans-serif';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            const labelText = window.__canvasState.interactionCompleted ? 'SUCCESS' : (window.__canvasState.status === 'active' ? 'TARGET' : 'LOADING');
            ctx.fillText(labelText, t.x + t.w / 2, t.y + t.h / 2);
        }

        requestAnimationFrame(render);
    }

    // Start RAF rendering loop
    requestAnimationFrame(render);

    // Mouse Interaction Handlers for Chained Action (Hover -> Drag 15px X -> Click)
    function getCanvasCoords(e) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: e.clientX - rect.left,
            y: e.clientY - rect.top
        };
    }

    function isInsideTarget(coords) {
        const t = window.__canvasState.target;
        return coords.x >= t.x && coords.x <= (t.x + t.w) &&
               coords.y >= t.y && coords.y <= (t.y + t.h);
    }

    canvas.addEventListener('mousemove', (e) => {
        const coords = getCanvasCoords(e);
        if (isInsideTarget(coords)) {
            if (!hoverDetected) {
                hoverDetected = true;
                console.log('[CANVAS ACTION] Hover detected on active target');
            }
        }
        if (isMouseDown) {
            const currentDx = coords.x - dragStartX;
            if (currentDx > maxDragDx) {
                maxDragDx = currentDx;
            }
        }
    });

    canvas.addEventListener('mousedown', (e) => {
        const coords = getCanvasCoords(e);
        if (isInsideTarget(coords)) {
            isMouseDown = true;
            dragStartX = coords.x;
            maxDragDx = 0;
            console.log(`[CANVAS ACTION] MouseDown at x=${coords.x}`);
        }
    });

    canvas.addEventListener('mouseup', (e) => {
        const coords = getCanvasCoords(e);
        if (isMouseDown) {
            isMouseDown = false;
            console.log(`[CANVAS ACTION] MouseUp at x=${coords.x}, Max Drag Dx=${maxDragDx}px`);

            // Verify Chained Interaction: Hover -> Drag ~15px on X-axis -> Click on Target
            if (hoverDetected && maxDragDx >= 10 && isInsideTarget(coords)) {
                window.__canvasState.interactionCompleted = true;
                interactionStatusEl.textContent = `SUCCESS (Drag ${maxDragDx.toFixed(1)}px)`;
                interactionStatusEl.style.color = '#10b981';
                successBannerEl.classList.remove('hidden');

                if (ws.readyState === WebSocket.OPEN) {
                    ws.send(JSON.stringify({
                        type: 'interaction_result',
                        success: true,
                        drag_dx: maxDragDx
                    }));
                }
            }
        }
    });

})();
