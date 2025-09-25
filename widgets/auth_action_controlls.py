import flet as ft
from utils.responsive_manager import MediaQuery

class ResponsiveAuthActionControlls(ft.Container):
    def __init__(self):
        self.container_width_rx = MediaQuery.get_shared_container_width_rx()

        self.create_account_btn = ft.TextButton(
            "Create Account",
            style=ft.ButtonStyle(
                color=ft.Colors.BLUE_GREY_400,
                overlay_color=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_400),
                text_style=ft.TextStyle(
                    weight=ft.FontWeight.W_300,
                    size=12
                ),
            ),
        )
        self.forgot_password_btn = ft.TextButton(
            "Forgot password?",
            style=ft.ButtonStyle(
                color=ft.Colors.BLUE_GREY_400,
                overlay_color=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_400),
                text_style=ft.TextStyle(
                    weight=ft.FontWeight.W_300,
                    size=12
                ),
            ),
        )
        super().__init__(
            width=self.container_width_rx.value,
            content=ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    self.create_account_btn,
                    self.forgot_password_btn
                ]
            )
        )
        self.container_width_rx.listen(self._on_container_width_changed)

    def _on_container_width_changed(self):
        """Called when container width changes"""
        print(f"auth actions btn controlls width changed to: {self.container_width_rx.value}")
        self.width = self.container_width_rx.value
        if hasattr(self, 'page') and self.page:
            self.update()

def auth_action_controlls():
    return ResponsiveAuthActionControlls()