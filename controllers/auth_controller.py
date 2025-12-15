from fletx.core import FletXController
from utils import get_storage
from services.auth_service import SignInService, SignUpService
import re

class SigninController(FletXController):
    def __init__(self):
        super().__init__()
        self.email = self.create_rx_str("")
        self.password = self.create_rx_str("")
        self.signin_error = self.create_rx_str("")
        self.is_valid = self.create_rx_bool(False)
        self.is_loading = self.create_rx_bool(False)
        
        # Initialize the SignIn service
        self.signin_service = SignInService()

    def on_ready(self):
        self.email.listen(self.validate_form)
        self.password.listen(self.validate_form)
        # Run initial validation
        self.validate_form()

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None

    def validate_form(self):
        """Validate signin form"""
        # Check if all fields are filled
        if not self.email.value or not self.password.value:
            self.signin_error.value = "All fields are required"
            self.is_valid.value = False
            return

        # Validate email format
        if not self.validate_email(self.email.value):
            self.signin_error.value = "Please enter a valid email address"
            self.is_valid.value = False
            return

        # Validate password is not empty (basic check for signin)
        if len(self.password.value) < 1:
            self.signin_error.value = "Password cannot be empty"
            self.is_valid.value = False
            return

        # All validations passed
        self.signin_error.value = ""
        self.is_valid.value = True
        print(f"SigninController: Form is valid! Email: {self.email.value}, is_valid: {self.is_valid.value}")

    def get_signin_data(self) -> dict:
        """Get signin form data as dictionary"""
        return {
            "email": self.email.value,
            "password": self.password.value
        }

    async def signin(self):
        """
        Perform sign in operation
        Returns: (success: bool, message: str, data: dict)
        """
        # Force validation before attempting signin
        self.validate_form()
        
        print(f"SigninController.signin() - is_valid: {self.is_valid.value}")
        print(f"SigninController.signin() - email: {self.email.value}")
        print(f"SigninController.signin() - password: {self.password.value}")
        
        if not self.is_valid.value:
            error_msg = self.signin_error.value or "Please fill in all fields correctly"
            return False, error_msg, None
        
        self.is_loading.value = True
        self.signin_error.value = ""
        
        try:
            # Call the signin service
            response = await self.signin_service.post(
                email=self.email.value,
                password=self.password.value
            )
            
            # Check if response is successful
            if response.status == 200:
                data = response.json()
                tokens = {
                    'access': data.get('data')['access_token'],
                    'refresh': data.get('data')['refresh_token']
                }
                get_storage().set('tokens', tokens)
                self.is_loading.value = False
                return True, "Sign in successful!", data
            else:
                error_data = response.json()
                error_message = error_data.get("message", "Sign in failed")
                self.signin_error.value = error_message
                self.is_loading.value = False
                return False, error_message, None
                
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            self.signin_error.value = error_message
            self.is_loading.value = False
            return False, error_message, None

    def reset_form(self):
        """Reset all form fields"""
        self.email.value = ""
        self.password.value = ""
        self.signin_error.value = ""
        self.is_valid.value = False
        self.is_loading.value = False


class ForgotPasswordController(FletXController):
    def __init__(self):
        super().__init__()
        self.email = self.create_rx_str("")
        self.error = self.create_rx_str("")
        self.success = self.create_rx_str("")
        self.is_valid = self.create_rx_bool(False)
        self.is_loading = self.create_rx_bool(False)

    def on_ready(self):
        self.email.listen(self.validate_form)
        # Run initial validation
        self.validate_form()

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None

    def validate_form(self):
        """Validate forgot password form"""
        # Clear previous messages
        self.success.value = ""
        
        # Check if email is filled
        if not self.email.value:
            self.error.value = "Email address is required"
            self.is_valid.value = False
            return

        # Check if email has content (strip whitespace)
        if not self.email.value.strip():
            self.error.value = "Email address is required"
            self.is_valid.value = False
            return

        # Validate email format
        if not self.validate_email(self.email.value):
            self.error.value = "Please enter a valid email address"
            self.is_valid.value = False
            return

        # All validations passed
        self.error.value = ""
        self.is_valid.value = True
        print(f"ForgotPasswordController: Form is valid! Email: {self.email.value}, is_valid: {self.is_valid.value}")

    def send_reset_link(self) -> bool:
        """
        Send password reset link
        Returns: True if successful, False otherwise
        """
        if not self.is_valid.value:
            return False

        self.is_loading.value = True
        self.error.value = ""
        self.success.value = ""

        try:
            # TODO: Implement actual password reset logic here
            # Example: Call your backend API
            # response = api.send_password_reset(self.email.value)
            
            # Simulate success for now
            self.success.value = f"Password reset link sent to {self.email.value}"
            self.is_loading.value = False
            return True
            
        except Exception as e:
            self.error.value = f"Failed to send reset link: {str(e)}"
            self.is_loading.value = False
            return False

    def get_email(self) -> str:
        """Get the email address"""
        return self.email.value

    def reset_form(self):
        """Reset all form fields"""
        self.email.value = ""
        self.error.value = ""
        self.success.value = ""
        self.is_valid.value = False
        self.is_loading.value = False


class SignupController(FletXController):
    def __init__(self):
        super().__init__()
        self.username = self.create_rx_str("")
        self.email = self.create_rx_str("")
        self.phone_number = self.create_rx_str("")
        self.password = self.create_rx_str("")
        self.confirm_password = self.create_rx_str("")
        self.signup_error = self.create_rx_str("")
        self.is_valid = self.create_rx_bool(False)
        self.is_loading = self.create_rx_bool(False)
        
        # Initialize the SignUp service
        self.signup_service = SignUpService()

    def on_ready(self):
        self.username.listen(self.validate_form)
        self.email.listen(self.validate_form)
        self.phone_number.listen(self.validate_form)
        self.password.listen(self.validate_form)
        self.confirm_password.listen(self.validate_form)

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None

    def validate_eswatini_phone(self, phone: str) -> tuple[bool, str]:
        """
        Validate Eswatini phone number format
        Eswatini uses country code +268
        Mobile numbers: 7XXX XXXX or 76XX XXXX, 78XX XXXX, 79XX XXXX
        Returns: (is_valid, error_message)
        """
        # Remove spaces, dashes, and parentheses
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        # Check various valid formats
        patterns = [
            r'^268[67]\d{7}$',           # 2687XXXXXXX or 2686XXXXXXX (country code without +)
            r'^\+268[67]\d{7}$',         # +2687XXXXXXX or +2686XXXXXXX (country code with +)
            r'^[67]\d{7}$',              # 7XXXXXXX or 6XXXXXXX (local format 8 digits)
            r'^0[67]\d{7}$',             # 07XXXXXXX or 06XXXXXXX (local format with leading 0)
        ]
        
        for pattern in patterns:
            if re.match(pattern, cleaned_phone):
                return True, ""
        
        return False, "Please enter a valid Eswatini phone number (e.g., +268 7XXX XXXX, 07XXX XXXX, or 7XXX XXXX)"

    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """
        Validate password strength
        Returns: (is_valid, error_message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, ""

    def validate_username(self, username: str) -> tuple[bool, str]:
        """
        Validate username
        Returns: (is_valid, error_message)
        """
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 20:
            return False, "Username must not exceed 20 characters"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, ""

    def validate_form(self):
        """Validate entire signup form"""
        # Check if all required fields are filled
        if not all([self.username.value, self.email.value, self.phone_number.value,
                   self.password.value, self.confirm_password.value]):
            self.signup_error.value = "All fields are required"
            self.is_valid.value = False
            return

        # Validate username
        username_valid, username_error = self.validate_username(self.username.value)
        if not username_valid:
            self.signup_error.value = username_error
            self.is_valid.value = False
            return

        # Validate email
        if not self.validate_email(self.email.value):
            self.signup_error.value = "Please enter a valid email address"
            self.is_valid.value = False
            return

        # Validate phone number
        phone_valid, phone_error = self.validate_eswatini_phone(self.phone_number.value)
        if not phone_valid:
            self.signup_error.value = phone_error
            self.is_valid.value = False
            return

        # Validate password strength
        password_valid, password_error = self.validate_password_strength(self.password.value)
        if not password_valid:
            self.signup_error.value = password_error
            self.is_valid.value = False
            return

        # Check if passwords match
        if self.password.value != self.confirm_password.value:
            self.signup_error.value = "Passwords do not match"
            self.is_valid.value = False
            return

        # All validations passed
        self.signup_error.value = ""
        self.is_valid.value = True

    def get_signup_data(self) -> dict:
        """Get signup form data as dictionary"""
        return {
            "username": self.username.value,
            "email": self.email.value,
            "phone_number": self.phone_number.value,
            "password": self.password.value
        }

    async def signup(self):
        """
        Perform sign up operation
        Returns: (success: bool, message: str, data: dict)
        """
        # Force validation before attempting signup
        self.validate_form()
        
        print(f"SignupController.signup() - is_valid: {self.is_valid.value}")
        print(f"SignupController.signup() - username: {self.username.value}")
        print(f"SignupController.signup() - email: {self.email.value}")
        print(f"SignupController.signup() - phone: {self.phone_number.value}")
        
        if not self.is_valid.value:
            error_msg = self.signup_error.value or "Please fill in all fields correctly"
            return False, error_msg, None
        
        self.is_loading.value = True
        self.signup_error.value = ""
        
        try:
            # Call the signup service
            response = await self.signup_service.post(
                username=self.username.value,
                email=self.email.value,
                password=self.password.value,
                phone_number=self.phone_number.value
            )
            
            # Check if response is successful
            if response.status == 201:  # 201 Created for registration
                data = response.json()
                self.is_loading.value = False
                return True, "Sign up successful!", data
            else:
                error_data = response.json()
                error_message = error_data.get("message", "Sign up failed")
                self.signup_error.value = error_message
                self.is_loading.value = False
                return False, error_message, None
                
        except Exception as e:
            error_message = f"An error occurred: {str(e)}"
            self.signup_error.value = error_message
            self.is_loading.value = False
            return False, error_message, None

    def reset_form(self):
        """Reset all form fields"""
        self.username.value = ""
        self.email.value = ""
        self.phone_number.value = ""
        self.password.value = ""
        self.confirm_password.value = ""
        self.signup_error.value = ""
        self.is_valid.value = False
        self.is_loading.value = False