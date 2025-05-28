from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel
from core.security.rate_limiter import rate_limit
from core.database.supabase_crud import SupabaseCRUD

router = APIRouter(tags=["Authentication"], prefix="/auth")

class UserSignup(BaseModel):
    email: str
    password: str

@router.post("/signup")
async def signup(user: UserSignup):
    crud = SupabaseCRUD()

    if crud.user_exists_by_email(user.email):
        raise HTTPException(400, "Email already registered")

    try:
        new_user = crud.create_user(user.email, user.password)
        return {"api_token": new_user["api_token"]}
    except Exception as e:
        raise HTTPException(400, str(e))

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/login")
async def login(user: UserLogin):
    await rate_limit(user.email)
    crud = SupabaseCRUD()

    try:
        auth_user = crud.authenticate_user(user.email, user.password)
    except Exception as e:
        raise HTTPException(401, str(e))

    return {"api_token": auth_user["api_token"]}

@router.post("/logout")
async def logout(authorization: str = Header(...)):
    crud = SupabaseCRUD()

    token = authorization.replace("Bearer ", "")
    try:
        crud.invalidate_token(token)  # This method should be implemented in your SupabaseCRUD
        return {"detail": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(400, str(e))
    