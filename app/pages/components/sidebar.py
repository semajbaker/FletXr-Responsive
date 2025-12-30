import flet as ft
from fletx.navigation import navigate

from app.constants.ui_constants import AppColors

def sidebar_item(icon: str, label: str, route: str, is_active: bool = False):
    """Create a sidebar menu item"""
    return ft.Container(
        content=ft.Row(
            controls=[
                ft.Icon(
                    icon,
                    size=22,
                    color=ft.Colors.WHITE if is_active else ft.Colors.BLUE_GREY_300
                ),
                ft.Text(
                    label,
                    size=14,
                    weight=ft.FontWeight.W_500 if is_active else ft.FontWeight.W_400,
                    color=ft.Colors.WHITE if is_active else ft.Colors.BLUE_GREY_300
                )
            ],
            spacing=15,
        ),
        padding=ft.padding.symmetric(horizontal=20, vertical=12),
        bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.WHITE) if is_active else ft.Colors.TRANSPARENT,
        border_radius=10,
        ink=True,
        on_click=lambda e: navigate(route),
    )

def sidebar(active_route: str = "/"):
    """
    Reusable sidebar widget for the dashboard
    
    Args:
        active_route: Current active route to highlight the corresponding menu item
    """
    
    menu_items = [
        {"icon": ft.Icons.DASHBOARD_OUTLINED, "label": "Dashboard", "route": "/"},
        {"icon": ft.Icons.SOLAR_POWER_OUTLINED, "label": "Solar Systems", "route": "/solar-systems"},
        {"icon": ft.Icons.ENERGY_SAVINGS_LEAF_OUTLINED, "label": "Energy Analytics", "route": "/energy-analytics"},
        {"icon": ft.Icons.PEOPLE_OUTLINE, "label": "Employees", "route": "/employees"},
        {"icon": ft.Icons.INVENTORY_2_OUTLINED, "label": "Inventory", "route": "/inventory"},
        {"icon": ft.Icons.ASSIGNMENT_OUTLINED, "label": "Projects", "route": "/projects"},
        {"icon": ft.Icons.ACCOUNT_CIRCLE_OUTLINED, "label": "Customers", "route": "/customers"},
        {"icon": ft.Icons.BAR_CHART_OUTLINED, "label": "Reports", "route": "/reports"},
    ]
    
    return ft.Container(
        width=260,
        bgcolor=ft.Colors.BLUE_GREY_900,
        padding=ft.padding.all(0),
        content=ft.Column(
            spacing=0,
            controls=[
                # Logo/Brand section
                ft.Container(
                    padding=ft.padding.all(20),
                    content=ft.Row(
                        controls=[
                            ft.Icon(
                                ft.Icons.SOLAR_POWER,
                                size=32,
                                color=ft.Colors.AMBER_400
                            ),
                            ft.Column(
                                spacing=0,
                                controls=[
                                    ft.Text(
                                        "SolarTech",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE
                                    ),
                                    ft.Text(
                                        "Management",
                                        size=11,
                                        color=ft.Colors.BLUE_GREY_300
                                    ),
                                ]
                            )
                        ],
                        spacing=12,
                    ),
                ),
                
                ft.Divider(height=1, color=ft.Colors.BLUE_GREY_800),
                
                # Menu items
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=15, vertical=20),
                    expand=True,
                    content=ft.Column(
                        spacing=5,
                        scroll=ft.ScrollMode.AUTO,
                        controls=[
                            sidebar_item(
                                icon=item["icon"],
                                label=item["label"],
                                route=item["route"],
                                is_active=item["route"] == active_route
                            )
                            for item in menu_items
                        ]
                    )
                ),
                
                ft.Divider(height=1, color=ft.Colors.BLUE_GREY_800),
                
                # User profile section
                ft.Container(
                    padding=ft.padding.all(20),
                    content=ft.Row(
                        controls=[
                            ft.CircleAvatar(
                                content=ft.Text("JD", color=ft.Colors.WHITE),
                                bgcolor=ft.Colors.AMBER_600,
                                radius=20,
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        "John Doe",
                                        size=13,
                                        weight=ft.FontWeight.W_500,
                                        color=ft.Colors.WHITE
                                    ),
                                    ft.Text(
                                        "Administrator",
                                        size=11,
                                        color=ft.Colors.BLUE_GREY_400
                                    ),
                                ]
                            ),
                            ft.IconButton(
                                icon=ft.Icons.LOGOUT,
                                icon_size=20,
                                icon_color=ft.Colors.BLUE_GREY_400,
                                tooltip="Logout",
                                on_click=lambda e: navigate("/signin")
                            )
                        ],
                        spacing=10,
                    ),
                ),
            ]
        )
    )