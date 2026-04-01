import bcrypt
from db import get_connection

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())

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
                   VALUES (:user_id, :email, :name, SYSDATE, :password_hash)""",
                {"user_id": user_id, "email": email, "name": name, "password_hash": hashed}
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