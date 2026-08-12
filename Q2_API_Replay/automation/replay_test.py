import time
import datetime
import json
import secrets
from typing import Dict, Any, Tuple
from automation.api_client import TransactionAPIClient
from automation.crypto import generate_fmac

class ReplayAttackTester:
    def __init__(self, api_client: TransactionAPIClient):
        self.api_client = api_client

    def execute_replay_test_flow(self) -> Dict[str, Any]:
        """
        Executes complete Stateful Chaining & Replay Attack test:
        1. POST /transaction -> extract dynamic TxID, challenge, timestamp
        2. Construct PUT payload & generate HMAC-SHA512 MAC
        3. Send 1st authenticated PUT -> expect HTTP 200 OK
        4. Replay EXACT SAME packet within 150 ms window
        5. Assert 2nd request rejected with HTTP 409 Conflict & REPLAY_DETECTED
        """
        print("\n" + "=" * 50)
        print("Q2 - CRYPTOGRAPHIC REPLAY TEST")
        print("=" * 50)

        # Step 1: Stateful POST transaction creation
        tx_info = self.api_client.create_transaction(amount=1500.75, currency="INR", account="TEST-ACC-99")
        tx_id = tx_info["transaction_id"]
        challenge = tx_info["challenge"]

        # Step 2: Prepare PUT payload & generate localized microsecond timestamp and salt
        raw_body_dict = {
            "amount": 1500.75,
            "currency": "INR",
            "account": "TEST-ACC-99",
            "action": "MUTATE_BALANCE",
            "status": "APPROVED"
        }
        raw_body_str = json.dumps(raw_body_dict)
        timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        salt = secrets.token_hex(8)

        # Generate HMAC-SHA512 MAC signature
        mac = generate_fmac(raw_body_str, timestamp, challenge, salt)

        # Construct exact original request dictionary
        original_request = {
            "transaction_id": tx_id,
            "raw_body": raw_body_str,
            "headers": {
                "X-Frugal-Mac": mac,
                "X-Timestamp": timestamp,
                "X-Salt": salt,
                "X-Challenge": challenge
            }
        }

        # Step 3: Send 1st Authenticated PUT
        print("\n[PUT] First authenticated request...")
        t0 = time.perf_counter_ns()
        resp_1 = self.api_client.send_put_request(
            original_request["transaction_id"],
            original_request["raw_body"],
            original_request["headers"]
        )
        t1 = time.perf_counter_ns()

        print(f"[PUT] HTTP {resp_1.status_code}")
        assert resp_1.status_code == 200, f"First PUT failed with status {resp_1.status_code}: {resp_1.text}"
        print("[PUT] Transaction accepted")

        # Step 4: Replay EXACT SAME Packet Immediately (<150 ms requirement)
        print("\n[REPLAY] Reusing EXACT original packet...")
        t_replay_start = time.perf_counter_ns()
        resp_2 = self.api_client.send_put_request(
            original_request["transaction_id"],
            original_request["raw_body"],
            original_request["headers"]
        )
        t_replay_end = time.perf_counter_ns()

        replay_elapsed_ms = (t_replay_end - t_replay_start) / 1_000_000.0

        print(f"[REPLAY] Elapsed time: {replay_elapsed_ms:.2f} ms")
        print(f"[REPLAY] Same timestamp: YES")
        print(f"[REPLAY] Same MAC: YES")
        print(f"[REPLAY] Same body: YES")

        # Step 5: Assert Server Replay Protection Rejection
        print(f"\n[SERVER] Response status code: HTTP {resp_2.status_code}")
        resp_2_data = resp_2.json() if resp_2.headers.get("content-type") == "application/json" else {}
        print(f"[SERVER] Error message: {resp_2_data.get('error')}")

        assert resp_2.status_code == 409, f"Expected HTTP 409 Conflict, got {resp_2.status_code}"
        assert resp_2_data.get("error") == "REPLAY_DETECTED", f"Expected error 'REPLAY_DETECTED', got {resp_2_data.get('error')}"

        print("[SECURITY] Replay attack successfully blocked")
        print("\n" + "=" * 50)
        print("Q2 RESULT: PASS")
        print("=" * 50)

        return {
            "first_status": resp_1.status_code,
            "replay_status": resp_2.status_code,
            "replay_elapsed_ms": replay_elapsed_ms,
            "replay_blocked": True
        }
