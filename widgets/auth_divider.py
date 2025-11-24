import flet as ft
from utils.responsive_manager import MediaQuery


class ResponsiveAuthDivider(ft.Row):
    """Reactive auth divider that automatically updates when breakpoints change."""
    
    def __init__(self):
        # Get reactive property
        self.auth_divider_width_rx = MediaQuery.get_auth_divider_width_rx()
        
        # Create separate containers for left and right lines
        self.left_container = ft.Container(
            width=self.auth_divider_width_rx.value,
            height=1,
            bgcolor=ft.Colors.BLUE_GREY_200
        )
        
        self.right_container = ft.Container(
            width=self.auth_divider_width_rx.value,
            height=1,
            bgcolor=ft.Colors.BLUE_GREY_200
        )
        
        # Initialize the row
        super().__init__(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            controls=[
                self.left_container,
                ft.Text(
                    "Or continue with",
                    size=14,
                    color=ft.Colors.BLUE_GREY_400,
                    weight=ft.FontWeight.W_500
                ),
                self.right_container,
            ]
        )
        
        # Set up listener after initialization
        self.auth_divider_width_rx.listen(self._on_container_width_changed)
    
    def _on_container_width_changed(self):
        """Called when container width changes"""
        print(f"Auth divider width changed to: {self.auth_divider_width_rx.value}")
        
        # Update both containers
        self.left_container.width = self.auth_divider_width_rx.value
        self.right_container.width = self.auth_divider_width_rx.value
        
        if hasattr(self, 'page') and self.page:
            self.update()


def auth_divider():
    """Factory function to create a responsive auth divider."""
    return ResponsiveAuthDivider()