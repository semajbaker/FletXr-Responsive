import flet as ft
from utils.responsive_manager import MediaQuery

class ResponsiveMainAuthBtn(ft.Container):
    """Reactive main auth btn that automatically updates when breakpoints change."""
    
    def __init__(self, title: str, on_click=None):
        self.container_width_rx = MediaQuery.get_shared_container_width_rx()
        
        # CRITICAL: Store observer reference for cleanup
        self._container_width_observer = None

        self.btn = ft.TextButton(
            title,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                text_style=ft.TextStyle(size=18, weight=ft.FontWeight.BOLD),
                overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            ),
            on_click=on_click
        )
        
        super().__init__(
            width=self.container_width_rx.value,
            height=55,
            bgcolor=ft.Colors.BLUE_600,
            border_radius=15,
            shadow=ft.BoxShadow(
                spread_radius=1,
                offset=ft.Offset(0, 4),
                blur_radius=10,
                color=ft.Colors.with_opacity(0.3, ft.Colors.BLUE_400),
            ),
            content=self.btn
        )
        
        # Store observer reference
        self._container_width_observer = self.container_width_rx.listen(self._on_container_width_changed)
    
    def will_unmount(self):
        """Clean up listeners when widget is unmounted"""
        try:
            # Dispose observer properly
            if self._container_width_observer:
                self._container_width_observer.dispose()
                self._container_width_observer = None
            print(f"ResponsiveMainAuthBtn cleaned up")
        except Exception as e:
            print(f"Error cleaning up ResponsiveMainAuthBtn: {e}")
    
    def _on_container_width_changed(self):
        print(f"Main auth btn Container width changed to: {self.container_width_rx.value}")
        self.width = self.container_width_rx.value
        if hasattr(self, 'page') and self.page:
            self.update()


def main_auth_btn(title: str, on_click=None):
    return ResponsiveMainAuthBtn(title, on_click)