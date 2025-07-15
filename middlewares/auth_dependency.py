from fastapi import Request, HTTPException, Depends
import jwt


def verify_token(request: Request):
    auth_header = request.headers.get("authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Authorization header missing or invalid"
        )

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, "python", algorithms=["HS256"])
        request.state.user = payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def rate_limiter(request: Request):
    ip = request.client.host
    key = f"rate-limit:{ip}"

    count = await request.state.redis.get(key)
    if count and int(count) >= 100:
        raise HTTPException(status_code=429, detail="Too Many Requests")

    pipeline = request.state.redis.pipeline()
    pipeline.incr(key)
    pipeline.expire(key, 60)
    await pipeline.execute()


def require_role(required_role: str):
    def role_checker(request: Request):
        user = request.state.user  # or decoded token
        if not user or user.get("role") != required_role:
            raise HTTPException(status_code=403, detail="Forbidden")

    return Depends(role_checker)
