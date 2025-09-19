import flet as ft
    
def animated_box(primary_color, secondary_color, initial_scale):
    return ft.Container(
        width=60,
        height=60,
        bgcolor=primary_color,
        border_radius=30,
        border=ft.border.all(3, secondary_color),
        scale=ft.Scale(initial_scale),
        rotate=0,
        animate_scale=600,
        animate_rotation=800,
        animate_opacity=400,
        opacity=0.9,
        shadow=ft.BoxShadow(
            spread_radius=2,
            blur_radius=15,
            color=ft.Colors.with_opacity(0.3, primary_color),
            offset=ft.Offset(0, 5)
        ),
    )