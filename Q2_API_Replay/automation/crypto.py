import hmac
import hashlib
import json

# Default Shared Secret Key
DEFAULT_SECRET_KEY = b"frugal_testing_intern_secure_salt_2026"

def canonicalize_raw_body(raw_body: str) -> str:
    """
    Canonicalizes raw JSON body string to ensure identical payload representation.
    Sorts dictionary keys and removes arbitrary whitespace.
    """
    try:
        parsed = json.loads(raw_body)
        return json.dumps(parsed, sort_keys=True, separators=(',', ':'))
    except Exception:
        return raw_body.strip()

def generate_fmac(
    raw_body: str,
    timestamp: str,
    challenge: str,
    salt: str,
    secret_key: bytes = DEFAULT_SECRET_KEY
) -> str:
    """
    Generates HMAC-SHA512 authentication MAC token (X-Frugal-Mac).
    Incorporates:
    1. Raw transaction body (canonicalized)
    2. Localized microsecond timestamp
    3. Server-provided challenge token
    4. Salt sequence
    """
    canonical_body = canonicalize_raw_body(raw_body)
    signing_message = f"{canonical_body}:{timestamp}:{challenge}:{salt}"

    print(f"[CRYPTO] Raw body canonicalized: {canonical_body}")
    print(f"[CRYPTO] Timestamp: {timestamp}")
    print(f"[CRYPTO] Salt: {salt}")
    print(f"[CRYPTO] Challenge: {challenge[:16]}...")
    print(f"[CRYPTO] Algorithm: HMAC-SHA512")

    mac = hmac.new(secret_key, signing_message.encode('utf-8'), hashlib.sha512).hexdigest()
    print(f"[CRYPTO] X-Frugal-Mac generated: {mac[:32]}...")
    return mac
