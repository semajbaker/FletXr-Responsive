from fletx.core import FletXController, RxStr
from fletx.decorators import reactive_form

@reactive_form(
    form_fields={
        'email': 'rx_email',
        'password': 'rx_password',
    },
    validation_rules={
        'email': 'email_regex',         
        'password': 'validate_pass',    
    },
    on_submit = 'perform_submit',  
    on_submit_failed = 'show_erros',
    auto_validate = True
)

class AuthController(FletXController):
    def __init__(self, page):
        super().__init__(page)
        self.rx_email = RxStr("")
        self.rx_password = RxStr("")

    def perform_submit(self):
        print("Form submitted successfully!")
        print(f"Email: {self.rx_email.value}")
        print(f"Password: {self.rx_password.value}")

    def show_erros(self, errors):
        print("Form submission failed with errors:")
        for field, error in errors.items():
            print(f"{field}: {error}")

    def validate_pass(self, value):
        if len(value) < 6:
            return "Password must be at least 6 characters long."
        return None