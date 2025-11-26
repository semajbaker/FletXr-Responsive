import flet as ft
from fletx.core import FletXPage
from fletx.navigation import navigate
from controllers.animation_controller import AnimationController
from controllers.auth_controller import ForgotPasswordController
from utils.animation_manager import AnimationManager
from constants.ui_constants import AppColors
from widgets.animated_box import animated_box
from widgets.input_field import input_field
from widgets.main_auth_btn import main_auth_btn
from widgets.auth_action_controlls import auth_action_controlls

class ForgotPasswordScreen(FletXPage):
    def __init__(self):
        super().__init__()
        self.box1 = animated_box(ft.Colors.PINK_400, ft.Colors.PURPLE_300, 1.0)
        self.box2 = animated_box(ft.Colors.CYAN_400, ft.Colors.TEAL_300, 0.8)
        self.box3 = animated_box(ft.Colors.AMBER_400, ft.Colors.ORANGE_300, 1.2)
        self.box4 = animated_box(ft.Colors.GREEN_400, ft.Colors.LIGHT_GREEN_300, 0.9)
        self.animation_ctrl = AnimationController()
        self.animation_manager = None
        
        # Initialize ForgotPasswordController
        self.forgot_password_controller = ForgotPasswordController()
        
        # Create error text that will update reactively
        self.error_text = ft.Text(
            value="",
            size=12,
            color=ft.Colors.RED_400,
            text_align=ft.TextAlign.CENTER,
            visible=False
        )
        
        # Create success text that will update reactively
        self.success_text = ft.Text(
            value="",
            size=12,
            color=ft.Colors.GREEN_600,
            text_align=ft.TextAlign.CENTER,
            visible=False,
            weight=ft.FontWeight.W_500
        )

    def on_init(self):
        """Initialize animation and controller after page is ready"""
        # Create animation manager with page reference and controller
        self.animation_manager = AnimationManager(self.page, self.animation_ctrl)
        
        # Set the boxes to animate
        self.animation_manager.set_boxes(self.box1, self.box2, self.box3, self.box4)
        
        # Start animation using controller
        self.animation_ctrl.start_animation()
        
        # Set up listeners for error and success messages
        self.forgot_password_controller.error.listen(self._on_error_changed)
        self.forgot_password_controller.success.listen(self._on_success_changed)
    
    def _on_error_changed(self):
        """Handle error message changes"""
        if self.forgot_password_controller.error.value:
            self.error_text.value = self.forgot_password_controller.error.value
            self.error_text.visible = True
            self.success_text.visible = False
        else:
            self.error_text.visible = False
        self.error_text.update()
    
    def _on_success_changed(self):
        """Handle success message changes"""
        if self.forgot_password_controller.success.value:
            self.success_text.value = self.forgot_password_controller.success.value
            self.success_text.visible = True
            self.error_text.visible = False
        else:
            self.success_text.visible = False
        self.success_text.update()
    
    def handle_send_reset_link(self, e):
        """Handle send reset link button click"""
        print(f"Send Reset Link clicked!")
        print(f"Email: {self.forgot_password_controller.email.value}")
        print(f"is_valid: {self.forgot_password_controller.is_valid.value}")
        
        # Force validation before sending
        self.forgot_password_controller.validate_form()
        
        print(f"After validation - is_valid: {self.forgot_password_controller.is_valid.value}")
        
        if self.forgot_password_controller.is_valid.value:
            success = self.forgot_password_controller.send_reset_link()
            if success:
                print("Reset link sent successfully!")
                # Optionally navigate back to signin after a delay
                # You can implement a timer here if needed
        else:
            print(f"Form validation failed. Error: {self.forgot_password_controller.error.value}")
    
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
                                    "Password Reset", 
                                    size=32, 
                                    weight=ft.FontWeight.BOLD, 
                                    color=ft.Colors.BLUE_GREY_800
                                ),
                                ft.Text(
                                    "Enter your email to receive a reset link", 
                                    size=14,
                                    color=ft.Colors.BLUE_GREY_500,
                                    weight=ft.FontWeight.W_400,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ]
                        ),
                        ft.Container(height=30),
                        # Email input field with reactive binding
                        input_field(
                            "Enter your email address", 
                            ft.Icons.ALTERNATE_EMAIL, 
                            hide=False,
                            rx_value=self.forgot_password_controller.email
                        ),
                        ft.Container(height=15),
                        # Error message display
                        self.error_text,
                        # Success message display
                        self.success_text,
                        ft.Container(height=25),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                auth_action_controlls(
                                    primary_action_text="Sign In",
                                    primary_action_on_click=self.go_to_signin,
                                    show_forgot_password=False,
                                )
                            ]
                        ),
                        ft.Container(height=30),
                        main_auth_btn(
                            "Send Reset Link", 
                            on_click=self.handle_send_reset_link
                        ),
                        ft.Container(height=25),
                    ]
                ),
            ),
        )