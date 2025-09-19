import flet as ft

def input_field(hint_text, icon, hide):
    """Creates a modern glass-morphism style input field."""
    return ft.Container(
        width=350,
        height=55,
        bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_GREY_100),
        border_radius=15,
        border=ft.border.all(1.5, ft.Colors.with_opacity(0.3, ft.Colors.BLUE_400)),
        padding=ft.padding.symmetric(horizontal=15, vertical=8),
        content=ft.Row(
            spacing=15,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(
                    icon, 
                    color=ft.Colors.BLUE_600,
                    size=20,
                ),
                ft.TextField(
                    border_color="transparent",
                    bgcolor="transparent",  
                    hint_text=hint_text,
                    hint_style=ft.TextStyle(
                        size=14,
                        color=ft.Colors.BLUE_GREY_400
                    ),
                    height=40,
                    width=280,
                    text_size=14,
                    content_padding=0,
                    cursor_color=ft.Colors.BLUE_600,
                    password=hide,
                    can_reveal_password=hide,
                    text_style=ft.TextStyle(
                        color=ft.Colors.BLUE_GREY_800,
                        weight=ft.FontWeight.W_500
                    )
                )
            ]
        ),
    )