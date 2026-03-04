from fastapi import HTTPException, Request
import hashlib

def get_hashed_token(request: Request) -> str:
    """
    Extracts Bearer token from Authorization header and returns SHA256 hash
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="No token provided")

    token = auth_header.split(" ")[1]
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token_hash