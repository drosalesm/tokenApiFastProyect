# utils/authentication.py

import jwt
from datetime import datetime, timedelta
from typing import Dict
from models.models import Usuarios
from utils import verify_password
from db.database import engine,SessionLocal
from sqlalchemy.orm import Session

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def create_access_token(data: Dict[str, str], expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, str]:
    try:
        decoded_jwt = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return decoded_jwt
    except jwt.ExpiredSignatureError:
        raise Exception("Token has expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")


def authenticate_user(db: Session, username: str, password: str) -> Usuarios:
    user = db.query(Usuarios).filter(Usuarios.usuario == username).first()
    if user is None:
        return False
    if not verify_password(password, user.password):
        return False
    return user