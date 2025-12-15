import flet as ft
from fletx.core import FletXPage
from utils.navigation_helper import safe_navigate
from utils.animation_manager import AnimationManager
from widgets.animated_box import animated_box
from widgets.input_field import input_field
from widgets.main_auth_btn import main_auth_btn
from widgets.auth_action_controlls import auth_action_controlls
from widgets.auth_divider import auth_divider
from controllers.auth_controller import SigninController
from constants.ui_constants import AppColors
from utils.responsive_manager import MediaQuery

class SignInScreen(FletXPage):
    def __init__(self):
        super().__init__()
        self.box1 = animated_box(ft.Colors.PINK_400, ft.Colors.PURPLE_300, 1.0)
        self.box2 = animated_box(ft.Colors.CYAN_400, ft.Colors.TEAL_300, 0.8)
        self.box3 = animated_box(ft.Colors.AMBER_400, ft.Colors.ORANGE_300, 1.2)
        self.box4 = animated_box(ft.Colors.GREEN_400, ft.Colors.LIGHT_GREEN_300, 0.9)
        self.widgets_to_cleanup = []
        # Initialize SigninController
        self.signin_controller = SigninController()
        
        # Create error text that will update reactively
        self.error_text = ft.Text(
            value="",
            size=12,
            color=ft.Colors.RED_400,
            text_align=ft.TextAlign.CENTER,
            visible=False
        )
        
    def on_init(self):
        """Initialize animation and controller after page is ready"""
        print("SignInScreen: on_init called")
        
        # Initialize AnimationManager with page reference
        # This will attach a NEW listener to the EXISTING controller
        AnimationManager.initialize_with_page(self.page)
        
        # Set the boxes to animate
        AnimationManager.set_boxes(self.box1, self.box2, self.box3, self.box4)
        
        # Start animation
        AnimationManager.start_animation()
        
        MediaQuery.update_page_reference(self.page)
        MediaQuery.debug_all_listeners()
        
        # Set up listener for signin error
        self.signin_controller.signin_error.listen(self._on_error_changed)
        
    def will_unmount(self):
        """Cleanup when page is about to be unmounted"""
        print("SignInScreen: will_unmount called - cleaning up resources")
        
        # Cleanup widgets
        for widget in self.widgets_to_cleanup:
            if hasattr(widget, 'will_unmount'):
                try:
                    widget.will_unmount()
                except Exception as e:
                    print(f"Error cleaning up widget {widget}: {e}")
        
        # Clear the list
        self.widgets_to_cleanup.clear()
        
        # Cleanup animation (stops animation and removes listener)
        AnimationManager.cleanup()
        
        # Clean up MediaQuery
        MediaQuery.reset_all()
        
        print("SignInScreen: cleanup completed")
        
    def on_destroy(self):
        """Cleanup on page destroy"""
        print("SignInScreen: on_destroy called")

    def _on_error_changed(self):
        """Handle error message changes"""
        if self.signin_controller.signin_error.value:
            self.error_text.value = self.signin_controller.signin_error.value
            self.error_text.visible = True
        else:
            self.error_text.visible = False
        self.error_text.update()
    
    async def handle_signin(self, e):
        """Handle sign in button click"""
        print(f"Sign In clicked!")
        print(f"Email: {self.signin_controller.email.value}")
        print(f"Password: {self.signin_controller.password.value}")
        
        # Call the signin method from controller
        success, message, data = await self.signin_controller.signin()
        
        if success:
            print(f"Sign in successful! Message: {message}")
            print(f"User data: {data}")
            
            # Store the token (you might want to use a secure storage mechanism)
            if data and 'token' in data:
                # TODO: Store token securely
                print(f"Token received: {data['token']}")
            
            # Navigate to home or dashboard
            # safe_navigate("/home", current_page=self, replace=True, clear_history=True)
        else:
            print(f"Sign in failed: {message}")
            # Error is already set in the controller and will be displayed
        
    def go_to_forgot_password(self, e):
        """Handle forgot password"""
        print("Navigating to forgot password...")
        # Use safe_navigate to ensure cleanup happens
        safe_navigate("/forgot-password", current_page=self)

    def go_to_signup(self, e):
        """Navigate to signup screen"""
        print("Navigating to signup...")
        # Use safe_navigate to ensure cleanup happens
        safe_navigate("/signup", current_page=self)

    def build(self):
        email_field = input_field(
            "Enter your email address", 
            ft.Icons.ALTERNATE_EMAIL, 
            hide=False,
            rx_value=self.signin_controller.email
        )
        password_field = input_field(
            "Enter your password", 
            ft.Icons.LOCK_OUTLINE, 
            hide=True,
            rx_value=self.signin_controller.password
        )
        auth_controls = auth_action_controlls(
            primary_action_text="Sign Up",
            primary_action_on_click=self.go_to_signup,
            show_forgot_password=True,
            forgot_password_on_click=self.go_to_forgot_password
        )
        main_btn = main_auth_btn("Sign In", on_click=self.handle_signin)
        divider = auth_divider()
        
        self.widgets_to_cleanup.append(email_field)
        self.widgets_to_cleanup.append(password_field)
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
                                    "Sign In", 
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
                        # Email input field with reactive binding
                        email_field,
                        ft.Container(height=20),
                        # Password input field with reactive binding
                        password_field,
                        ft.Container(height=10),
                        # Error message display
                        self.error_text,
                        ft.Container(height=20),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                auth_controls
                            ]
                        ),
                        ft.Container(height=30),
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