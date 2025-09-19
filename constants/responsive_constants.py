"""
Responsive breakpoint constants following Material Design guidelines.

File: constants/responsive_constants.py
"""

class ResponsiveBreakpoints:
    """Breakpoint definitions following Material Design"""
    
    # Breakpoint ranges (min_width, max_width)
    MOBILE = (0, 599)
    TABLET = (600, 1023) 
    DESKTOP = (1024, 9999)  # Use large number instead of float('inf')
    
    # Breakpoint names
    MOBILE_KEY = "mobile"
    TABLET_KEY = "tablet"
    DESKTOP_KEY = "desktop"

class InputFieldSizes:
    """Input field width constants for different breakpoints"""
    
    MOBILE_WIDTH = 280
    TABLET_WIDTH = 320
    DESKTOP_WIDTH = 350