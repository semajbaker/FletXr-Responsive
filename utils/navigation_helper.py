"""
Navigation helper that ensures proper cleanup before navigation.

File: utils/navigation_helper.py
"""
from fletx.navigation import navigate as fletx_navigate
from fletx.core import FletXPage
from typing import Optional

def safe_navigate(
    route: str,
    current_page: Optional[FletXPage] = None,
    replace: bool = False,
    clear_history: bool = False
):
    """
    Navigate to a new route with proper cleanup.
    
    Args:
        route: The target route path
        current_page: The current FletXPage instance (to call will_unmount)
        replace: Whether to replace current route
        clear_history: Whether to clear navigation history
    """
    # Call will_unmount on current page if provided
    if current_page is not None:
        try:
            if hasattr(current_page, 'will_unmount'):
                print(f"Calling will_unmount on {current_page.__class__.__name__}")
                current_page.will_unmount()
        except Exception as e:
            print(f"Error during will_unmount: {e}")
    
    # Proceed with navigation
    fletx_navigate(route, replace=replace, clear_history=clear_history)