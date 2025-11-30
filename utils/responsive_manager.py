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
        controller = FletX.find(MediaQueryController, tag='media_query_controller')
        
        if controller is None:
            # If not found, create and register it
            controller = MediaQueryController()
            FletX.put(controller, tag='media_query_controller')
        
        return controller
    
    @classmethod
    def dispose_controller(cls):
        """Dispose the media query controller and clean up resources"""
        controller = FletX.find(MediaQueryController, tag='media_query_controller')
        
        if controller is not None:
            # Clean up the controller instance
            controller.cleanup()
            
            # Remove from FletX dependency injection
            try:
                from fletx.core.di import DI
                tag = 'media_query_controller'
                if MediaQueryController in DI._instances:
                    if tag in DI._instances[MediaQueryController]:
                        # Call dispose manually to trigger our custom disposal
                        if hasattr(controller, 'dispose'):
                            controller.dispose()
                        # Remove from DI
                        del DI._instances[MediaQueryController][tag]
                        print("MediaQueryController removed from DI")
            except Exception as e:
                print(f"Error removing controller from DI: {e}")
        
        return controller

    @classmethod
    def reset_all(cls):
        """Complete reset - dispose controller and reset shared state"""
        # First dispose the current controller
        cls.dispose_controller()
        
        # Then reset all shared state
        MediaQueryController.reset_shared_state()
        
        print("MediaQuery system completely reset")

    @classmethod
    def cleanup(cls):
        """Full cleanup including shared state reset"""
        cls.reset_all()
    
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
        """Get the reactive field width property"""
        controller = cls.get_controller()
        return controller.auth_divider_width
    
    @classmethod
    def get_auth_navigation_controls_width_rx(cls):
        """Get the reactive field width property"""
        controller = cls.get_controller()
        return controller.auth_navigation_controls_width
    
    @classmethod
    def initialize_with_page(cls, page: ft.Page):
        """Initialize the media query system with a page - call from page's on_init"""
        controller = cls.get_controller()
        controller.initialize_with_page(page)
    
    @classmethod
    def complete_registration(cls):
        """Call after all breakpoints and listeners are registered to start responsive checking"""
        controller = cls.get_controller()
        controller.complete_registration()
    
    @classmethod
    def debug_listener_count(cls):
        """Print current breakpoint listener counts for debugging"""
        controller = cls.get_controller()
        print("=== MediaQuery Listener Stats ===")
        total = controller.get_listener_count()
        print(f"Total listeners: {total}")
        print("=================================")

    @classmethod
    def debug_all_listeners(cls):
        """Print complete listener report including all reactive properties"""
        controller = cls.get_controller()
        return controller.get_all_listener_counts()

    @classmethod
    def debug_listener_details(cls):
        """Print detailed listener information with function names"""
        controller = cls.get_controller()
        controller.debug_listener_details()