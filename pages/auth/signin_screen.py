import flet as ft
from fletx.core import FletXPage
from utils.animation_manager import animate_boxes
from widgets.animated_box import animated_box
from widgets.input_field import input_field
from controllers.animation_controller import AnimationController
from constants.ui_constants import AppColors

class SignInScreen(FletXPage):
    def __init__(self):
        super().__init__()
        self.main_content = None
        self.box1 = animated_box(ft.Colors.PINK_400, ft.Colors.PURPLE_300, 1.0)
        self.box2 = animated_box(ft.Colors.CYAN_400, ft.Colors.TEAL_300, 0.8)
        self.box3 = animated_box(ft.Colors.AMBER_400, ft.Colors.ORANGE_300, 1.2)
        self.box4 = animated_box(ft.Colors.GREEN_400, ft.Colors.LIGHT_GREEN_300, 0.9)
        self.animation_ctrl = AnimationController()

    def on_init(self):
        self.animation_value = self.animation_ctrl.start_animation()
        animate_boxes(self, self.box1, self.box2, self.box3, self.box4, self.animation_value)

    def build(self):
        return ft.Container(
            bgcolor=AppColors.LIGHT['background'],
            margin=ft.margin.all(0),
            alignment=ft.alignment.center,
            padding=ft.padding.all(20),
            content=ft.Card(
                width=500,
                height=750,
                elevation=8,
                surface_tint_color=AppColors.LIGHT['surface'],
                color=AppColors.LIGHT['background'],
                shadow_color=ft.Colors.with_opacity(0.15, AppColors.LIGHT['shadow']),
                content=ft.Column(
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                    controls=[
                        ft.Container(height=30),
                        ft.Container(
                            width=200,
                            height=120,
                            content=ft.Stack(
                                controls=[
                                    ft.Container(
                                        left=70,
                                        top=30,
                                        content=self.box1
                                    ),
                                    ft.Container(
                                        left=130,
                                        top=50,
                                        content=self.box2
                                    ),
                                    ft.Container(
                                        left=40,
                                        top=60,
                                        content=self.box3
                                    ),
                                    ft.Container(
                                        left=100,
                                        top=10,
                                        content=self.box4
                                    ),
                                ]
                            )
                        ),
                        ft.Container(height=25),
                         # Header section
                        ft.Column(
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=8,
                            controls=[
                                ft.Text(
                                    "Sign In", 
                                    size=32, 
                                    weight=ft.FontWeight.BOLD, 
                                    color=ft.Colors.BLUE_GREY_800
                                ),
                                ft.Text(
                                    "Python Flet(Flutter for Python) UI", 
                                    size=16,
                                    color=ft.Colors.BLUE_GREY_500,
                                    weight=ft.FontWeight.W_400
                                ),
                            ]
                        ),
                        ft.Container(height=25),

                        input_field("Enter your email address", ft.Icons.ALTERNATE_EMAIL, hide=False),

                        ft.Container(height=20),

                        input_field("Enter your password", ft.Icons.LOCK_OUTLINE, hide=True),

                        ft.Container(height=25),
                        ft.Container(
                            width=350,
                            content=ft.Row(
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                controls=[
                                    ft.TextButton(
                                        "Create Account",
                                        style=ft.ButtonStyle(
                                            color=ft.Colors.BLUE_GREY_400,
                                            overlay_color=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_400),
                                            text_style=ft.TextStyle(
                                                weight=ft.FontWeight.W_300,
                                                size=12
                                            ),
                                        ),
                                    ),
                                    ft.TextButton(
                                        "Forgot password?",
                                        style=ft.ButtonStyle(
                                            color=ft.Colors.BLUE_GREY_400,
                                            overlay_color=ft.Colors.with_opacity(0.2, ft.Colors.BLUE_GREY_400),
                                            text_style=ft.TextStyle(
                                                weight=ft.FontWeight.W_300,
                                                size=12
                                            ),
                                        ),
                                    ),
                                ]
                            ),
                        ),
                        ft.Container(height=20),
                        ft.Container(
                            width=350,
                            height=55,
                            bgcolor=ft.Colors.BLUE_600,
                            border_radius=15,
                            shadow=ft.BoxShadow(
                                spread_radius=1,
                                offset=ft.Offset(0, 4),
                                blur_radius=10,
                                color=ft.Colors.with_opacity(0.3, ft.Colors.BLUE_400),
                            ),
                            content=ft.TextButton(
                                "Sign In",
                                style=ft.ButtonStyle(
                                    color=ft.Colors.WHITE,
                                    text_style=ft.TextStyle(
                                        size=18,
                                        weight=ft.FontWeight.BOLD
                                    ),
                                    overlay_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE),
                                ),
                            ),
                        ),
                        ft.Container(height=25),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=10,
                            controls=[
                                ft.Container(
                                    width=100,
                                    height=1,
                                    bgcolor=ft.Colors.BLUE_GREY_200
                                ),
                                ft.Text(
                                    "Or continue with",
                                    size=14,
                                    color=ft.Colors.BLUE_GREY_400,
                                    weight=ft.FontWeight.W_500
                                ),
                                ft.Container(
                                    width=100,
                                    height=1,
                                    bgcolor=ft.Colors.BLUE_GREY_200
                                ),
                            ]
                        ),
                        ft.Container(height=25),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=15,
                            controls=[
                                ft.Container(
                                    width=100,
                                    height=50,
                                    content=ft.FloatingActionButton(
                                        content=ft.Icon(
                                            ft.Icons.EMAIL, 
                                            size=20, 
                                            color=ft.Colors.BLUE_GREY_400
                                        ),
                                        width=30,
                                        height=30,
                                        bgcolor=ft.Colors.WHITE,
                                        shape=ft.CircleBorder(),
                                        elevation=3,
                                        tooltip="Continue with Google",
                                    ),
                                ),
                                ft.Container(
                                    width=100,
                                    height=50,
                                    content=ft.FloatingActionButton(
                                        content=ft.Icon(
                                            ft.Icons.CODE, 
                                            size=20, 
                                            color=ft.Colors.BLUE_GREY_400
                                        ),
                                        width=30,
                                        height=30,
                                        bgcolor=ft.Colors.WHITE,
                                        shape=ft.CircleBorder(),
                                        elevation=3,
                                        tooltip="Continue with Github",
                                    ),
                                ),
                            ]
                        )
                    ]
                ),
            ),
        )