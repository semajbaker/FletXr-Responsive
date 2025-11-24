import flet as ft
from utils.responsive_manager import MediaQuery


class ResponsiveAuthActionControls(ft.Container):
    """Reactive auth action controls that automatically update when breakpoints change."""
    
    def __init__(
        self,
        primary_action_text: str,
        primary_action_on_click,
        show_forgot_password: bool = False,
        forgot_password_on_click = None
    ):
        # Store parameters
        self.primary_action_text = primary_action_text
        self.primary_action_on_click = primary_action_on_click
        self.show_forgot_password = show_forgot_password
        self.forgot_password_on_click = forgot_password_on_click
        
        # Get reactive property
        self.container_width_rx = MediaQuery.get_auth_navigation_controls_width_rx()
        
        # Determine the prefix text based on the action
        if primary_action_text.lower() == "sign in":
            self.prefix_text = "Already have an account? "
        elif primary_action_text.lower() == "forgot password":
            self.prefix_text = "Remember your password? "
        elif primary_action_text.lower() in ["sign up", "create account"]:
            self.prefix_text = "Don't have an account? "
        else:
            self.prefix_text = ""
        
        # ---- LEFT SIDE: Primary action (button + prefix) ----
        self.primary_section = ft.Container(
            content=ft.Row(
                spacing=2,
                tight=True,
                controls=[
                    ft.Text(
                        self.prefix_text,
                        size=12,
                        color=ft.Colors.BLUE_GREY_600,
                    ),
                    ft.TextButton(
                        text=primary_action_text,
                        on_click=primary_action_on_click,
                        style=ft.ButtonStyle(
                            color=ft.Colors.BLUE_600,
                            overlay_color=ft.Colors.BLUE_50,
                            padding=ft.padding.all(0),
                        ),
                    ),
                ]
            )
        )
        
        # ---- RIGHT SIDE: Forgot password or spacer ----
        if show_forgot_password and forgot_password_on_click:
            self.forgot_section = ft.Container(
                content=ft.TextButton(
                    text="Forgot Password?",
                    on_click=forgot_password_on_click,
                    style=ft.ButtonStyle(
                        color=ft.Colors.BLUE_600,
                        overlay_color=ft.Colors.BLUE_50,
                    ),
                )
            )
        else:
            self.forgot_section = ft.Container()
        
        # Create initial content layout
        self.content_layout = self._create_layout()
        
        # Initialize the container
        super().__init__(
            width=self.container_width_rx.value,
            padding=ft.padding.symmetric(horizontal=20),
            content=self.content_layout
        )
        
        # Set up listeners after initialization
        self.container_width_rx.listen(self._on_container_width_changed)
        
        # Register breakpoint listeners for layout changes
        MediaQuery.on('mobile', self._on_mobile_breakpoint)
        MediaQuery.on('tablet', self._on_desktop_breakpoint)
        MediaQuery.on('desktop', self._on_desktop_breakpoint)
    
    def _create_layout(self):
        """Create layout based on current breakpoint"""
        current_breakpoint = MediaQuery.get_current_breakpoint()
        print(f"Creating layout for breakpoint: {current_breakpoint}")
        
        if current_breakpoint == 'mobile':
            # Stack vertically on mobile
            return ft.Column(
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self.primary_section,
                    self.forgot_section
                ]
            )
        else:
            # Horizontal layout for tablet and desktop
            return ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    self.primary_section,   # LEFT
                    self.forgot_section     # RIGHT
                ]
            )
    
    def _on_mobile_breakpoint(self):
        """Called when mobile breakpoint becomes active"""
        print("Auth controls: Mobile breakpoint activated")
        self._update_layout()
    
    def _on_desktop_breakpoint(self):
        """Called when tablet/desktop breakpoint becomes active"""
        print("Auth controls: Desktop/Tablet breakpoint activated")
        self._update_layout()
    
    def _update_layout(self):
        """Update the layout based on current breakpoint"""
        new_layout = self._create_layout()
        self.content = new_layout
        if hasattr(self, 'page') and self.page:
            self.update()
    
    def _on_container_width_changed(self):
        """Called when container width changes"""
        print(f"Auth controls container width changed to: {self.container_width_rx.value}")
        self.width = self.container_width_rx.value
        if hasattr(self, 'page') and self.page:
            self.update()


def auth_action_controlls(
    primary_action_text: str,
    primary_action_on_click,
    show_forgot_password: bool = False,
    forgot_password_on_click = None
):
    """Factory function to create responsive auth action controls."""
    return ResponsiveAuthActionControls(
        primary_action_text,
        primary_action_on_click,
        show_forgot_password,
        forgot_password_on_click
    )