import flet as ft
from utils.responsive_manager import MediaQuery

class ResponsiveAuthDivider(ft.Row):
    """Reactive auth divider that automatically updates when breakpoints change."""
    
    def __init__(self):
        self.auth_divider_width_rx = MediaQuery.get_auth_divider_width_rx()
        
        # CRITICAL: Store observer reference for cleanup
        self._divider_width_observer = None
        
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
        
        super().__init__(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            controls=[
                self.left_container,
                ft.Text("Or continue with", size=14, color=ft.Colors.BLUE_GREY_400, weight=ft.FontWeight.W_500),
                self.right_container,
            ]
        )
        
        # Store observer reference
        self._divider_width_observer = self.auth_divider_width_rx.listen(self._on_container_width_changed)
    
    def will_unmount(self):
        """Clean up listeners when widget is unmounted"""
        try:
            # Dispose observer properly
            if self._divider_width_observer:
                self._divider_width_observer.dispose()
                self._divider_width_observer = None
            print(f"ResponsiveAuthDivider cleaned up")
        except Exception as e:
            print(f"Error cleaning up ResponsiveAuthDivider: {e}")
    
    def _on_container_width_changed(self):
        print(f"Auth divider width changed to: {self.auth_divider_width_rx.value}")
        self.left_container.width = self.auth_divider_width_rx.value
        self.right_container.width = self.auth_divider_width_rx.value
        if hasattr(self, 'page') and self.page:
            self.update()


def auth_divider():
    return ResponsiveAuthDivider()