from datetime import UTC, datetime, timedelta
from hashlib import sha256

import jwt
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from ..config import SECRET_KEY

oauth_scheme = OAuth2PasswordBearer(tokenUrl='/api/auth/login')


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'


class Auth:
    @staticmethod
    def generate_jwt(user_registration: str) -> str:
        """
        Generate a JSON Web Token (JWT) for the user.

        :param user_registration: The user's registration.
        :type user_id: str

        :return: The JWT.
        :rtype: str
        """
        payload = {
            'user_registration': user_registration,
            'exp': datetime.now(UTC) + timedelta(days=7),
            'secret': SECRET_KEY,
        }
        return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

    @staticmethod
    def decode_jwt(token: str) -> dict | None:
        """
        Decode a JSON Web Token (JWT).

        :param token: The JWT.
        :type token: str

        :return: The decoded JWT.
        :rtype: dict | None
        """
        try:
            return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    def encrypt_password(password: str) -> str:
        """
        Encrypt the password using SHA-256.

        :param password: The password.
        :type password: str

        :return: The hashed password.
        :rtype: str
        """
        password += SECRET_KEY
        return sha256(password.encode()).hexdigest()

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify the password.

        :param password: The password.
        :type password: str
        :param hashed_password: The hashed password.
        :type hashed_password: str

        :return: True if the password is correct, False otherwise.
        :rtype: bool
        """
        return hashed_password == Auth.encrypt_password(password)
