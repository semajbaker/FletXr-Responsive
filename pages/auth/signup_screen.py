import flet as ft
from fletx.core import FletXPage
from fletx.navigation import navigate
from widgets.animated_box import animated_box
from utils.animation_manager import AnimationManager
from widgets.input_field import input_field
from widgets.main_auth_btn import main_auth_btn
from controllers.animation_controller import AnimationController
from controllers.auth_controller import SignupController
from constants.ui_constants import AppColors
from widgets.auth_action_controlls import auth_action_controlls

class SignUpScreen(FletXPage):
    def __init__(self):
        super().__init__()
        self.box1 = animated_box(ft.Colors.PINK_400, ft.Colors.PURPLE_300, 1.0)
        self.box2 = animated_box(ft.Colors.CYAN_400, ft.Colors.TEAL_300, 0.8)
        self.box3 = animated_box(ft.Colors.AMBER_400, ft.Colors.ORANGE_300, 1.2)
        self.box4 = animated_box(ft.Colors.GREEN_400, ft.Colors.LIGHT_GREEN_300, 0.9)
        self.animation_ctrl = AnimationController()
        self.animation_manager = None
        
        # Initialize SignupController
        self.signup_controller = SignupController()
        
        # Create error text that will update reactively
        self.error_text = ft.Text(
            value="",
            size=12,
            color=ft.Colors.RED_400,
            text_align=ft.TextAlign.CENTER,
            visible=False
        )
        
        # Create success text for validation feedback
        self.success_text = ft.Text(
            value="",
            size=12,
            color=ft.Colors.GREEN_600,
            text_align=ft.TextAlign.CENTER,
            visible=False
        )
        
    def on_init(self):
        """Initialize animation and controller after page is ready"""
        # Create animation manager with page reference and controller
        self.animation_manager = AnimationManager(self.page, self.animation_ctrl)
        
        # Set the boxes to animate
        self.animation_manager.set_boxes(self.box1, self.box2, self.box3, self.box4)
        
        # Start animation using controller
        self.animation_ctrl.start_animation()
        
        # Set up listener for signup error
        self.signup_controller.signup_error.listen(self._on_error_changed)
        self.signup_controller.is_valid.listen(self._on_validation_changed)
    
    def _on_error_changed(self):
        """Handle error message changes"""
        if self.signup_controller.signup_error.value:
            self.error_text.value = self.signup_controller.signup_error.value
            self.error_text.visible = True
            self.success_text.visible = False
        else:
            self.error_text.visible = False
        self.error_text.update()
    
    def _on_validation_changed(self):
        """Handle validation state changes"""
        if self.signup_controller.is_valid.value:
            self.success_text.value = "All fields are valid! ✓"
            self.success_text.visible = True
            self.error_text.visible = False
            self.success_text.update()
        else:
            self.success_text.visible = False
            if hasattr(self, 'success_text') and self.success_text.page:
                self.success_text.update()
    
    def handle_signup(self, e):
        """Handle sign up button click"""
        print(f"Sign Up clicked!")
        
        # Validate form one more time
        self.signup_controller.validate_form()
        
        if self.signup_controller.is_valid.value:
            # Get form data
            signup_data = self.signup_controller.get_signup_data()
            print(f"Username: {signup_data['username']}")
            print(f"Email: {signup_data['email']}")
            print(f"Password: {signup_data['password']}")
            
            print("Form is valid, proceeding with sign up...")
            # Call your backend service here
            # Example:
            # response = backend_service.signup(signup_data)
            # if response.success:
            #     navigate("/signin")
            
            # For now, show success and optionally reset form
            # self.signup_controller.reset_form()
        else:
            print("Form validation failed")
            print(f"Error: {self.signup_controller.signup_error.value}")
    
    def on_unmount(self):
        """Stop animation when leaving the page"""
        if self.animation_ctrl:
            self.animation_ctrl.stop_animation()
        
    def go_to_signin(self, e):
        """Navigate to signin screen"""
        print("Navigating to signin...")
        # Stop animation before navigating using controller
        if self.animation_ctrl:
            self.animation_ctrl.stop_animation()
        navigate("/signin", replace=True, clear_history=True)

    def build(self):
        return ft.Container(
            bgcolor=AppColors.LIGHT['background'],
            margin=ft.margin.all(0),
            alignment=ft.alignment.center,
            padding=ft.padding.all(20),
            content=ft.Card(
                width=520,
                height=760,
                elevation=8,
                surface_tint_color=AppColors.LIGHT['surface'],
                color=AppColors.LIGHT['background'],
                shadow_color=ft.Colors.with_opacity(0.15, AppColors.LIGHT['shadow']),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                    auto_scroll=True,
                    expand=True,
                    controls=[
                        ft.Container(height=30),
                        ft.Container(
                            width=200,
                            height=120,
                            content=ft.Stack(
                                controls=[
                                    ft.Container(
                                        left=70,
                                        top=30,
                                        content=self.box1
                                    ),
                                    ft.Container(
                                        left=130,
                                        top=50,
                                        content=self.box2
                                    ),
                                    ft.Container(
                                        left=40,
                                        top=60,
                                        content=self.box3
                                    ),
                                    ft.Container(
                                        left=100,
                                        top=10,
                                        content=self.box4
                                    ),
                                ]
                            )
                        ),
                        ft.Container(height=25),
                        ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                            controls=[
                                ft.Text(
                                    "Sign Up", 
                                    size=32, 
                                    weight=ft.FontWeight.BOLD, 
                                    color=ft.Colors.BLUE_GREY_800
                                ),
                                ft.Text(
                                    "Python Flet(Flutter for Python) UI", 
                                    size=16,
                                    color=ft.Colors.BLUE_GREY_500,
                                    weight=ft.FontWeight.W_400
                                ),
                            ]
                        ),
                        ft.Container(height=25),
                        # Username input field with reactive binding
                        input_field(
                            "Enter your username", 
                            ft.Icons.VERIFIED_USER_OUTLINED, 
                            hide=False,
                            rx_value=self.signup_controller.username
                        ),
                        ft.Container(height=20),
                        # Email input field with reactive binding
                        input_field(
                            "Enter your email address", 
                            ft.Icons.ALTERNATE_EMAIL, 
                            hide=False,
                            rx_value=self.signup_controller.email
                        ),
                        ft.Container(height=20),
                        # Password input field with reactive binding
                        input_field(
                            "Enter your password", 
                            ft.Icons.LOCK_OUTLINE, 
                            hide=True,
                            rx_value=self.signup_controller.password
                        ),
                        ft.Container(height=20),
                        # Confirm password input field with reactive binding
                        input_field(
                            "Repeat your password", 
                            ft.Icons.LOCK_OUTLINE, 
                            hide=True,
                            rx_value=self.signup_controller.confirm_password
                        ),
                        ft.Container(height=10),
                        # Error message display
                        self.error_text,
                        # Success message display
                        self.success_text,
                        ft.Container(height=15),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                auth_action_controlls(
                                    primary_action_text="Sign In",
                                    primary_action_on_click=self.go_to_signin,
                                    show_forgot_password=False,
                                    forgot_password_on_click=None
                                )
                            ]
                        ),
                        ft.Container(height=20),
                        main_auth_btn("Sign Up", on_click=self.handle_signup),
                        ft.Container(height=25),
                    ]
                ),
            ),
        )