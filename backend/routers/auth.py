# routers/auth.py
# Signup and login endpoints for CliniSight

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from database import get_connection
from auth import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

class UserSignup(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    role: str = "Receptionist"


@router.post("/signup")
def signup(user: UserSignup):
    """Registers a new CliniSight staff user."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT user_id FROM users WHERE email = %s",
                (user.email,)
            )

            existing = cursor.fetchone()

            if existing:
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )

            hashed = hash_password(user.password)

            cursor.execute("""
                INSERT INTO users (full_name, email, hashed_password, role)
                VALUES (%s, %s, %s, %s)
            """, (
                user.full_name,
                user.email,
                hashed,
                user.role
            ))

            connection.commit()
            new_id = cursor.lastrowid

        return {
            "status": "success",
            "user_id": new_id
        }

    except HTTPException:
        raise

    except Exception as e:
        connection.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        connection.close()


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Logs in a user. Note: form_data.username actually holds the email,
    per the OAuth2 password flow standard FastAPI follows.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s",
                (form_data.username,)
            )
            user = cursor.fetchone()

        if user is None or not verify_password(
            form_data.password,
            user["hashed_password"]
        ):
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password"
            )

        token = create_access_token({
            "user_id": user["user_id"],
            "email": user["email"],
            "role": user["role"]
        })

        return {
            "access_token": token,
            "token_type": "bearer"
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        connection.close()