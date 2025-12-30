import flet as ft

class AppColors:
    """Centralized color definitions for the application"""
    
    # Light theme colors
    LIGHT = {
        'primary': ft.Colors.BLUE_600,
        'primary_container': ft.Colors.BLUE_100,
        'secondary': ft.Colors.GREY_600,
        'secondary_container': ft.Colors.GREY_100,
        'surface': ft.Colors.WHITE,
        'surface_variant': ft.Colors.GREY_50,
        'background': ft.Colors.WHITE,
        'error': ft.Colors.RED_600,
        'on_primary': ft.Colors.WHITE,
        'on_secondary': ft.Colors.WHITE,
        'on_surface': ft.Colors.BLACK,
        'on_background': ft.Colors.BLACK,
        'on_error': ft.Colors.WHITE,
        'outline': ft.Colors.GREY_300,
        'shadow': ft.Colors.BLACK26,
    }
    
    # Dark theme colors  
    DARK = {
        'primary': ft.Colors.BLUE_400,
        'primary_container': ft.Colors.BLUE_900,
        'secondary': ft.Colors.GREY_400,
        'secondary_container': ft.Colors.GREY_800,
        'surface': ft.Colors.GREY_900,
        'surface_variant': ft.Colors.GREY_800,
        'background': ft.Colors.BLACK,
        'error': ft.Colors.RED_400,
        'on_primary': ft.Colors.BLACK,
        'on_secondary': ft.Colors.BLACK,
        'on_surface': ft.Colors.WHITE,
        'on_background': ft.Colors.WHITE,
        'on_error': ft.Colors.BLACK,
        'outline': ft.Colors.GREY_600,
        'shadow': ft.Colors.WHITE24,
    }