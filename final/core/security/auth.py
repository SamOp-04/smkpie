from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from core.database.supabase_crud import SupabaseCRUD

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        supabase_crud = SupabaseCRUD()
        # Fetch user by API token
        user = supabase_crud.get_user_by_token(token)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API token"
            )
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )
