import pytest
import datetime
import json
import secrets
from automation.api_client import TransactionAPIClient
from automation.crypto import generate_fmac
from automation.replay_test import ReplayAttackTester

def test_1_complete_authenticated_transaction_flow(api_client: TransactionAPIClient):
    """
    Test 1: Complete authenticated transaction flow
    Verifies POST dynamic token extraction, HMAC-SHA512 generation, and valid PUT acceptance.
    """
    print("\n" + "=" * 50)
    print("TEST 1 — COMPLETE AUTHENTICATED TRANSACTION FLOW")
    print("=" * 50)

    # 1. POST transaction creation
    tx_info = api_client.create_transaction(amount=2500.00, currency="INR", account="ACC-FULL-FLOW")
    tx_id = tx_info["transaction_id"]
    challenge = tx_info["challenge"]

    assert tx_id is not None and len(tx_id) > 0
    assert challenge is not None and len(challenge) == 64
    assert tx_info["status"] == "created"

    # 2. Construct PUT body & security parameters
    raw_body_dict = {"amount": 2500.00, "currency": "INR", "account": "ACC-FULL-FLOW", "status": "CONFIRMED"}
    raw_body_str = json.dumps(raw_body_dict)
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    salt = secrets.token_hex(8)

    # 3. Generate dynamic HMAC-SHA512 signature
    mac = generate_fmac(raw_body_str, timestamp, challenge, salt)

    headers = {
        "X-Frugal-Mac": mac,
        "X-Timestamp": timestamp,
        "X-Salt": salt,
        "X-Challenge": challenge
    }

    # 4. Execute PUT transaction
    response = api_client.send_put_request(tx_id, raw_body_str, headers)
    print(f"[PUT] HTTP {response.status_code}")
    assert response.status_code == 200
    assert response.json()["status"] == "updated"
    print("[SECURITY] Test 1 PASS — Authenticated transaction flow verified.")


def test_2_replay_attack(api_client: TransactionAPIClient):
    """
    Test 2: Replay attack prevention
    Verifies sub-150ms exact packet replay detection and HTTP 409 Conflict rejection.
    """
    tester = ReplayAttackTester(api_client)
    result = tester.execute_replay_test_flow()

    assert result["first_status"] == 200
    assert result["replay_status"] == 409
    assert result["replay_blocked"] is True
    print(f"[SECURITY] Test 2 PASS — Replay attack blocked in {result['replay_elapsed_ms']:.2f} ms.")


def test_3_invalid_mac(api_client: TransactionAPIClient):
    """
    Test 3: Invalid MAC rejection
    Mutates X-Frugal-Mac signature by 1 character and asserts HTTP 401 rejection.
    """
    print("\n" + "=" * 50)
    print("TEST 3 — INVALID MAC REJECTION")
    print("=" * 50)

    tx_info = api_client.create_transaction(amount=500.00, currency="INR", account="ACC-BAD-MAC")
    tx_id = tx_info["transaction_id"]
    challenge = tx_info["challenge"]

    raw_body_str = json.dumps({"amount": 500.00, "currency": "INR", "account": "ACC-BAD-MAC"})
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    salt = secrets.token_hex(8)

    valid_mac = generate_fmac(raw_body_str, timestamp, challenge, salt)
    # Mutate last character of MAC string
    corrupted_mac = valid_mac[:-1] + ("0" if valid_mac[-1] != "0" else "1")

    headers = {
        "X-Frugal-Mac": corrupted_mac,
        "X-Timestamp": timestamp,
        "X-Salt": salt,
        "X-Challenge": challenge
    }

    print("[ATTACK] Mutating X-Frugal-Mac signature...")
    response = api_client.send_put_request(tx_id, raw_body_str, headers)
    print(f"[SERVER] Response: HTTP {response.status_code} | {response.json().get('error')}")

    assert response.status_code == 401
    assert response.json()["error"] == "INVALID_MAC"
    print("[SERVER] Invalid MAC rejected")
    print("[SECURITY] PASS — Tampered MAC successfully blocked.")


def test_4_timestamp_mutation(api_client: TransactionAPIClient):
    """
    Test 4: Timestamp mutation rejection
    Mutates the authenticated timestamp header and asserts signature validation failure.
    """
    print("\n" + "=" * 50)
    print("TEST 4 — TIMESTAMP MUTATION REJECTION")
    print("=" * 50)

    tx_info = api_client.create_transaction(amount=750.00, currency="INR", account="ACC-BAD-TIME")
    tx_id = tx_info["transaction_id"]
    challenge = tx_info["challenge"]

    raw_body_str = json.dumps({"amount": 750.00, "currency": "INR", "account": "ACC-BAD-TIME"})
    valid_timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    salt = secrets.token_hex(8)

    # Generate MAC using valid timestamp
    mac = generate_fmac(raw_body_str, valid_timestamp, challenge, salt)

    # Mutate timestamp sent in HTTP header
    mutated_timestamp = valid_timestamp.replace("2026", "2025")

    headers = {
        "X-Frugal-Mac": mac,
        "X-Timestamp": mutated_timestamp,
        "X-Salt": salt,
        "X-Challenge": challenge
    }

    print("[ATTACK] Mutating timestamp header...")
    response = api_client.send_put_request(tx_id, raw_body_str, headers)
    print(f"[SERVER] Response: HTTP {response.status_code} | {response.json().get('error')}")

    assert response.status_code == 401
    assert response.json()["error"] == "INVALID_MAC"
    print("[SERVER] Authentication rejected")
    print("[SECURITY] PASS — Timestamp mutation successfully blocked.")


def test_5_challenge_mutation(api_client: TransactionAPIClient):
    """
    Test 5: Challenge mutation rejection
    Mutates the server-provided challenge token and asserts HTTP 401 rejection.
    """
    print("\n" + "=" * 50)
    print("TEST 5 — CHALLENGE MUTATION REJECTION")
    print("=" * 50)

    tx_info = api_client.create_transaction(amount=1200.00, currency="INR", account="ACC-BAD-CHALLENGE")
    tx_id = tx_info["transaction_id"]
    challenge = tx_info["challenge"]

    raw_body_str = json.dumps({"amount": 1200.00, "currency": "INR", "account": "ACC-BAD-CHALLENGE"})
    timestamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    salt = secrets.token_hex(8)

    mac = generate_fmac(raw_body_str, timestamp, challenge, salt)

    # Mutate challenge in header
    mutated_challenge = "f" * 64

    headers = {
        "X-Frugal-Mac": mac,
        "X-Timestamp": timestamp,
        "X-Salt": salt,
        "X-Challenge": mutated_challenge
    }

    print("[ATTACK] Mutating challenge token header...")
    response = api_client.send_put_request(tx_id, raw_body_str, headers)
    print(f"[SERVER] Response: HTTP {response.status_code} | {response.json().get('error')}")

    assert response.status_code == 401
    assert response.json()["error"] == "INVALID_CHALLENGE"
    print("[SERVER] Authentication rejected")
    print("[SECURITY] PASS — Challenge mutation successfully blocked.")
