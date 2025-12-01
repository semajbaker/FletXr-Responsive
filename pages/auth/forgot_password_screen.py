import flet as ft
from fletx.core import FletXPage
from utils.navigation_helper import safe_navigate
from utils.animation_manager import AnimationManager
from constants.ui_constants import AppColors
from widgets.animated_box import animated_box
from widgets.input_field import input_field
from widgets.main_auth_btn import main_auth_btn
from widgets.auth_action_controlls import auth_action_controlls
from controllers.auth_controller import ForgotPasswordController
from utils.responsive_manager import MediaQuery

class ForgotPasswordScreen(FletXPage):
    def __init__(self):
        super().__init__()
        self.box1 = animated_box(ft.Colors.PINK_400, ft.Colors.PURPLE_300, 1.0)
        self.box2 = animated_box(ft.Colors.CYAN_400, ft.Colors.TEAL_300, 0.8)
        self.box3 = animated_box(ft.Colors.AMBER_400, ft.Colors.ORANGE_300, 1.2)
        self.box4 = animated_box(ft.Colors.GREEN_400, ft.Colors.LIGHT_GREEN_300, 0.9)
        self.widgets_to_cleanup = []
        
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
        print("ForgotPasswordScreen: on_init called")
        
        # Initialize AnimationManager with page reference (static class)
        AnimationManager.initialize_with_page(self.page)
        
        # Set the boxes to animate
        AnimationManager.set_boxes(self.box1, self.box2, self.box3, self.box4)
        
        # Start animation
        AnimationManager.start_animation()
        MediaQuery.update_page_reference(self.page)
        MediaQuery.debug_all_listeners()
        # Set up listeners for error and success messages
        self.forgot_password_controller.error.listen(self._on_error_changed)
        self.forgot_password_controller.success.listen(self._on_success_changed)
        
    def will_unmount(self):
        """Cleanup when page is about to be unmounted"""
        print("ForgotPasswordScreen: will_unmount called - cleaning up resources")
        
        # Clean up all widgets
        for widget in self.widgets_to_cleanup:
            if hasattr(widget, 'will_unmount'):
                try:
                    widget.will_unmount()
                except Exception as e:
                    print(f"Error cleaning up widget {widget}: {e}")
        
        # Clear the list
        self.widgets_to_cleanup.clear()
        
        # Stop animation using static class method
        AnimationManager.stop_animation()
        
        # Clean up MediaQuery
        MediaQuery.reset_all()
        
        print("ForgotPasswordScreen: cleanup completed")
    
    def on_destroy(self):
        """Cleanup on page destroy"""
        print("ForgotPasswordScreen: on_destroy called")
        
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

    def go_to_signin(self, e):
        """Navigate to signin screen"""
        print("Navigating to signin...")
        # Use safe_navigate to ensure cleanup happens
        safe_navigate("/signin", current_page=self)

    def build(self):
        # Clear any previous widgets
        self.widgets_to_cleanup.clear()
        
        # Create widgets
        email_field = input_field(
            "Enter your email address", 
            ft.Icons.ALTERNATE_EMAIL, 
            hide=False,
            rx_value=self.forgot_password_controller.email
        )
        
        auth_controls = auth_action_controlls(
            primary_action_text="Sign In",
            primary_action_on_click=self.go_to_signin,
            show_forgot_password=False,
        )
        
        main_btn = main_auth_btn(
            "Send Reset Link", 
            on_click=self.handle_send_reset_link
        )
        
        # Store widget references for cleanup
        self.widgets_to_cleanup.append(email_field)
        self.widgets_to_cleanup.append(auth_controls)
        self.widgets_to_cleanup.append(main_btn)
        
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
                        email_field,
                        ft.Container(height=15),
                        # Error message display
                        self.error_text,
                        # Success message display
                        self.success_text,
                        ft.Container(height=25),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                auth_controls
                            ]
                        ),
                        ft.Container(height=30),
                        main_btn,
                        ft.Container(height=25),
                    ]
                ),
            ),
        )