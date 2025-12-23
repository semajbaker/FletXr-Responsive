import flet as ft
from fletx import FletX
from fletx.core import FletXPage
from fletx.navigation import navigate
from widgets.animated_box import animated_box
from widgets.input_field import input_field
from widgets.main_auth_btn import main_auth_btn
from widgets.auth_action_controls import auth_action_controlls
from widgets.auth_divider import auth_divider
from widgets.loading_inicator import loading_indicator
from widgets.snackbar_message import SnackbarMessage
from controllers.auth_controller import SignUpController
from utils.animation_manager import AnimationManager
from constants.ui_constants import AppColors
from utils.responsive_manager import MediaQuery

class SignUpScreen(FletXPage):
    def __init__(self):
        super().__init__()
        self.box1 = animated_box(ft.Colors.PINK_400, ft.Colors.PURPLE_300, 1.0)
        self.box2 = animated_box(ft.Colors.CYAN_400, ft.Colors.TEAL_300, 0.8)
        self.box3 = animated_box(ft.Colors.AMBER_400, ft.Colors.ORANGE_300, 1.2)
        self.box4 = animated_box(ft.Colors.GREEN_400, ft.Colors.LIGHT_GREEN_300, 0.9)
        self.widgets_to_cleanup = []
        self.signup_controller: SignUpController = FletX.find(
            SignUpController, tag='signup_ctrl'
        )
        # Initialize snackbar widget
        self.snackbar = SnackbarMessage()

    def on_init(self):
        # This will attach a NEW listener to the EXISTING controller
        AnimationManager.initialize_with_page(self.page)
        AnimationManager.set_boxes(self.box1, self.box2, self.box3, self.box4)
        AnimationManager.start_animation()
        MediaQuery.update_page_reference(self.page)
        MediaQuery.debug_all_listeners()
        self.watch(
            self.signup_controller._is_loading,
            lambda: loading_indicator(
                controller = self.signup_controller,
                page = self.page_instance,
                message= "Signing up..."
            ),
            immediate = True,
        )
        
    def on_destroy(self):
        # Cleanup widgets
        for widget in self.widgets_to_cleanup:
            if hasattr(widget, 'will_unmount'):
                try:
                    widget.will_unmount()
                except Exception as e:
                    print(f"Error cleaning up widget {widget}: {e}")
        # Clear the list
        self.widgets_to_cleanup.clear()
        AnimationManager.cleanup()
        MediaQuery.reset_all()
        print("Signup Screen destroyed")

    def handle_signup(self, e):
        """Handle sign up button click"""
        print(f"Sign Up clicked!")
        print(f"Username: {self.signup_controller.username.value}")
        print(f"Email: {self.signup_controller.email.value}")
        # Call the signup method from controller
        success, message, data = self.signup_controller.signup()
        
        if success:
            print(f"Message: {message}")
            print(f"User data: {data}")
            self.snackbar.show_success(self.page, message)
            self.signup_controller.reset_form()
            navigate("/signin")
        else:
            print(f"Sign up failed: {message}")
            self.snackbar.show_error(self.page, message)

    def goto_signin(self, e):
        self.will_unmount()
        navigate("/signin")

    def build(self):
        username_field = input_field(
            "Enter your username", 
            ft.Icons.VERIFIED_USER_OUTLINED, 
            hide=False,
            rx_value=self.signup_controller.username
        )
        email_field = input_field(
            "Enter your email address", 
            ft.Icons.ALTERNATE_EMAIL, 
            hide=False,
            rx_value=self.signup_controller.email
        )
        phonenumber_field = input_field(
            "Enter your phone number", 
            ft.Icons.PHONE, 
            hide=False,
            rx_value=self.signup_controller.phone_number
        )
        password_field = input_field(
            "Enter your password", 
            ft.Icons.LOCK_OUTLINE, 
            hide=True,
            rx_value=self.signup_controller.password
        )
        repeat_password_field = input_field(
            "Repeat your password", 
            ft.Icons.LOCK_OUTLINE, 
            hide=True,
            rx_value=self.signup_controller.confirm_password
        )
        auth_controls = auth_action_controlls(
            primary_action_text="Sign In",
            primary_action_on_click=self.goto_signin,
            show_forgot_password=False,
            forgot_password_on_click=None
        )
        main_btn = main_auth_btn("Sign Up", on_click=self.handle_signup)
        divider = auth_divider()
        
        self.widgets_to_cleanup.append(username_field)
        self.widgets_to_cleanup.append(email_field)
        self.widgets_to_cleanup.append(phonenumber_field)
        self.widgets_to_cleanup.append(password_field)
        self.widgets_to_cleanup.append(repeat_password_field)
        self.widgets_to_cleanup.append(auth_controls)
        self.widgets_to_cleanup.append(main_btn)
        self.widgets_to_cleanup.append(divider)
        
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
                        username_field,
                        ft.Container(height=20),
                        # Email input field with reactive binding
                        email_field,
                        ft.Container(height=20),
                        # Phone number input field with reactive binding
                        phonenumber_field,
                        ft.Container(height=20),
                        # Password input field with reactive binding
                        password_field,
                        ft.Container(height=20),
                        # Confirm password input field with reactive binding
                        repeat_password_field,
                        ft.Container(height=10),
                        # Error message display
                        ft.Container(height=15),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                auth_controls
                            ]
                        ),
                        ft.Container(height=20),
                        main_btn,
                        ft.Container(height=25),
                        divider,
                        ft.Container(height=25),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=15,
                            controls=[
                                ft.Container(
                                    width=100,
                                    height=50,
                                    content=ft.FloatingActionButton(
                                        content=ft.Icon(
                                            ft.Icons.EMAIL, 
                                            size=20, 
                                            color=ft.Colors.BLUE_GREY_400
                                        ),
                                        width=30,
                                        height=30,
                                        bgcolor=ft.Colors.WHITE,
                                        shape=ft.CircleBorder(),
                                        elevation=3,
                                        tooltip="Continue with Google",
                                        on_click=self.goto_signin
                                    ),
                                ),
                                ft.Container(
                                    width=100,
                                    height=50,
                                    content=ft.FloatingActionButton(
                                        content=ft.Icon(
                                            ft.Icons.CODE, 
                                            size=20, 
                                            color=ft.Colors.BLUE_GREY_400
                                        ),
                                        width=30,
                                        height=30,
                                        bgcolor=ft.Colors.WHITE,
                                        shape=ft.CircleBorder(),
                                        elevation=3,
                                        tooltip="Continue with Github",
                                    ),
                                ),
                            ]
                        ),
                        ft.Container(height=20),
                    ]
                ),
            ),
        )