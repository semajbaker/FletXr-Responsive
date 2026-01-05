import flet as ft
from fletx import FletX
from fletx.core import FletXPage
from fletx.navigation import navigate

from app.utils.animation_manager import AnimationManager
from app.widgets.animated_box import animated_box
from app.widgets.input_field import input_field
from app.widgets.main_auth_btn import main_auth_btn
from app.widgets.auth_action_controls import auth_action_controlls
from app.constants.ui_constants import AppColors
from app.controllers.auth_controller import ForgotPasswordController
from app.utils.responsive_manager import MediaQuery

class ForgotPasswordScreen(FletXPage):
    def __init__(self):
        super().__init__(
            padding = ft.padding.only(left=0, right=0, top=0, bottom=0),
            # You can use `ft.Colors` to access theme colors 
            # Eg. bgcolor = Colors.SURFACE
        )
        self.box1 = animated_box(ft.Colors.PINK_400, ft.Colors.PURPLE_300, 1.0)
        self.box2 = animated_box(ft.Colors.CYAN_400, ft.Colors.TEAL_300, 0.8)
        self.box3 = animated_box(ft.Colors.AMBER_400, ft.Colors.ORANGE_300, 1.2)
        self.box4 = animated_box(ft.Colors.GREEN_400, ft.Colors.LIGHT_GREEN_300, 0.9)
        self.widgets_to_cleanup = []
        self.forgot_password_controller: ForgotPasswordController = FletX.find(
            ForgotPasswordController, tag='forgot_password_ctrl'
        )
    
    def on_init(self):
        # Initialize MediaQuery with page
        MediaQuery.initialize_with_page(self.page_instance)
        MediaQuery.debug_all_listeners()
        AnimationManager.initialize_with_page(self.page_instance)
        # Set the boxes to animate
        AnimationManager.set_boxes(self.box1, self.box2, self.box3, self.box4)
        # Start animation
        AnimationManager.start_animation()
        # Set up resize handler that works with both systems
        self.page_instance.on_resized = lambda e: self.handle_resize(e)
        
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
        print("Forgot Password Screen destroyed")

        
    def handle_resize(self, event: ft.ControlEvent):
         """Combined resize handler for both FletXPage and MediaQuery"""
         print(f'Resizing to {event.width}x{event.height}...')
        
         # Update FletXPage dimensions
         self.width = event.width
         self.height = event.height
        
         # Update MediaQuery system
         MediaQuery.handle_page_resize(event.width, event.height)
        
         # Refresh the page
         self.refresh()

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

    def goto_signin(self, e):
        self.will_unmount()
        navigate("/signin")

    def build(self):
        # Create widgets
        email_field = input_field(
            "Enter your email address", 
            ft.Icons.ALTERNATE_EMAIL, 
            hide=False,
            rx_value=self.forgot_password_controller.email
        )
        
        auth_controls = auth_action_controlls(
            primary_action_text="Sign In",
            primary_action_on_click=self.goto_signin,
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