import hmac
import hashlib
import json
import secrets
from typing import Dict, Any, Tuple

# Server Cryptographic Secret Key
SECRET_KEY = b"frugal_testing_intern_secure_salt_2026"

# In-Memory Replay Protection Store
SEEN_REPLAYS = set()

def reset_security_store():
    """Resets replay protection store between test runs."""
    SEEN_REPLAYS.clear()

def generate_challenge_token() -> str:
    """Generates a cryptographically random 32-byte hex challenge token."""
    return secrets.token_hex(32)

def canonicalize_body(raw_body: str) -> str:
    """Canonicalizes JSON string by sorting keys and stripping whitespace."""
    try:
        data = json.loads(raw_body)
        return json.dumps(data, sort_keys=True, separators=(',', ':'))
    except Exception:
        return raw_body.strip()

def compute_hmac_sha512(raw_body_str: str, timestamp: str, challenge: str, salt: str) -> str:
    """
    Computes HMAC-SHA512 over canonical signing material:
    message = canonical_body + ":" + timestamp + ":" + challenge + ":" + salt
    """
    canonical_body = canonicalize_body(raw_body_str)
    signing_message = f"{canonical_body}:{timestamp}:{challenge}:{salt}"
    return hmac.new(SECRET_KEY, signing_message.encode('utf-8'), hashlib.sha512).hexdigest()

def verify_put_request(
    tx_id: str,
    raw_body_str: str,
    headers: Dict[str, str],
    transaction_store: Dict[str, Any]
) -> Tuple[bool, int, str, str]:
    """
    Security Validation Pipeline:
    1. Transaction Existence Check
    2. Header Existence Check
    3. Replay Protection Store Lookup
    4. Challenge Token Verification
    5. Constant-Time HMAC-SHA512 Signature Comparison
    6. Commit Replay Record
    """
    # 1. Transaction Existence
    if tx_id not in transaction_store:
        return False, 404, "TRANSACTION_NOT_FOUND", f"Transaction '{tx_id}' not found."

    tx_state = transaction_store[tx_id]

    # 2. Header Extraction & Check
    mac = headers.get("X-Frugal-Mac") or headers.get("x-frugal-mac")
    timestamp = headers.get("X-Timestamp") or headers.get("x-timestamp")
    salt = headers.get("X-Salt") or headers.get("x-salt")
    client_challenge = headers.get("X-Challenge") or headers.get("x-challenge") or tx_state["challenge"]

    if not mac or not timestamp or not salt:
        return False, 400, "MISSING_HEADERS", "Required authentication headers (X-Frugal-Mac, X-Timestamp, X-Salt) missing."

    # 3. Replay Attack Store Lookup
    replay_key = f"{tx_id}:{timestamp}:{mac}"
    if replay_key in SEEN_REPLAYS:
        return False, 409, "REPLAY_DETECTED", "Duplicate authenticated request rejected by server replay-protection store."

    # 4. Challenge Token Check
    if client_challenge != tx_state["challenge"]:
        return False, 401, "INVALID_CHALLENGE", "Server challenge token mismatch."

    # 5. HMAC-SHA512 Signature Verification using Constant-Time Comparison
    expected_mac = compute_hmac_sha512(raw_body_str, timestamp, tx_state["challenge"], salt)
    if not hmac.compare_digest(expected_mac, mac):
        return False, 401, "INVALID_MAC", "HMAC-SHA512 signature verification failed. Invalid MAC header."

    # 6. Commit to Replay Store
    SEEN_REPLAYS.add(replay_key)
    return True, 200, "SUCCESS", "Transaction updated successfully."
