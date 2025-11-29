"""
Main application file with responsive system integration.

File: main.py
"""
import os
import warnings
import flet as ft
from fletx.app import FletXApp
from fletx.core import RxInt, RxStr
from pages.auth.signin_screen import SignInScreen
from pages.auth.signup_screen import SignUpScreen
from pages.auth.forgot_password_screen import ForgotPasswordScreen
from utils.responsive_manager import MediaQuery
from fletx.navigation import router_config
    
def main():
    mobile_text = RxStr('mobile')
    mobile_min_width = RxStr(0)
    mobile_max_width = RxInt(768)
    tablet_text = RxStr('tablet')
    tablet_min_width = RxStr(768)
    tablet_max_width = RxStr(1024)
    desktop_text = RxStr('desktop')
    desktop_min_width = RxStr(1024)
    desktop_max_width = RxStr(1924)

    async def on_startup(page: ft.Page):
        print("App is running!")
        print(os.getenv('FLETX_DEBUG'))
            # Initialize MediaQuery first
        MediaQuery.initialize_with_page(page)

    def on_shutdown(page: ft.Page):
        print("App is closed!")
        
    # Add your route
    routes = [
        {
        "path": "/signin",
        "component": SignInScreen,

        },
        {
            "path": "/signup",
            "component": SignUpScreen,

        },
        {
            "path": "/forgot-password",
            "component": ForgotPasswordScreen,

        }
    ]
    router_config.add_routes(routes)
    
    # Register all breakpoints
    MediaQuery.register(mobile_text.value, mobile_min_width.value, mobile_max_width.value)     
    MediaQuery.register(tablet_text.value, tablet_min_width.value, tablet_max_width.value)     
    MediaQuery.register(desktop_text.value, desktop_min_width.value, desktop_max_width.value)     
    
    # Complete registration - this will trigger the initial breakpoint check
    MediaQuery.complete_registration()
    
    # Create the FletXr app
    app = FletXApp(
        title="FletXr Responsive UI",
        initial_route="/signin",
        debug=True,
        on_startup = on_startup,
        on_shutdown = on_shutdown
    ).with_theme(
        ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    )
    
    # Run the app
    app.run_async()

if __name__ == "__main__":
    warnings.filterwarnings("ignore", message=".*websockets.*", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message=".*ws_handler.*", category=DeprecationWarning)
    main()