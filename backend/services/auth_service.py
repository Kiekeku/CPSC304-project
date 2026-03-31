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
    hashed = hash_password(password)
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT NVL(MAX(user_id), 0) + 1 FROM Calibrated_User")
            user_id = cursor.fetchone()[0]
            cursor.execute(
                """INSERT INTO Calibrated_User (user_id, email, name, date_of_creation, password_hash)
                   VALUES (:uid, :email, :name, SYSDATE, :pw)""",
                {"uid": user_id, "email": email, "name": name, "pw": hashed}
            )
            conn.commit()
            return True, "Registered successfully"
    except Exception as e:
        return False, str(e)

def login_user(email: str, password: str) -> tuple[bool, str]:
    '''
    logs a user into their profile
    '''
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, password_hash FROM Calibrated_User WHERE email = :email",
                {"email": email}
            )
            row = cursor.fetchone()
            if not row or not verify_password(password, row[1]):
                return False, "Invalid email or password"
            return True, str(row[0])  # returns user_id as string
    except Exception as e:
        return False, str(e)