from fastapi import APIRouter, HTTPException, Request

from app.config import DEMO_PASSWORD, DEMO_USERNAME
from app.schemas import LoginRequest

router = APIRouter(tags=["auth"])


@router.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/api/login")
def login(credentials: LoginRequest, request: Request) -> dict[str, bool]:
    is_valid = (
        credentials.username == DEMO_USERNAME and credentials.password == DEMO_PASSWORD
    )
    if not is_valid:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    request.session["user"] = credentials.username
    return {"ok": True}


@router.post("/api/logout")
def logout(request: Request) -> dict[str, bool]:
    request.session.clear()
    return {"ok": True}


@router.get("/api/session")
def session(request: Request) -> dict[str, bool]:
    return {"authenticated": "user" in request.session}
