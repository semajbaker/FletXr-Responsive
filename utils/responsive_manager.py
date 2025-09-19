"""
Modified responsive system for FletXr applications using proper lifecycle methods.

File: utils/responsive_manager.py
"""
import flet as ft
from fletx import FletX
from typing import Callable
from controllers.responsive_controller import MediaQueryController

class MediaQuery:
    """
    Static utility class for easier access to media query functionality.
    Uses FletX dependency injection system.
    """
    
    @classmethod
    def get_controller(cls) -> MediaQueryController:
        """Get the media query controller from FletX dependency injection"""
        try:
            return FletX.find('media_query_controller')
        except:
            # If not found, create and register it
            controller = MediaQueryController()
            FletX.put(controller, 'media_query_controller')
            return controller
    
    @classmethod
    def register(cls, point: str, min_width: int, max_width: int):
        """Register a breakpoint"""
        controller = cls.get_controller()
        controller.register(point, min_width, max_width)
    
    @classmethod
    def on(cls, point: str, callback_function: Callable):
        """Register a callback for a breakpoint"""
        controller = cls.get_controller()
        controller.on(point, callback_function)
    
    @classmethod
    def off(cls, point: str, callback_function: Callable):
        """Remove a callback for a breakpoint"""
        controller = cls.get_controller()
        controller.off(point, callback_function)
    
    @classmethod
    def get_current_breakpoint(cls) -> str:
        """Get the current active breakpoint"""
        controller = cls.get_controller()
        return controller.current_breakpoint.value
    
    @classmethod
    def get_current_width(cls) -> int:
        """Get the current window width"""
        controller = cls.get_controller()
        return controller.window_width.value
    
    @classmethod
    def initialize_with_page(cls, page: ft.Page):
        """Initialize the media query system with a page - call from page's on_init"""
        controller = cls.get_controller()
        controller.initialize_with_page(page)