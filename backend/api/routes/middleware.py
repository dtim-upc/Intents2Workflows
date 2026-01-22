import secrets
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

SESSION_COOKIE = "I2WG-session" #Can be disclosed because sessions are not required to be private right now.

# Considered to allow multiple users using the same application and recover intents and data products created earlier, but not long ago
class SessionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        session_id = request.cookies.get(SESSION_COOKIE)

        if not session_id:
            session_id = secrets.token_urlsafe(32)
            request.state.session_id = session_id
            response: Response = await call_next(request)
            response.set_cookie(
                key=SESSION_COOKIE,
                value=session_id,
                httponly=True,
                samesite="lax",
                secure=False,  # set True in HTTPS
                max_age=60 * 60 * 24 * 10  # 10 days
            )
            return response

        request.state.session_id = session_id
        return await call_next(request)