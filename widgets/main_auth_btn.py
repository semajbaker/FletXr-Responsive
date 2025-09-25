import flet as ft
from utils.responsive_manager import MediaQuery

class ResponsiveMainAuthBtn(ft.Container):
    """Reactive main auth btn that automatically updates when breakpoints change."""
    def __init__(self, title: str):
        self.container_width_rx = MediaQuery.get_shared_container_width_rx()

        self.btn = ft.TextButton(
            title,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                text_style=ft.TextStyle(
                    size=18,
                    weight=ft.FontWeight.BOLD
                ),
                overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
            ),
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
        self.container_width_rx.listen(self._on_container_width_changed)
    
    def _on_container_width_changed(self):
        """Called when container width changes"""
        print(f"Main auth btn Container width changed to: {self.container_width_rx.value}")
        self.width = self.container_width_rx.value
        if hasattr(self, 'page') and self.page:
            self.update()
        

def main_auth_btn(title: str):
    return ResponsiveMainAuthBtn(title)