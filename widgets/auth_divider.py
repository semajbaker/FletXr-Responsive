import flet as ft
from utils.responsive_manager import MediaQuery

class ResponsiveAuthDivider(ft.Row):
    def __init__(self):
        self.auth_divider_wdth_rx = MediaQuery.get_auth_divider_width_rx()

        self.container = ft.Container(
            width=self.auth_divider_wdth_rx,
            height=1,
            bgcolor=ft.Colors.BLUE_GREY_200
        )
        super().__init__(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
            controls=[
                self.container,
                ft.Text(
                    "Or continue with",
                    size=14,
                    color=ft.Colors.BLUE_GREY_400,
                    weight=ft.FontWeight.W_500
                ),
                self.container,
            ]
        )
        self.auth_divider_wdth_rx.listen(self._on_container_width_changed)

    def _on_container_width_changed(self):
        """Called when container width changes"""
        print(f"auth divider width changed to: {self.auth_divider_wdth_rx.value}")
        self.container.width = self.auth_divider_wdth_rx.value
        if hasattr(self, 'page') and self.page:
            self.update()

def auth_divider():
    return ResponsiveAuthDivider()