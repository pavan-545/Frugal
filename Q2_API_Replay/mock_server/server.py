import uuid
import datetime
import json
from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from mock_server.security import (
    generate_challenge_token,
    verify_put_request,
    reset_security_store
)

app = FastAPI(title="Q2 Secure Transaction API Server")

# In-Memory Transaction State Store
TRANSACTIONS = {}

def reset_server_state():
    """Resets server state between tests."""
    TRANSACTIONS.clear()
    reset_security_store()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/transaction")
async def create_transaction(request: Request):
    """
    POST /transaction
    Generates dynamic transaction ID, challenge token, and server timestamp.
    Returns X-Transaction-ID header and token challenge response.
    """
    try:
        body = await request.json()
    except Exception:
        body = {}

    tx_id = str(uuid.uuid4())
    challenge = generate_challenge_token()
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Store transaction state in memory
    TRANSACTIONS[tx_id] = {
        "id": tx_id,
        "amount": body.get("amount", 0.0),
        "currency": body.get("currency", "INR"),
        "account": body.get("account", "UNKNOWN"),
        "challenge": challenge,
        "server_timestamp": timestamp,
        "status": "created"
    }

    print(f"[POST] Created transaction ID: {tx_id}")
    print(f"[POST] Challenge generated: {challenge[:16]}...")
    print(f"[POST] Server timestamp: {timestamp}")

    response = JSONResponse(
        content={
            "challenge": challenge,
            "server_timestamp": timestamp,
            "status": "created"
        },
        status_code=status.HTTP_201_CREATED
    )
    # Header X-Transaction-ID
    response.headers["X-Transaction-ID"] = tx_id
    return response

@app.put("/transaction/{transaction_id}")
async def update_transaction(transaction_id: str, request: Request):
    """
    PUT /transaction/{transaction_id}
    Performs full security validation (HMAC-SHA512 + Replay Protection).
    """
    raw_body_bytes = await request.body()
    raw_body_str = raw_body_bytes.decode('utf-8')
    headers = dict(request.headers)

    is_valid, status_code, error_code, message = verify_put_request(
        transaction_id,
        raw_body_str,
        headers,
        TRANSACTIONS
    )

    if not is_valid:
        print(f"[SERVER] Request rejected ({status_code} {error_code}): {message}")
        return JSONResponse(
            status_code=status_code,
            content={"error": error_code, "message": message}
        )

    # Mutate transaction state
    TRANSACTIONS[transaction_id]["status"] = "updated"
    try:
        TRANSACTIONS[transaction_id]["updated_body"] = json.loads(raw_body_str)
    except Exception:
        pass

    print(f"[SERVER] HTTP 200 OK | Transaction '{transaction_id}' updated successfully.")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "updated", "transaction_id": transaction_id}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
