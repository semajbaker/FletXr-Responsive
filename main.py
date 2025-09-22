"""
Main application file with responsive system integration.

File: main.py
"""
import warnings
import flet as ft
from fletx.app import FletXApp
from fletx.core import RxInt, RxStr
from fletx.navigation import router_config
from pages.auth.signin_screen import SignInScreen
from utils.responsive_manager import MediaQuery

def _handle_mobile_layout():
    """Handle mobile breakpoint activation"""
    print("Switched to mobile layout")
    # Add mobile-specific layout changes here
    
def _handle_tablet_layout():
    """Handle tablet breakpoint activation"""
    print("Switched to tablet layout")
    # Add tablet-specific layout changes here
    
def _handle_desktop_layout():
    """Handle desktop breakpoint activation"""
    print("Switched to desktop layout")


def main(page: ft.Page):
    mobile_text = RxStr('mobile')
    mobile_min_width = RxStr(0)
    mobile_max_width = RxInt(768)
    tablet_text = RxStr('tablet')
    tablet_min_width = RxStr(768)
    tablet_max_width = RxStr(1024)
    desktop_text = RxStr('desktop')
    desktop_min_width = RxStr(1024)
    desktop_max_width = RxStr(1912)
    
    # Add your route
    router_config.add_routes([
        # Main entry point
        {"path": "/signin", "component": SignInScreen}  # Static settings page
    ])
    
    # Initialize MediaQuery first
    MediaQuery.initialize_with_page(page)
    
    # Register all breakpoints
    MediaQuery.register(mobile_text.value, mobile_min_width.value, mobile_max_width.value)     
    MediaQuery.register(tablet_text.value, tablet_min_width.value, tablet_max_width.value)     
    MediaQuery.register(desktop_text.value, desktop_min_width.value, desktop_max_width.value)     
    
    # Register all callbacks for breakpoint changes
    MediaQuery.on(mobile_text.value, _handle_mobile_layout)
    MediaQuery.on(tablet_text.value, _handle_tablet_layout)
    MediaQuery.on(desktop_text.value, _handle_desktop_layout)
    
    # Complete registration - this will trigger the initial breakpoint check
    MediaQuery.complete_registration()
    
    # Create the FletXr app
    app = FletXApp(
        title="Counter App",
        initial_route="/signin",
        debug=True,
    ).with_theme(
        ft.Theme(color_scheme_seed=ft.Colors.BLACK)
    )
    
    # Run the app
    app._main(page)

if __name__ == "__main__":
    warnings.filterwarnings("ignore", message=".*websockets.*", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message=".*ws_handler.*", category=DeprecationWarning)
    ft.app(target=main)