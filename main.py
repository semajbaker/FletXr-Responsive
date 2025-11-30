"""
Main application file with responsive system integration.

File: main.py
"""
import os
import warnings
import flet as ft
from fletx.app import FletXApp
from pages.auth.signin_screen import SignInScreen
from pages.auth.signup_screen import SignUpScreen
from pages.auth.forgot_password_screen import ForgotPasswordScreen
from utils.responsive_manager import MediaQuery
from fletx.navigation import router_config
    
def main():
    async def on_startup(page: ft.Page):
        print("App is running!")
        print(os.getenv('FLETX_DEBUG'))
        
    def on_shutdown(page: ft.Page):
        print("App is closed!")
        # Clean up MediaQuery on shutdown
        MediaQuery.reset_all()
        
    # Add your routes
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
    
    # Create the FletXr app
    app = FletXApp(
        title="FletXr Responsive UI",
        initial_route="/signin",
        debug=False,
        on_startup=on_startup,
        on_shutdown=on_shutdown
    ).with_theme(
        ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    )
    
    # Run the app
    app.run_async()

if __name__ == "__main__":
    warnings.filterwarnings("ignore", message=".*websockets.*", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message=".*ws_handler.*", category=DeprecationWarning)
    main()