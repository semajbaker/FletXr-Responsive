import os
from typing import Optional
from dotenv import load_dotenv

from fletx.core import FletXService
from fletx.core.http import HTTPClient

from app.utils import get_storage

load_dotenv()
class SignInService(FletXService):
    def __init__(self, *args, **kwargs):
        # Get the backend URL from environment variable
        backend_url = os.getenv("BACKEND_URL", "http://localhost:5000")
        super().__init__(http_client=HTTPClient(base_url=backend_url, sync_mode=True), **kwargs)

    def post(self, email: str, password: str):
        """
        Sign in user with email and password
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Response from the backend API
        """
        try:
            payload = {
                "email": email,
                "password": password
            }
            return self.http_client.post(
                endpoint = '/api/auth/login',
                json_data = payload,
                headers = {
                    'Content-Type': 'application/json'
                }
            )
        except Exception as e:
            print(f"SignIn Error: {e}")
            raise


class SignUpService(FletXService):
    def __init__(self, *args, **kwargs):
        # Get the backend URL from environment variable
        backend_url = os.getenv("BACKEND_URL", "http://localhost:5000")
        super().__init__(http_client=HTTPClient(base_url=backend_url, sync_mode=True), **kwargs)

    def post(self, username: str, email: str, phone_number: str, password: str):
        """
        Register a new user
        
        Args:
            username: User's username
            email: User's email address
            password: User's password
            
        Returns:
            Response from the backend API
        """
        try:
            payload = {
                "username": username,
                "email": email,
                "phone_number": phone_number,
                "password": password
            }
            return self.http_client.post(
                endpoint="/api/auth/register",
                json_data=payload,
                headers = {
                    'Content-Type': 'application/json'
                }
            )
        except Exception as e:
            print(f"SignUp Error: {e}")
            raise


class ForgotPasswordService(FletXService):
    def __init__(self, *args, **kwargs):
        # Get the backend URL from environment variable
        backend_url = os.getenv("BACKEND_URL", "http://localhost:5000")
        super().__init__(http_client=HTTPClient(base_url=backend_url, sync_mode=True), **kwargs)

    def post(self, email: str):
        """
        Send password reset link to user's email
        
        Args:
            email: User's email address
            
        Returns:
            Response from the backend API
        """
        try:
            payload = {
                "email": email
            }
            return self.http_client.post(
                "/api/auth/forgot-password",
                data=payload,
                headers = {
                    'Content-Type': 'application/json'
                }
            )
        except Exception as e:
            print(f"ForgotPassword Error: {e}")
            raise


class SessionService(FletXService):
    def __init__(self, *args, **kwargs):
        # Get the backend URL from environment variable
        backend_url = os.getenv("BACKEND_URL", "http://localhost:5000")
        super().__init__(http_client=HTTPClient(base_url=backend_url,  sync_mode=True), **kwargs)
    
    def get_token(self, name: str):
        """Return saved token from Client Storage"""

        tokens: dict = (
            get_storage().get('tokens') 
            if get_storage().contains_key('tokens')
            else {}
        )
        return tokens.get(name)

    def refresh_token(self):
        """Refresh auth tokens"""

        # Get the REFRESH token, not access token
        token = self.get_token('access')  # ✅
        
        if not token:
            raise Exception("No access token available")

        return self.http_client.post(
            endpoint = '/api/auth/refresh-token',
            json_data = {
                "refreshToken": f"{token}"
            },
            headers = {
                'Content-Type': 'application/json'
            }
        )
    
    def get_profile(self):
        """Get user profile by a given token."""

        token = self.get_token('access')

        return self.http_client.get(
            endpoint = '/api/auth/profile',
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )


class LogoutService(FletXService):
    def __init__(self, *args, **kwargs):
        # Get the backend URL from environment variable
        backend_url = os.getenv("BACKEND_URL", "http://localhost:5000")
        super().__init__(http_client=HTTPClient(base_url=backend_url, sync_mode=True), **kwargs)

    def post(self, token: Optional[str] = None):
        """
        Logout user
        
        Args:
            token: Optional token to invalidate
            
        Returns:
            Response from the backend API
        """
        try:
            payload = {}
            if token:
                payload["token"] = token
            response = self.http_client.post(
                "/api/auth/logout",
                data=payload
            )
            return response
        except Exception as e:
            print(f"Logout Error: {e}")
            raise