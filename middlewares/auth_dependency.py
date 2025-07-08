from fastapi import Request, HTTPException, Depends


def verify_token(request: Request):
    token = request.headers.get("authorization")
    if not token or token != "secret-token":
        raise HTTPException(status_code=401, detail="Unauthorized")


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
