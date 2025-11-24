import flet as ft
from typing import Callable
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
    _shared_current_breakpoint = RxStr("desktop")
    _shared_registration_complete = False
    
    # Add reactive properties for UI dimensions
    _shared_container_width = RxInt(SharedContainerSizes.DESKTOP_WIDTH)
    _shared_text_field_width = RxInt(InputFieldSizes.DESKTOP_WIDTH)
    _auth_divider_width = RxInt(AuthDividerSizes.DESKTOP_WIDTH)
    
    def __init__(self):
        super().__init__()
        
        # Use shared class-level reactive state
        self.window_width = MediaQueryController._shared_width
        self.current_breakpoint = MediaQueryController._shared_current_breakpoint
        self._breakpoints = MediaQueryController._shared_breakpoints
        self._listeners = MediaQueryController._shared_listeners
        
        # Reactive UI dimensions
        self.shared_container_width = MediaQueryController._shared_container_width
        self.shared_text_field_width = MediaQueryController._shared_text_field_width
        self.auth_divider_width = MediaQueryController._auth_divider_width
        
        # Set up listeners only once - but don't trigger width changes during registration
        if not hasattr(MediaQueryController, '_listeners_initialized'):
            # Only listen to width changes, not breakpoint changes during registration
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
    
    def initialize_with_page(self, page: ft.Page):
        """Initialize with page reference - called from page's on_init"""
        if self._initialized:
            return
            
        page.on_resized = self._handle_resize
        
        # Set initial width if available - checks are prevented by _registration_complete flag
        if hasattr(page, 'width') and page.width:
            self.window_width.value = page.width
        
        self._initialized = True
    
    def complete_registration(self):
        """Call this after all breakpoints are registered to trigger initial check"""
        self._registration_complete = True
        if self._initialized:
            self._check_for_updates(self.window_width.value)
    
    def _handle_resize(self, event: ft.WindowResizeEvent):
        """Handle window resize events from Flet"""
        self.window_width.value = event.width
    
    def _on_width_changed(self):
        """React to width changes and update current breakpoint - only after registration is complete"""
        if self._registration_complete and self._initialized:
            self._check_for_updates(self.window_width.value)
    
    def _update_ui_dimensions(self, breakpoint: str):
        """Update UI dimensions based on current breakpoint"""
        if breakpoint == 'mobile':
            self.shared_container_width.value = SharedContainerSizes.MOBILE_WIDTH
            self.shared_text_field_width.value = InputFieldSizes.MOBILE_WIDTH
            self.auth_divider_width.value = AuthDividerSizes.MOBILE_WIDTH
        else:  # tablet and desktop
            self.shared_container_width.value = SharedContainerSizes.DESKTOP_WIDTH
            self.shared_text_field_width.value = InputFieldSizes.DESKTOP_WIDTH
            self.auth_divider_width.value = AuthDividerSizes.DESKTOP_WIDTH
    
    def _check_for_updates(self, width: int):
        """Check if breakpoint should change based on current width"""
        if not self._registration_complete:
            return
            
        print(f"Checking width: {width}")
        print(f"Available breakpoints: {list(self._breakpoints.value.keys())}")
        print(f"Available listeners: {list(self._listeners.value.keys())}")
        
        for name, (min_width, max_width) in self._breakpoints.value.items():
            print(f"Checking breakpoint '{name}': {min_width} < {width} <= {max_width}")
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
                                print(f"Calling listener: {func}")
                                func()
                            except Exception as e:
                                print(f"Error in breakpoint listener: {e}")
                    else:
                        print(f"No listeners found for breakpoint '{name}'")
                else:
                    # Even if breakpoint hasn't changed, ensure dimensions are correct
                    self._update_ui_dimensions(name)
                return
        
        print("No matching breakpoint found")
    
    def register(self, point: str, min_width: int, max_width: int):
        """Register a breakpoint with min/max width values"""
        current_breakpoints = self._breakpoints.value.copy()
        current_breakpoints[point] = (min_width, max_width)
        self._breakpoints.value = current_breakpoints
        
        current_listeners = self._listeners.value.copy()
        if point not in current_listeners:
            current_listeners[point] = RxList([])
            self._listeners.value = current_listeners
        
        # Don't trigger updates during registration phase
    
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
        
        # If this breakpoint is currently active and registration is complete, call the callback immediately
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