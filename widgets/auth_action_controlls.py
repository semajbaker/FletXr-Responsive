import flet as ft
from utils.responsive_manager import MediaQuery

class ResponsiveAuthActionControlls(ft.Container):
    def __init__(self, 
                 primary_action_text="Create Account",
                 primary_action_on_click=None,
                 show_forgot_password=True,
                 forgot_password_on_click=None):
        """
        Dynamic auth action controls
        
        Args:
            primary_action_text: Text for the primary action button (e.g., "Create Account" or "Sign In")
            primary_action_on_click: Callback function for primary button click
            show_forgot_password: Boolean to show/hide forgot password button
            forgot_password_on_click: Callback function for forgot password button click
        """
        self.container_width_rx = MediaQuery.get_shared_container_width_rx()
        self.show_forgot_password = show_forgot_password

        # Primary action button (left side)
        self.primary_action_btn = ft.TextButton(
            primary_action_text,
            on_click=primary_action_on_click,
            style=ft.ButtonStyle(
                color=ft.Colors.BLUE_GREY_400,
                overlay_color=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_400),
                text_style=ft.TextStyle(
                    weight=ft.FontWeight.W_300,
                    size=12
                ),
            ),
        )
        
        # Forgot password button (right side)
        self.forgot_password_btn = ft.TextButton(
            "Forgot password?",
            on_click=forgot_password_on_click,
            style=ft.ButtonStyle(
                color=ft.Colors.BLUE_GREY_400,
                overlay_color=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_400),
                text_style=ft.TextStyle(
                    weight=ft.FontWeight.W_300,
                    size=12
                ),
            ),
        )
        
        # Build controls list based on what should be shown
        controls = []
        
        if show_forgot_password:
            # Show both buttons with space between
            controls = [
                self.primary_action_btn,
                self.forgot_password_btn
            ]
            alignment = ft.MainAxisAlignment.SPACE_BETWEEN
        else:
            # Show only primary action button, aligned to start
            controls = [self.primary_action_btn]
            alignment = ft.MainAxisAlignment.START
        
        super().__init__(
            width=self.container_width_rx.value,
            content=ft.Row(
                alignment=alignment,
                controls=controls
            )
        )
        self.container_width_rx.listen(self._on_container_width_changed)

    def _on_container_width_changed(self):
        """Called when container width changes"""
        print(f"auth actions btn controls width changed to: {self.container_width_rx.value}")
        self.width = self.container_width_rx.value
        if hasattr(self, 'page') and self.page:
            self.update()

def auth_action_controlls(primary_action_text="Create Account",
                          primary_action_on_click=None,
                          show_forgot_password=True,
                          forgot_password_on_click=None):
    """
    Factory function for creating auth action controls
    
    Args:
        primary_action_text: Text for the primary action button
        primary_action_on_click: Callback function when primary button is clicked
        show_forgot_password: Whether to show forgot password button
        forgot_password_on_click: Callback function when forgot password button is clicked
    
    Returns:
        ResponsiveAuthActionControlls instance
        
    Example Usage:
        # In SignInScreen:
        def go_to_signup(self, e):
            from fletx.navigation import navigate
            navigate("/signup")
        
        auth_action_controlls(
            primary_action_text="Create Account",
            primary_action_on_click=self.go_to_signup,
            show_forgot_password=True,
        )
        
        # In SignUpScreen:
        def go_to_signin(self, e):
            from fletx.navigation import navigate
            navigate("/signin")
        
        auth_action_controlls(
            primary_action_text="Sign In",
            primary_action_on_click=self.go_to_signin,
            show_forgot_password=False
        )
    """
    return ResponsiveAuthActionControlls(
        primary_action_text=primary_action_text,
        primary_action_on_click=primary_action_on_click,
        show_forgot_password=show_forgot_password,
        forgot_password_on_click=forgot_password_on_click
    )