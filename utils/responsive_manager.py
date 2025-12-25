"""
Modified responsive system for FletXr applications.
File: utils/responsive_manager.py
"""
import flet as ft
from fletx import FletX
from typing import Callable
from controllers.responsive_controller import MediaQueryController

class MediaQuery:
    """
    Static utility class for easier access to media query functionality.
    """
    
    @classmethod
    def get_controller(cls) -> MediaQueryController:
        """Get the media query controller from FletX dependency injection"""
        controller: MediaQueryController = FletX.find(MediaQueryController, tag='media_query_ctrl')
        
        if controller is None:
            raise RuntimeError("MediaQueryController not found! Make sure it's initialized.")
        
        return controller
    
    @classmethod
    def handle_page_resize(cls, width: int, height: int):
        """
        Called from FletXPage's set_size method to handle resize.
        This integrates with the MediaQuery system.
        """
        controller = cls.get_controller()
        controller.handle_resize(width, height)
    
    @classmethod
    def reset_all(cls):
        """Navigation cleanup - clear page-specific listeners only"""
        MediaQueryController.reset_shared_state()
        print("MediaQuery reset for navigation")
        
    @classmethod
    def cleanup(cls):
        """Alias for reset_all - used during navigation"""
        cls.reset_all()

    @classmethod
    def shutdown(cls):
        """Complete shutdown - use only when app is closing"""
        MediaQueryController.complete_shutdown()
        print("MediaQuery completely shut down")
    
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
    def get_current_height(cls) -> int:
        """Get the current window height"""
        controller = cls.get_controller()
        return controller.window_height.value
    
    @classmethod
    def get_shared_container_width_rx(cls):
        """Get the reactive container width property"""
        controller = cls.get_controller()
        return controller.shared_container_width
    
    @classmethod
    def get_text_field_width_rx(cls):
        """Get the reactive field width property"""
        controller = cls.get_controller()
        return controller.shared_text_field_width

    @classmethod
    def get_auth_divider_width_rx(cls):
        """Get the reactive divider width property"""
        controller = cls.get_controller()
        return controller.auth_divider_width
    
    @classmethod
    def get_auth_navigation_controls_width_rx(cls):
        """Get the reactive navigation controls width property"""
        controller = cls.get_controller()
        return controller.auth_navigation_controls_width
    
    @classmethod
    def initialize_with_page(cls, page: ft.Page):
        """Initialize the media query system with a page"""
        controller = cls.get_controller()
        controller.initialize_with_page(page)
    
    @classmethod
    def complete_registration(cls):
        """Call after all breakpoints are registered"""
        controller = cls.get_controller()
        controller.complete_registration()
    
    @classmethod
    def debug_listener_count(cls):
        """Print current breakpoint listener counts"""
        controller = cls.get_controller()
        print("=== MediaQuery Listener Stats ===")
        total = controller.get_listener_count()
        print(f"Total listeners: {total}")
        print("=================================")

    @classmethod
    def debug_all_listeners(cls):
        """Print complete listener report"""
        controller = cls.get_controller()
        return controller.get_all_listener_counts()