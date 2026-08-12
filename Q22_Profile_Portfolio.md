# Q22. Profile & Technical Portfolio Compilation

## 1. Professional Credentials

- **Full Name:** Pavan Kumar Chandaka
- **LinkedIn Profile:** https://www.linkedin.com/in/pavan-kumar-chandaka?utm_source=share_via&utm_content=profile&utm_medium=member_android
- **Resume Download Link (PDF):** https://drive.google.com/file/d/1o6TnHteDPjKh2kKidzfkDcMkM7RgqXyv/view?usp=sharing
- **GitHub Profile:** https://github.com/pavan-545
- **LeetCode Profile:** https://leetcode.com/u/pavan_545/
- **HackerRank Profile:** https://www.hackerrank.com/profile/pavankumar_chan4

---

## 2. Technical Repositories & Profiles

| Platform | Profile / Repository Description | Verified URL |
| :--- | :--- | :--- |
| **Resume PDF** | Candidate Official Resume | https://drive.google.com/file/d/1o6TnHteDPjKh2kKidzfkDcMkM7RgqXyv/view?usp=sharing |
| **LinkedIn** | Candidate Professional Profile | https://www.linkedin.com/in/pavan-kumar-chandaka?utm_source=share_via&utm_content=profile&utm_medium=member_android |
| **GitHub** | Engineering Portfolio & Source Code | https://github.com/pavan-545 |
| **LeetCode** | Algorithmic Problem Solving Profile | https://leetcode.com/u/pavan_545/ |
| **HackerRank** | Technical Skills & Assessment Profile | https://www.hackerrank.com/profile/pavankumar_chan4 |

---

## 3. Outstanding System Projects

### 1. Dynamic HTML5 Canvas State Drifts & Asynchronous Race Interception Framework (Q1)
- **Objective:** Build a self-contained local HTML5 Canvas testbed and non-blocking Playwright automation engine to detect pixel-state transitions and execute rapid chained interactions (Hover -> Drag 15px X -> Click) under Fibonacci network jitter.
- **Key Technical Contribution:** Engineered a custom browser `requestAnimationFrame` pixel-state detection loop (`getImageData()`) and a 7-stage Circuit-Breaker state machine that detects dynamic coordinate drift (>5.0px threshold), invalidates stale coordinates, and recalculates target offsets safely before interaction execution.
- **Technology Stack:** Python, Playwright, HTML5 Canvas API, JavaScript (ES6+), WebSockets (`aiohttp`), pytest-asyncio.
- **GitHub/Repository URL:** https://github.com/pavan-545/Frugal/tree/main/Q1_Canvas_WebSocket
- **Live URL:** Not available

### 2. Cryptographic Replay Testing & Stateful Nonce Security Gateway (Q2)
- **Objective:** Build a high-security API testbed and automated security suite validating HMAC-SHA512 request signing, stateful challenge nonces, and sub-150ms exact packet replay attack detection.
- **Key Technical Contribution:** Developed a FastAPI mock gateway implementing constant-time `hmac.compare_digest()` verification, body canonicalization, and an in-memory replay protection store (`SEEN_REPLAYS`) returning `HTTP 409 Conflict` upon duplicate authenticated packet detection.
- **Technology Stack:** Python, FastAPI, Uvicorn, HMAC-SHA512, httpx, pytest.
- **GitHub/Repository URL:** https://github.com/pavan-545/Frugal/tree/main/Q2_API_Replay
- **Live URL:** Not available
