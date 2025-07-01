from fastapi import Request, HTTPException


def verify_token(request: Request):
    token = request.headers.get("authorization")
    if not token or token != "secret-token":
        raise HTTPException(status_code=401, detail="Unauthorized")
