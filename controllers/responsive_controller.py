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
        self.current_breakpoint = MediaQueryController._shared_current_breakpoint
        self._breakpoints = MediaQueryController._shared_breakpoints
        self._listeners = MediaQueryController._shared_listeners
        
        # Reactive UI dimensions
        self.shared_container_width = MediaQueryController._shared_container_width
        self.shared_text_field_width = MediaQueryController._shared_text_field_width
        self.auth_divider_width = MediaQueryController._auth_divider_width
        self.auth_navigation_controls_width = MediaQueryController._auth_navigation_controls_width
        
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
        
        # Always set/update the resize handler
        page.on_resized = self._handle_resize
        
        # Set initial width if available
        if hasattr(page, 'width') and page.width:
            self.window_width.value = page.width
            print(f"MediaQuery initialized with page width: {page.width}")
        
        # Mark as initialized
        self._initialized = True
        print(f"MediaQuery page initialization complete. Handler attached: {page.on_resized is not None}")
    
    def _handle_resize(self, event: ft.WindowResizeEvent):
        """Handle window resize events from Flet"""
        print(f"Resize event detected: {event.width}x{event.height}")
        self.window_width.value = event.width
    
    def complete_registration(self):
        """Call this after all breakpoints are registered to trigger initial check"""
        self._registration_complete = True
        if self._initialized:
            self._check_for_updates(self.window_width.value)
    
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
                
    def get_listener_count(self):
        """Get the total number of registered breakpoint listeners (for debugging)"""
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
        
        # 1. Breakpoint listeners
        print("\n1. BREAKPOINT LISTENERS:")
        breakpoint_total = 0
        for point, listener_list in self._listeners.value.items():
            count = len(listener_list.value) if hasattr(listener_list, 'value') else len(listener_list)
            breakpoint_total += count
            print(f"   {point}: {count} listeners")
        print(f"   Subtotal: {breakpoint_total}")
        
        # 2. Reactive property listeners (UI dimensions)
        print("\n2. REACTIVE PROPERTY LISTENERS:")
        
        # Check window_width listeners
        width_listeners = 0
        if hasattr(self.window_width, '_listeners'):
            width_listeners = len(self.window_width._listeners)
        print(f"   window_width: {width_listeners} listeners")
        
        # Check shared_container_width listeners
        container_listeners = 0
        if hasattr(self.shared_container_width, '_listeners'):
            container_listeners = len(self.shared_container_width._listeners)
        print(f"   shared_container_width: {container_listeners} listeners")
        
        # Check shared_text_field_width listeners
        textfield_listeners = 0
        if hasattr(self.shared_text_field_width, '_listeners'):
            textfield_listeners = len(self.shared_text_field_width._listeners)
        print(f"   shared_text_field_width: {textfield_listeners} listeners")
        
        # Check auth_divider_width listeners
        divider_listeners = 0
        if hasattr(self.auth_divider_width, '_listeners'):
            divider_listeners = len(self.auth_divider_width._listeners)
        print(f"   auth_divider_width: {divider_listeners} listeners")
        
        # Check auth_navigation_controls_width listeners
        nav_listeners = 0
        if hasattr(self.auth_navigation_controls_width, '_listeners'):
            nav_listeners = len(self.auth_navigation_controls_width._listeners)
        print(f"   auth_navigation_controls_width: {nav_listeners} listeners")
        
        reactive_total = (width_listeners + container_listeners + textfield_listeners + 
                          divider_listeners + nav_listeners)
        print(f"   Subtotal: {reactive_total}")
        
        # 3. Current breakpoint listener
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

    def debug_listener_details(self):
        """Show which specific functions are registered as listeners"""
        print("\n" + "="*60)
        print("DETAILED LISTENER INSPECTION")
        print("="*60)
        
        # Breakpoint listeners with function names
        print("\n1. BREAKPOINT LISTENERS (with function names):")
        for point, listener_list in self._listeners.value.items():
            listeners = listener_list.value if hasattr(listener_list, 'value') else listener_list
            print(f"\n   {point} ({len(listeners)} listeners):")
            for i, func in enumerate(listeners, 1):
                func_name = getattr(func, '__name__', str(func))
                func_class = func.__self__.__class__.__name__ if hasattr(func, '__self__') else 'Unknown'
                print(f"      {i}. {func_class}.{func_name}")
        
        # Reactive property listeners
        print("\n2. REACTIVE PROPERTY LISTENERS (with function names):")
        
        properties = {
            'window_width': self.window_width,
            'shared_container_width': self.shared_container_width,
            'shared_text_field_width': self.shared_text_field_width,
            'auth_divider_width': self.auth_divider_width,
            'auth_navigation_controls_width': self.auth_navigation_controls_width,
            'current_breakpoint': self.current_breakpoint
        }
        
        for prop_name, prop in properties.items():
            if hasattr(prop, '_listeners'):
                listeners = list(prop._listeners)
                print(f"\n   {prop_name} ({len(listeners)} listeners):")
                for i, func in enumerate(listeners, 1):
                    func_name = getattr(func, '__name__', str(func))
                    func_class = func.__self__.__class__.__name__ if hasattr(func, '__self__') else 'Unknown'
                    print(f"      {i}. {func_class}.{func_name}")
        
        print("\n" + "="*60 + "\n")

    def dispose(self):
        """Override FletXController's dispose to handle RxList properly"""
        try:
            # Clean up our custom resources first
            self.cleanup()
            
            # Safely handle _children attribute
            if hasattr(self, '_children'):
                try:
                    # Try to get children as a list
                    if hasattr(self._children, 'value'):
                        children = list(self._children.value) if self._children.value else []
                    elif hasattr(self._children, '__iter__'):
                        children = list(self._children)
                    else:
                        children = []
                    
                    # Dispose all children
                    for child in children:
                        try:
                            if hasattr(child, 'dispose'):
                                child.dispose()
                        except Exception as child_error:
                            print(f"Error disposing child: {child_error}")
                    
                    # Clear children collection
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
            # Remove the resize handler from the old page
            if hasattr(self, '_page') and self._page:
                old_page = self._page
                if hasattr(old_page, 'on_resized'):
                    old_page.on_resized = None
                    print("Removed resize handler from old page")
            
            # DON'T clear window_width listeners - needed for responsive system
            # DON'T clear shared breakpoint listeners - they persist across pages
            # DON'T reset _registration_complete - stays true after main.py registration
            # DON'T reset _initialized - stays true after main.py initialization
            
            print("MediaQueryController cleanup completed (core state preserved)")
            
        except Exception as e:
            print(f"Error during cleanup: {e}")

    @classmethod
    def reset_shared_state(cls):
        """
        Reset only page-specific state during navigation.
        Preserves breakpoints, dimensions, and global state.
        """
        try:
            # DON'T clear breakpoint listeners - they persist across navigation
            # Only clear reactive property listeners (page-specific UI updates)
            
            for prop in [cls._shared_container_width, cls._shared_text_field_width, 
                        cls._auth_divider_width, cls._auth_navigation_controls_width]:
                if hasattr(prop, '_listeners') and hasattr(prop._listeners, 'clear'):
                    prop._listeners.clear()
            
            # DON'T reset breakpoints - registered once in main.py
            # DON'T clear _shared_listeners - breakpoint callbacks should persist
            # DON'T reset _shared_initialized - stays true after first page init
            # DON'T reset _shared_registration_complete - stays true after first registration
            # DON'T reset _shared_page - will be updated by next page's initialize_with_page
            # DON'T reset width or current breakpoint - preserve responsive state
            # DON'T reset dimension values - they update based on current breakpoint
            # DON'T delete _listeners_initialized - it should persist
            
            print("MediaQuery page-specific listeners cleared (breakpoint listeners preserved)")
            
        except Exception as e:
            print(f"Error resetting shared state: {e}")

    @classmethod
    def complete_shutdown(cls):
        """
        Complete reset for app shutdown.
        Resets EVERYTHING including breakpoints and state.
        """
        try:
            # Clear all listeners from shared state
            for point in list(cls._shared_listeners.value.keys()):
                listener_list = cls._shared_listeners.value.get(point)
                if listener_list and hasattr(listener_list, 'value'):
                    listener_list.value = []
            
            # Clear reactive property listeners
            for prop in [cls._shared_container_width, cls._shared_text_field_width, 
                        cls._auth_divider_width, cls._auth_navigation_controls_width,
                        cls._shared_width, cls._shared_current_breakpoint]:
                if hasattr(prop, '_listeners') and hasattr(prop._listeners, 'clear'):
                    prop._listeners.clear()
            
            # Reset everything for shutdown
            cls._shared_breakpoints.value = {}
            cls._shared_listeners.value = {}
            cls._shared_initialized = False
            cls._shared_registration_complete = False
            cls._shared_page = None
            
            # Reset to default values
            cls._shared_width.value = 1912
            cls._shared_current_breakpoint.value = "desktop"
            cls._shared_container_width.value = SharedContainerSizes.DESKTOP_WIDTH
            cls._shared_text_field_width.value = InputFieldSizes.DESKTOP_WIDTH
            cls._auth_divider_width.value = AuthDividerSizes.DESKTOP_WIDTH
            cls._auth_navigation_controls_width.value = AuthNavigationControlSizes.DESKTOP_WIDTH
            
            # Reset listener initialization flag
            if hasattr(cls, '_listeners_initialized'):
                delattr(cls, '_listeners_initialized')
            
            print("MediaQuery completely shut down and reset")
            
        except Exception as e:
            print(f"Error during complete shutdown: {e}")
            
FletX.put(MediaQueryController(), tag='media_query_ctrl')