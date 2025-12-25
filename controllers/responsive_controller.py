import flet as ft
from typing import Callable
from fletx import FletX
from fletx.core import FletXController, RxStr, RxInt, RxDict, RxList
from constants.responsive_constants import *

class MediaQueryController(FletXController):
    """
    Reactive media query controller for FletXr applications.
    Uses FletXr's proper lifecycle and dependency injection.
    """
    
    # Class-level shared data to prevent multiple instance issues
    _shared_breakpoints = RxDict({})
    _shared_listeners = RxDict({})
    _shared_initialized = False
    _shared_width = RxInt(1912)
    _shared_height = RxInt(810)
    _shared_current_breakpoint = RxStr("desktop")
    _shared_registration_complete = False
    _shared_page = None
    
    # Add reactive properties for UI dimensions
    _shared_container_width = RxInt(SharedContainerSizes.DESKTOP_WIDTH)
    _shared_text_field_width = RxInt(InputFieldSizes.DESKTOP_WIDTH)
    _auth_divider_width = RxInt(AuthDividerSizes.DESKTOP_WIDTH)
    _auth_navigation_controls_width = RxInt(AuthNavigationControlSizes.DESKTOP_WIDTH)
    
    def __init__(self):
        super().__init__()
        
        # Use shared class-level reactive state
        self.window_width = MediaQueryController._shared_width
        self.window_height = MediaQueryController._shared_height
        self.current_breakpoint = MediaQueryController._shared_current_breakpoint
        self._breakpoints = MediaQueryController._shared_breakpoints
        self._listeners = MediaQueryController._shared_listeners
        
        # Reactive UI dimensions
        self.shared_container_width = MediaQueryController._shared_container_width
        self.shared_text_field_width = MediaQueryController._shared_text_field_width
        self.auth_divider_width = MediaQueryController._auth_divider_width
        self.auth_navigation_controls_width = MediaQueryController._auth_navigation_controls_width
        
        # Set up listeners only once
        if not hasattr(MediaQueryController, '_listeners_initialized'):
            self.window_width.listen(self._on_width_changed)
            MediaQueryController._listeners_initialized = True
    
    @property
    def _initialized(self):
        return MediaQueryController._shared_initialized
    
    @_initialized.setter
    def _initialized(self, value):
        MediaQueryController._shared_initialized = value
    
    @property
    def _registration_complete(self):
        return MediaQueryController._shared_registration_complete
    
    @_registration_complete.setter
    def _registration_complete(self, value):
        MediaQueryController._shared_registration_complete = value

    @property
    def _page(self):
        return MediaQueryController._shared_page
    
    @_page.setter
    def _page(self, value):
        MediaQueryController._shared_page = value

    def initialize_with_page(self, page: ft.Page):
        """Initialize with page reference - called from page's on_init"""
        # Store page reference
        self._page = page
        
        # Set initial dimensions if available
        if hasattr(page, 'width') and page.width:
            self.window_width.value = page.width
            print(f"MediaQuery initialized with page width: {page.width}")
        
        if hasattr(page, 'height') and page.height:
            self.window_height.value = page.height
            print(f"MediaQuery initialized with page height: {page.height}")
        
        # Mark as initialized
        self._initialized = True
        print(f"MediaQuery page initialization complete")
    
    def handle_resize(self, width: int, height: int):
        """Handle resize events - called from FletXPage's set_size method"""
        print(f"MediaQuery handling resize: {width}x{height}")
        self.window_width.value = width
        self.window_height.value = height
    
    def complete_registration(self):
        """Call this after all breakpoints are registered to trigger initial check"""
        self._registration_complete = True
        if self._initialized:
            self._check_for_updates(self.window_width.value)
    
    def _on_width_changed(self):
        """React to width changes and update current breakpoint"""
        if self._registration_complete and self._initialized:
            self._check_for_updates(self.window_width.value)
    
    def _update_ui_dimensions(self, breakpoint: str):
        """Update UI dimensions based on current breakpoint"""
        if breakpoint == 'mobile':
            self.shared_container_width.value = SharedContainerSizes.MOBILE_WIDTH
            self.shared_text_field_width.value = InputFieldSizes.MOBILE_WIDTH
            self.auth_divider_width.value = AuthDividerSizes.MOBILE_WIDTH
            self.auth_navigation_controls_width.value = AuthNavigationControlSizes.MOBILE_WIDTH
        else:  # tablet and desktop
            self.shared_container_width.value = SharedContainerSizes.DESKTOP_WIDTH
            self.shared_text_field_width.value = InputFieldSizes.DESKTOP_WIDTH
            self.auth_divider_width.value = AuthDividerSizes.DESKTOP_WIDTH
            self.auth_navigation_controls_width.value = AuthNavigationControlSizes.DESKTOP_WIDTH
    
    def _check_for_updates(self, width: int):
        """Check if breakpoint should change based on current width"""
        if not self._registration_complete:
            return
            
        print(f"Checking width: {width}")
        
        for name, (min_width, max_width) in self._breakpoints.value.items():
            if min_width < width <= max_width:
                if self.current_breakpoint.value != name:
                    old_breakpoint = self.current_breakpoint.value
                    self.current_breakpoint.value = name
                    print(f"Breakpoint changed from '{old_breakpoint}' to '{name}'")
                    
                    # Update UI dimensions when breakpoint changes
                    self._update_ui_dimensions(name)
                    
                    # Trigger listeners for the new breakpoint
                    if name in self._listeners.value:
                        listener_list = self._listeners.value[name]
                        print(f"Found {len(listener_list.value)} listeners for '{name}'")
                        for func in listener_list.value:
                            try:
                                func()
                            except Exception as e:
                                print(f"Error in breakpoint listener: {e}")
                else:
                    # Even if breakpoint hasn't changed, ensure dimensions are correct
                    self._update_ui_dimensions(name)
                return
    
    def register(self, point: str, min_width: int, max_width: int):
        """Register a breakpoint with min/max width values"""
        current_breakpoints = self._breakpoints.value.copy()
        current_breakpoints[point] = (min_width, max_width)
        self._breakpoints.value = current_breakpoints
        
        current_listeners = self._listeners.value.copy()
        if point not in current_listeners:
            current_listeners[point] = RxList([])
            self._listeners.value = current_listeners
    
    def on(self, point: str, callback_function: Callable):
        """Register a callback for when a breakpoint becomes active"""
        current_listeners = self._listeners.value.copy()
        if point not in current_listeners:
            current_listeners[point] = RxList([])
        
        # Add callback to RxList
        listener_list = current_listeners[point]
        new_list = listener_list.value.copy() if hasattr(listener_list, 'value') else listener_list.copy()
        new_list.append(callback_function)
        current_listeners[point] = RxList(new_list)
        self._listeners.value = current_listeners
        
        # If this breakpoint is currently active, call the callback immediately
        if self.current_breakpoint.value == point and self._initialized and self._registration_complete:
            try:
                callback_function()
            except Exception as e:
                print(f"Error in immediate breakpoint callback: {e}")
    
    def off(self, point: str, callback_function: Callable):
        """Remove a callback for a breakpoint"""
        current_listeners = self._listeners.value.copy()
        if point in current_listeners:
            listener_list = current_listeners[point]
            new_list = listener_list.value.copy() if hasattr(listener_list, 'value') else listener_list.copy()
            if callback_function in new_list:
                new_list.remove(callback_function)
                current_listeners[point] = RxList(new_list)
                self._listeners.value = current_listeners
                
    def get_listener_count(self):
        """Get the total number of registered breakpoint listeners"""
        total = 0
        for point, listener_list in self._listeners.value.items():
            count = len(listener_list.value) if hasattr(listener_list, 'value') else len(listener_list)
            total += count
            print(f"  {point}: {count} listeners")
        return total

    def get_all_listener_counts(self):
        """Get detailed listener counts for all reactive properties"""
        print("\n" + "="*60)
        print("COMPLETE MEDIAQUERY LISTENER REPORT")
        print("="*60)
        
        # Breakpoint listeners
        print("\n1. BREAKPOINT LISTENERS:")
        breakpoint_total = 0
        for point, listener_list in self._listeners.value.items():
            count = len(listener_list.value) if hasattr(listener_list, 'value') else len(listener_list)
            breakpoint_total += count
            print(f"   {point}: {count} listeners")
        print(f"   Subtotal: {breakpoint_total}")
        
        # Reactive property listeners
        print("\n2. REACTIVE PROPERTY LISTENERS:")
        
        properties = {
            'window_width': self.window_width,
            'window_height': self.window_height,
            'shared_container_width': self.shared_container_width,
            'shared_text_field_width': self.shared_text_field_width,
            'auth_divider_width': self.auth_divider_width,
            'auth_navigation_controls_width': self.auth_navigation_controls_width,
        }
        
        reactive_total = 0
        for prop_name, prop in properties.items():
            count = 0
            if hasattr(prop, '_listeners'):
                count = len(prop._listeners)
            reactive_total += count
            print(f"   {prop_name}: {count} listeners")
        
        print(f"   Subtotal: {reactive_total}")
        
        # Current breakpoint listeners
        print("\n3. CURRENT BREAKPOINT LISTENERS:")
        current_bp_listeners = 0
        if hasattr(self.current_breakpoint, '_listeners'):
            current_bp_listeners = len(self.current_breakpoint._listeners)
        print(f"   current_breakpoint: {current_bp_listeners} listeners")
        
        # Grand total
        grand_total = breakpoint_total + reactive_total + current_bp_listeners
        print("\n" + "-"*60)
        print(f"GRAND TOTAL: {grand_total} listeners")
        print("="*60 + "\n")
        
        return {
            'breakpoint_listeners': breakpoint_total,
            'reactive_property_listeners': reactive_total,
            'current_breakpoint_listeners': current_bp_listeners,
            'grand_total': grand_total
        }

    def dispose(self):
        """Override FletXController's dispose"""
        try:
            self.cleanup()
            
            if hasattr(self, '_children'):
                try:
                    if hasattr(self._children, 'value'):
                        children = list(self._children.value) if self._children.value else []
                    elif hasattr(self._children, '__iter__'):
                        children = list(self._children)
                    else:
                        children = []
                    
                    for child in children:
                        try:
                            if hasattr(child, 'dispose'):
                                child.dispose()
                        except Exception as child_error:
                            print(f"Error disposing child: {child_error}")
                    
                    if hasattr(self._children, 'value'):
                        self._children.value = []
                    elif hasattr(self._children, 'clear'):
                        self._children.clear()
                        
                except Exception as children_error:
                    print(f"Error handling children during disposal: {children_error}")
            
            print("MediaQueryController disposed successfully")
            
        except Exception as e:
            print(f"Error during MediaQueryController disposal: {e}")

    def cleanup(self):
        """Clean up controller resources without destroying core state"""
        try:
            print("MediaQueryController cleanup completed (core state preserved)")
        except Exception as e:
            print(f"Error during cleanup: {e}")

    @classmethod
    def reset_shared_state(cls):
        """Reset only page-specific state during navigation"""
        try:
            # Only clear reactive property listeners (page-specific UI updates)
            for prop in [cls._shared_container_width, cls._shared_text_field_width, 
                        cls._auth_divider_width, cls._auth_navigation_controls_width]:
                if hasattr(prop, '_listeners') and hasattr(prop._listeners, 'clear'):
                    prop._listeners.clear()
            
            print("MediaQuery page-specific listeners cleared")
            
        except Exception as e:
            print(f"Error resetting shared state: {e}")

    @classmethod
    def complete_shutdown(cls):
        """Complete reset for app shutdown"""
        try:
            # Clear all listeners
            for point in list(cls._shared_listeners.value.keys()):
                listener_list = cls._shared_listeners.value.get(point)
                if listener_list and hasattr(listener_list, 'value'):
                    listener_list.value = []
            
            for prop in [cls._shared_container_width, cls._shared_text_field_width, 
                        cls._auth_divider_width, cls._auth_navigation_controls_width,
                        cls._shared_width, cls._shared_height, cls._shared_current_breakpoint]:
                if hasattr(prop, '_listeners') and hasattr(prop._listeners, 'clear'):
                    prop._listeners.clear()
            
            # Reset everything
            cls._shared_breakpoints.value = {}
            cls._shared_listeners.value = {}
            cls._shared_initialized = False
            cls._shared_registration_complete = False
            cls._shared_page = None
            
            # Reset to defaults
            cls._shared_width.value = 1912
            cls._shared_height.value = 810
            cls._shared_current_breakpoint.value = "desktop"
            cls._shared_container_width.value = SharedContainerSizes.DESKTOP_WIDTH
            cls._shared_text_field_width.value = InputFieldSizes.DESKTOP_WIDTH
            cls._auth_divider_width.value = AuthDividerSizes.DESKTOP_WIDTH
            cls._auth_navigation_controls_width.value = AuthNavigationControlSizes.DESKTOP_WIDTH
            
            if hasattr(cls, '_listeners_initialized'):
                delattr(cls, '_listeners_initialized')
            
            print("MediaQuery completely shut down and reset")
            
        except Exception as e:
            print(f"Error during complete shutdown: {e}")
            
FletX.put(MediaQueryController(), tag='media_query_ctrl')