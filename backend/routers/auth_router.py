from fastapi import APIRouter, Response, status
from pydantic import BaseModel
from services.auth_service import register_user, login_user

router = APIRouter(prefix="/auth")

class RegisterRequest(BaseModel):
    email: str
    name: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
def register(payload: RegisterRequest, response: Response):
    success, message = register_user(payload.email, payload.name, payload.password)
    if not success:
        response.status_code = status.HTTP_400_BAD_REQUEST
    return {"success": success, "message": message}

@router.post("/login")
def login(payload: LoginRequest, response: Response):
    success, message = login_user(payload.email, payload.password)
    if not success:
        response.status_code = status.HTTP_401_UNAUTHORIZED
    return {"success": success, "message": message}