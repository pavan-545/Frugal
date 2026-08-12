/**
 * JS Canvas Pixel Detector Engine
 * Executes inside browser window using requestAnimationFrame and getImageData().
 * Strictly complies with Anti-AI criteria: NO static sleeps, NO DOM locators for targets.
 */
(function () {
    return new Promise((resolve, reject) => {
        const canvas = document.getElementById('app-canvas');
        if (!canvas) {
            return reject(new Error('Canvas element #app-canvas not found on page'));
        }
        const ctx = canvas.getContext('2d');
        const maxTimeout = 15000; // 15s max timeout safety
        const startTime = performance.now();

        function scanCanvasPixels() {
            const width = canvas.width;
            const height = canvas.height;
            const imageData = ctx.getImageData(0, 0, width, height);
            const data = imageData.data;

            let minX = width, minY = height, maxX = 0, maxY = 0;
            let activePixelCount = 0;
            let loadingPixelCount = 0;

            // Scan pixels across canvas context
            // Step size 4 for performance while retaining accuracy
            for (let y = 0; y < height; y += 4) {
                for (let x = 0; x < width; x += 4) {
                    const idx = (y * width + x) * 4;
                    const r = data[idx];
                    const g = data[idx + 1];
                    const b = data[idx + 2];
                    const a = data[idx + 3];

                    if (a > 200) {
                        // Check for Active Target Green: G > 200, R < 50, B < 50
                        if (g > 200 && r < 50 && b < 50) {
                            activePixelCount++;
                            if (x < minX) minX = x;
                            if (x > maxX) maxX = x;
                            if (y < minY) minY = y;
                            if (y > maxY) maxY = y;
                        }
                        // Check for Loading Gray: R, G, B all within [120, 135]
                        else if (Math.abs(r - 128) < 15 && Math.abs(g - 128) < 15 && Math.abs(b - 128) < 15) {
                            loadingPixelCount++;
                        }
                    }
                }
            }

            // If active target pixels detected (at least 20 sampled pixels forming target box)
            if (activePixelCount >= 20 && maxX > minX && maxY > minY) {
                const targetW = maxX - minX;
                const targetH = maxY - minY;
                const centerX = minX + targetW / 2;
                const centerY = minY + targetH / 2;

                // Account for canvas bounding client rect offset in viewport
                const rect = canvas.getBoundingClientRect();
                const viewportX = rect.left + centerX;
                const viewportY = rect.top + centerY;

                return resolve({
                    state: 'active',
                    detected: true,
                    canvasX: centerX,
                    canvasY: centerY,
                    viewportX: viewportX,
                    viewportY: viewportY,
                    width: targetW,
                    height: targetH,
                    pixelCount: activePixelCount,
                    timestamp: performance.now()
                });
            }

            // Check if timed out
            if (performance.now() - startTime > maxTimeout) {
                return reject(new Error(`Canvas state detection timed out after ${maxTimeout}ms. (Loading pixels: ${loadingPixelCount})`));
            }

            // Continue polling next animation frame
            requestAnimationFrame(scanCanvasPixels);
        }

        // Start scanning loop
        requestAnimationFrame(scanCanvasPixels);
    });
})();
