from fletx.core import FletXController
import re
class SigninController(FletXController):
    def __init__(self):
        super().__init__()
        self.email = self.create_rx_str("")
        self.password = self.create_rx_str("")
        self.signin_error = self.create_rx_str("")

    def on_ready(self):
        self.email.listen(self.validate_form)
        self.password.listen(self.validate_form)

    def validate_form(self):
        if self.email.value and self.password.value:
            self.signin_error.value = ""
        else:
            self.signin_error.value = "All fields are required"

class SignupController(FletXController):
    def __init__(self):
        super().__init__()
        self.username = self.create_rx_str("")
        self.email = self.create_rx_str("")
        self.password = self.create_rx_str("")
        self.confirm_password = self.create_rx_str("")
        self.signup_error = self.create_rx_str("")
        self.is_valid = self.create_rx_bool(False)

    def on_ready(self):
        self.username.listen(self.validate_form)
        self.email.listen(self.validate_form)
        self.password.listen(self.validate_form)
        self.confirm_password.listen(self.validate_form)

    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None

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
        # Check if all fields are filled
        if not all([self.username.value, self.email.value, 
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
            "password": self.password.value
        }

    def reset_form(self):
        """Reset all form fields"""
        self.username.value = ""
        self.email.value = ""
        self.password.value = ""
        self.confirm_password.value = ""
        self.signup_error.value = ""
        self.is_valid.value = False