import itsdangerous
import os
import secrets
from db.database import SessionLocal
import uuid
import bcrypt
from cryptography.fernet import Fernet
import json
import base64





# config.py

SECRET_KEY = "your_secret_key_here"  # Replace with a strong key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Token expiration time in minutes



def create_api_response(uti="", status="", code="", message="", information=[]):

    return {
        "generalResponse": {
            "uti": uti,
            "status": status,
            "code": code,
            "message": message
        },
        "information": information
    }
    

key = Fernet.generate_key()
cipher_suite = Fernet(key)

    
def hash_password(password: str) -> str:
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')



def verify_password(password: str, hashed_password: str) -> bool:
    # Check if the provided password matches the hashed password
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))




def hash_nombre(nombre: str) -> str:
    # Hash the 'nombre' using bcrypt
    hashed = bcrypt.hashpw(nombre.encode(), bcrypt.gensalt())
    return hashed.decode()

def check_nombre(plain_nombre: str, hashed_nombre: str) -> bool:
    # Verify the 'nombre' using bcrypt
    return bcrypt.checkpw(plain_nombre.encode(), hashed_nombre.encode())




# Encode (like encryption but easily reversible)
def encrypt_data(data: str) -> str:
    encoded_data = base64.b64encode(data.encode()).decode()
    return encoded_data

# Decode (reverse the encoding)
def decrypt_data(encoded_data: str) -> str:
    decoded_data = base64.b64decode(encoded_data.encode()).decode()
    return decoded_data
    
    



def parse_json_field(field):
    """Helper function to parse JSON fields safely."""
    try:
        return json.loads(field) if field else None
    except json.JSONDecodeError:
        return None
