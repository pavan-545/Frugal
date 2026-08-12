import httpx
import json
from typing import Dict, Any

class TransactionAPIClient:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url.rstrip("/")

    def create_transaction(self, amount: float = 1000.50, currency: str = "INR", account: str = "TEST-001") -> Dict[str, Any]:
        """
        Executes POST /transaction to initiate a new transaction instance.
        Extracts X-Transaction-ID from response headers and dynamic nonces from JSON body.
        """
        url = f"{self.base_url}/transaction"
        payload = {
            "amount": amount,
            "currency": currency,
            "account": account
        }

        print("\n[POST] Creating transaction...")
        with httpx.Client() as client:
            response = client.post(url, json=payload, timeout=10.0)
            response.raise_for_status()

            tx_id = response.headers.get("X-Transaction-ID")
            data = response.json()

            challenge = data.get("challenge")
            server_timestamp = data.get("server_timestamp")

            print(f"[POST] Transaction ID: {tx_id}")
            print(f"[POST] Challenge received: {challenge[:16]}...")
            print(f"[POST] Server timestamp: {server_timestamp}")

            return {
                "transaction_id": tx_id,
                "challenge": challenge,
                "server_timestamp": server_timestamp,
                "status": data.get("status")
            }

    def send_put_request(
        self,
        transaction_id: str,
        raw_body_str: str,
        headers: Dict[str, str]
    ) -> httpx.Response:
        """
        Sends raw PUT /transaction/{transaction_id} request with specified headers and body.
        Used for both initial valid execution and sub-150ms exact replay attack.
        """
        url = f"{self.base_url}/transaction/{transaction_id}"
        req_headers = {"Content-Type": "application/json"}
        req_headers.update(headers)

        with httpx.Client() as client:
            response = client.put(url, content=raw_body_str, headers=req_headers, timeout=10.0)
            return response
