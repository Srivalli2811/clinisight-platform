from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Decodes JWT from Authorization header.
    Returns user dict if valid. Raises 401 if missing, invalid, or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = payload.get("user_id")
        email = payload.get("email")
        role = payload.get("role")

        if user_id is None:
            raise credentials_exception

        return {
            "user_id": user_id,
            "email": email,
            "role": role
        }
    except JWTError:
        raise credentials_exception
    
def require_admin(current_user: dict = Depends(get_current_user)):
    """
    Chains on top of get_current_user.
    Raises 403 if the logged-in user is not an Admin.
    """
    if current_user["role"] != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return current_user