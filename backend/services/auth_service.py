from passlib.context import CryptContext
from db import get_connection

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def register_user(email: str, name: str, password: str) -> tuple[bool, str]:
    '''
    registers a new user profile
    '''

def login_user(email: str, password: str) -> tuple[bool, str]:
    '''
    logs a user into their profile
    '''