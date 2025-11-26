from fletx.core import FletXService
from fletx.core.http import HTTPClient
from dotenv import load_dotenv
import os

load_dotenv()
class SignInService(FletXService):
    def __init__(self):
        # Get the backend URL from environment variable
        backend_url = os.getenv("BACKEND_URL", "http://localhost:3000")
        super().__init__(http_client=HTTPClient(base_url=backend_url))

    async def post(self, email: str, password: str):
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
            response = await self.http_client.post(               
                    endpoint="/api/auth/login",
                    json_data=payload          
                )


            return response
        except Exception as e:
            print(f"SignIn Error: {e}")
            raise


class SignUpService(FletXService):
    def __init__(self):
        # Get the backend URL from environment variable
        backend_url = os.getenv("BACKEND_URL", "http://localhost:3000")
        super().__init__(http_client=HTTPClient(base_url=backend_url))

    async def post(self, username: str, email: str, phone_number: str, password: str):
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
            response = await self.http_client.post(
                endpoint="/api/auth/register",
                json_data=payload
            )
            return response
        except Exception as e:
            print(f"SignUp Error: {e}")
            raise


class ForgotPasswordService(FletXService):
    def __init__(self):
        # Get the backend URL from environment variable
        backend_url = os.getenv("BACKEND_URL", "http://localhost:3000")
        super().__init__(http_client=HTTPClient(base_url=backend_url))

    async def post(self, email: str):
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
            response = await self.http_client.post(
                "/api/auth/forgot-password",
                data=payload
            )
            return response
        except Exception as e:
            print(f"ForgotPassword Error: {e}")
            raise


class RefreshTokenService(FletXService):
    def __init__(self):
        # Get the backend URL from environment variable
        backend_url = os.getenv("BACKEND_URL", "http://localhost:3000")
        super().__init__(http_client=HTTPClient(base_url=backend_url))

    async def post(self, refresh_token: str):
        """
        Refresh the access token
        
        Args:
            refresh_token: The refresh token
            
        Returns:
            Response with new access token
        """
        try:
            payload = {
                "refresh_token": refresh_token
            }
            response = await self.http_client.post(
                "/api/auth/refresh",
                data=payload
            )
            return response
        except Exception as e:
            print(f"RefreshToken Error: {e}")
            raise


class LogoutService(FletXService):
    def __init__(self):
        # Get the backend URL from environment variable
        backend_url = os.getenv("BACKEND_URL", "http://localhost:3000")
        super().__init__(http_client=HTTPClient(base_url=backend_url))

    async def post(self, token: str = None):
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
            response = await self.http_client.post(
                "/api/auth/logout",
                data=payload
            )
            return response
        except Exception as e:
            print(f"Logout Error: {e}")
            raise