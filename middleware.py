from fastapi import Request, HTTPException
from contextvars import ContextVar
from functools import wraps
from helpers import verify_access_token

# 1. Define the Context Variable
request_var = ContextVar("global_request", default=None)


# 2. DEFINE PURE ASGI MIDDLEWARE (This fixes the context loss)
class ContextMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # We only care about HTTP requests
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Create the Request object manually from scope
        request = Request(scope, receive=receive)

        # Set the context var
        token = request_var.set(request)

        try:
            # Call the next part of the app
            await self.app(scope, receive, send)
        finally:
            # Clean up
            request_var.reset(token)


# 3. Add the middleware to the app


def verify_token():
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # This will now successfully retrieve the request!
            request = request_var.get()

            if not request:
                # If this hits, the middleware didn't run or scope is wrong
                raise HTTPException(status_code=500, detail="Request context missing")

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Please login")

            token = auth_header.split(" ")[1]

            try:
                # --- MOCK VERIFICATION ---
                if token == "fail":
                    raise Exception()
                payload = verify_access_token(token)
            except Exception:
                raise HTTPException(status_code=403, detail="Invalid credentials! Please login again.")

            kwargs["decoded_payload"] = payload
            return await func(*args, **kwargs)

        return wrapper

    return decorator
