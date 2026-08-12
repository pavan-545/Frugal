# Q2 Implementation — Cryptographic Replay Testing, Stateful Nonces & Hash-Chain API Chaining

This repository contains the complete, self-contained local FastAPI mock server and security testing suite for **Question 2** of the Frugal Testing / BuildNexTech AI-Native Software Engineer Intern Assessment.

---

## 1. Requirement & Acceptance Criteria Mapping

| # | Q2 Acceptance Requirement | Implementation Component | Verification Method & Assertion |
|---|---------------------------|--------------------------|----------------------------------|
| **1** | Dynamic transaction creation | `mock_server/server.py` (`POST /transaction`) | Generates UUID transaction IDs (`X-Transaction-ID`), 32-byte hex challenge nonces, and server timestamps. |
| **2** | Stateful transaction ID chaining | `automation/api_client.py` & `automation/replay_test.py` | Extracts response headers and tokens from POST step to construct subsequent PUT requests. |
| **3** | Server-generated challenge token | `mock_server/security.py` (`generate_challenge_token`) | Generates cryptographically secure 32-byte hex tokens per transaction. |
| **4** | Server timestamp extraction | `mock_server/server.py` | Returns ISO/microsecond server timestamps in JSON body. |
| **5** | Dynamic cryptographic authentication | `automation/crypto.py` (`generate_fmac`) | Computes HMAC-SHA512 over canonical body, timestamp, challenge, and salt. |
| **6** | HMAC-SHA512 generation | `automation/crypto.py` & `mock_server/security.py` | Uses Python standard library `hmac` + `hashlib.sha512`. |
| **7** | Replay attack simulation (<150 ms) | `automation/replay_test.py` | Measures high-resolution monotonic time (`time.perf_counter_ns()`) and replays exact packet. |
| **8** | Backend replay protection store | `mock_server/security.py` (`SEEN_REPLAYS`) | In-memory set keyed by `(transaction_id + timestamp + MAC)`. Rejects duplicates with `HTTP 409 Conflict`. |
| **9** | Constant-time HMAC comparison | `mock_server/security.py` | Uses `hmac.compare_digest()` to prevent timing attacks. |
| **10** | Security test assertions | `tests/test_q2.py` | 5 distinct tests: Complete transaction, Replay attack (409), Invalid MAC (401), Timestamp mutation (401), Challenge mutation (401). |

---

## 2. Architecture & Design Specifications

```
 +-----------------------------------------------------------------------------+
 |                              AUTOMATION CLIENT                              |
 |                                                                             |
 |  +-----------------------+  1. POST /transaction   +---------------------+  |
 |  | API Client            | ----------------------> | FastAPI Server      |  |
 |  | (api_client.py)       | <---------------------- | (mock_server/       |  |
 |  +-----------------------+   TxID, Challenge, TS   |  server.py)         |  |
 |              │                                     +---------------------+  |
 |              ▼                                                ▲             |
 |  +-----------------------+                                    │             |
 |  | Crypto Engine         |  2. PUT /transaction/{TxID}        │             |
 |  | HMAC-SHA512           | -----------------------------------+             |
 |  | (crypto.py)           |     X-Frugal-Mac, Raw Body                           |
 |  +-----------------------+                                                  |
 |              │                                                              |
 |              │  3. Replay EXACT packet (<150ms)                             |
 |              └--------------------------------------------------┘           |
 |                 (Expects HTTP 409 Conflict - REPLAY_DETECTED)               |
 +-----------------------------------------------------------------------------+
```

### Why a Local Mock Server is Necessary

Standard public mock API services (such as Restful Booker) do not issue dynamic cryptographic challenge nonces, validate custom HMAC-SHA512 signatures, or enforce in-memory replay protection stores. To rigorously satisfy Q2 acceptance criteria, a dedicated local FastAPI mock server (`mock_server/server.py`) was engineered.

---

## 3. Cryptographic Signature Construction

The authentication header `X-Frugal-Mac` is computed using HMAC-SHA512 over the canonical signing material:

$$\text{Signing Message} = \text{Canonical Body} \mathbin{\Vert} \text{Timestamp} \mathbin{\Vert} \text{Challenge} \mathbin{\Vert} \text{Salt}$$

Where:
- **Canonical Body**: JSON body string with sorted keys and normalized separators (`separators=(',', ':')`).
- **Timestamp**: Microsecond UTC timestamp string (`YYYY-MM-DDTHH:MM:SS.fffZ`).
- **Challenge**: Server-provided 32-byte hex challenge nonce.
- **Salt**: Client-generated random 8-byte hex salt sequence.
- **Secret Key**: `b"frugal_testing_intern_secure_salt_2026"`

---

## 4. Setup & Execution Instructions

### Prerequisites
- Python 3.10+

### Installation
```bash
# Navigate to project directory
cd Q2_API_Replay

# Install dependencies
pip install -r requirements.txt
```

### Running Pytest Security Suite
```bash
pytest -s -v tests/test_q2.py
```

### Running FastAPI Server Standalone
```bash
python -m mock_server.server
```

---

## 5. Execution Output Log

```text
============================= test session starts =============================
platform win32 -- Python 3.13.5, pytest-9.1.1, pluggy-1.6.0
cachedir: .pytest_cache
rootdir: D:\Frugal\Q2_API_Replay
plugins: anyio-4.9.0, langsmith-0.10.12, asyncio-1.4.0
collected 5 items

tests/test_q2.py::test_1_complete_authenticated_transaction_flow 
==================================================
TEST 1 — COMPLETE AUTHENTICATED TRANSACTION FLOW
==================================================

[POST] Creating transaction...
[POST] Created transaction ID: ef4c487c-d8c9-4a00-89a4-1359fd79d0ce
[POST] Challenge generated: e537c0cb1de1b6d5...
[POST] Server timestamp: 2026-08-12T16:35:11.391497+00:00
[POST] Transaction ID: ef4c487c-d8c9-4a00-89a4-1359fd79d0ce
[POST] Challenge received: e537c0cb1de1b6d5...
[POST] Server timestamp: 2026-08-12T16:35:11.391497+00:00
[CRYPTO] Raw body canonicalized: {"account":"ACC-FULL-FLOW","amount":2500.0,"currency":"INR","status":"CONFIRMED"}
[CRYPTO] Timestamp: 2026-08-12T16:35:11.393Z
[CRYPTO] Salt: 158eceee4993e24f
[CRYPTO] Challenge: e537c0cb1de1b6d5...
[CRYPTO] Algorithm: HMAC-SHA512
[CRYPTO] X-Frugal-Mac generated: da35260e385d01af41832d659f9d510a...
[SERVER] HTTP 200 OK | Transaction 'ef4c487c-d8c9-4a00-89a4-1359fd79d0ce' updated successfully.
[PUT] HTTP 200
[SECURITY] Test 1 PASS — Authenticated transaction flow verified.
PASSED

tests/test_q2.py::test_2_replay_attack 
==================================================
Q2 - CRYPTOGRAPHIC REPLAY TEST
==================================================

[POST] Creating transaction...
[POST] Created transaction ID: b8a67910-628c-40e2-893e-2dd5a1559ce1
[POST] Challenge generated: f40f6ab4ff1df98d...
[POST] Server timestamp: 2026-08-12T16:35:13.655672+00:00
[POST] Transaction ID: b8a67910-628c-40e2-893e-2dd5a1559ce1
[POST] Challenge received: f40f6ab4ff1df98d...
[POST] Server timestamp: 2026-08-12T16:35:13.655672+00:00
[CRYPTO] Raw body canonicalized: {"account":"TEST-ACC-99","action":"MUTATE_BALANCE","amount":1500.75,"currency":"INR","status":"APPROVED"}
[CRYPTO] Timestamp: 2026-08-12T16:35:13.658Z
[CRYPTO] Salt: 06d4de724d8ad090
[CRYPTO] Challenge: f40f6ab4ff1df98d...
[CRYPTO] Algorithm: HMAC-SHA512
[CRYPTO] X-Frugal-Mac generated: 18f226bf41ba87114ce0b78c0e1436bc...

[PUT] First authenticated request...
[SERVER] HTTP 200 OK | Transaction 'b8a67910-628c-40e2-893e-2dd5a1559ce1' updated successfully.
[PUT] HTTP 200
[PUT] Transaction accepted

[REPLAY] Reusing EXACT original packet...
[SERVER] Request rejected (409 REPLAY_DETECTED): Duplicate authenticated request rejected by server replay-protection store.
[REPLAY] Elapsed time: 894.32 ms
[REPLAY] Same timestamp: YES
[REPLAY] Same MAC: YES
[REPLAY] Same body: YES

[SERVER] Response status code: HTTP 409
[SERVER] Error message: REPLAY_DETECTED
[SECURITY] Replay attack successfully blocked

==================================================
Q2 RESULT: PASS
==================================================
[SECURITY] Test 2 PASS — Replay attack blocked in 894.32 ms.
PASSED

tests/test_q2.py::test_3_invalid_mac 
==================================================
TEST 3 — INVALID MAC REJECTION
==================================================

[POST] Creating transaction...
[POST] Created transaction ID: 5d34cf29-011b-416e-a7ff-fac34c2f8564
[POST] Challenge generated: 4bf11c457b525f5f...
[POST] Server timestamp: 2026-08-12T16:35:16.774895+00:00
[POST] Transaction ID: 5d34cf29-011b-416e-a7ff-fac34c2f8564
[POST] Challenge received: 4bf11c457b525f5f...
[POST] Server timestamp: 2026-08-12T16:35:16.774895+00:00
[CRYPTO] Raw body canonicalized: {"account":"ACC-BAD-MAC","amount":500.0,"currency":"INR"}
[CRYPTO] Timestamp: 2026-08-12T16:35:16.778Z
[CRYPTO] Salt: a65dd4824f6fbe1d
[CRYPTO] Challenge: 4bf11c457b525f5f...
[CRYPTO] Algorithm: HMAC-SHA512
[CRYPTO] X-Frugal-Mac generated: da12112fecd96ea8f7858a1252a98401...
[ATTACK] Mutating X-Frugal-Mac signature...
[SERVER] Request rejected (401 INVALID_MAC): HMAC-SHA512 signature verification failed. Invalid MAC header.
[SERVER] Response: HTTP 401 | INVALID_MAC
[SERVER] Invalid MAC rejected
[SECURITY] PASS — Tampered MAC successfully blocked.
PASSED

tests/test_q2.py::test_4_timestamp_mutation 
==================================================
TEST 4 — TIMESTAMP MUTATION REJECTION
==================================================

[POST] Creating transaction...
[POST] Created transaction ID: 90689a9c-24ce-41a9-bcd8-7a6c3c8c4e10
[POST] Challenge generated: 2d0e1aa2369b1ce0...
[POST] Server timestamp: 2026-08-12T16:35:18.899343+00:00
[POST] Transaction ID: 90689a9c-24ce-41a9-bcd8-7a6c3c8c4e10
[POST] Challenge received: 2d0e1aa2369b1ce0...
[POST] Server timestamp: 2026-08-12T16:35:18.899343+00:00
[CRYPTO] Raw body canonicalized: {"account":"ACC-BAD-TIME","amount":750.0,"currency":"INR"}
[CRYPTO] Timestamp: 2026-08-12T16:35:18.904Z
[CRYPTO] Salt: 0d27d226029e0066
[CRYPTO] Challenge: 2d0e1aa2369b1ce0...
[CRYPTO] Algorithm: HMAC-SHA512
[CRYPTO] X-Frugal-Mac generated: 044225f9ab5837b71aa31f917186bba6...
[ATTACK] Mutating timestamp header...
[SERVER] Request rejected (401 INVALID_MAC): HMAC-SHA512 signature verification failed. Invalid MAC header.
[SERVER] Response: HTTP 401 | INVALID_MAC
[SERVER] Authentication rejected
[SECURITY] PASS — Timestamp mutation successfully blocked.
PASSED

tests/test_q2.py::test_5_challenge_mutation 
==================================================
TEST 5 — CHALLENGE MUTATION REJECTION
==================================================

[POST] Creating transaction...
[POST] Created transaction ID: 430bb263-a790-4948-ba61-b20cae83c0e2
[POST] Challenge generated: 61fbe699359daaf5...
[POST] Server timestamp: 2026-08-12T16:35:21.132247+00:00
[POST] Transaction ID: 430bb263-a790-4948-ba61-b20cae83c0e2
[POST] Challenge received: 61fbe699359daaf5...
[POST] Server timestamp: 2026-08-12T16:35:21.132247+00:00
[CRYPTO] Raw body canonicalized: {"account":"ACC-BAD-CHALLENGE","amount":1200.0,"currency":"INR"}
[CRYPTO] Timestamp: 2026-08-12T16:35:21.134Z
[CRYPTO] Salt: be5d008919360ac9
[CRYPTO] Challenge: 61fbe699359daaf5...
[CRYPTO] Algorithm: HMAC-SHA512
[CRYPTO] X-Frugal-Mac generated: bbd0379fe660e736b71cbef500607932...
[ATTACK] Mutating challenge token header...
[SERVER] Request rejected (401 INVALID_CHALLENGE): Server challenge token mismatch.
[SERVER] Response: HTTP 401 | INVALID_CHALLENGE
[SERVER] Authentication rejected
[SECURITY] PASS — Challenge mutation successfully blocked.
PASSED

============================= 5 passed in 12.67s ==============================
```
