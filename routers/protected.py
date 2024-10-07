from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta
from auth import create_access_token, verify_token, authenticate_user
from db.database import engine,SessionLocal



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(login_request: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_request.username, login_request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=30)  # or another expiration time
    access_token = create_access_token(data={"sub": user.usuario}, expires_delta=access_token_expires)

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/protected")
async def protected_route(token: str, db: Session = Depends(get_db)):
    try:
        decoded_token = verify_token(token)
        # Optionally, you can use decoded_token["sub"] to fetch user details if needed
        return {"message": "Access granted", "user": decoded_token["sub"]}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
