"""
Main application file with responsive system integration.

File: main.py
"""
import os
import warnings
import flet as ft
from fletx.app import FletXApp
from fletx.navigation import NavigationMode
from fletx import FletX
from pages.auth.signin_screen import SignInScreen
from pages.auth.signup_screen import SignUpScreen
from pages.auth.forgot_password_screen import ForgotPasswordScreen
from utils.responsive_manager import MediaQuery
from fletx.navigation import router_config
from controllers.animation_controller import AnimationController

def main():
    async def on_startup(page: ft.Page):
        print("App is running!")
        
        # Initialize MediaQuery
        MediaQuery.initialize_with_page(page)
        MediaQuery.register("mobile", 0, 768)
        MediaQuery.register("tablet", 768, 1024)
        MediaQuery.register("desktop", 1024, float('inf'))
        MediaQuery.complete_registration()
        print("MediaQuery breakpoints registered")
        
        # Initialize AnimationController ONCE and register it globally
        animation_controller = AnimationController()
        FletX.put(animation_controller, tag='animation_ctrl')
        print("AnimationController initialized globally")
        
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
        window_config={
            "resizable": True,
            "maximizable": True,
            "width": 600,
            "height": 810,
        }
    ).with_theme(
        ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    )
    
    # Run the app
    app.run_async()

if __name__ == "__main__":
    warnings.filterwarnings("ignore", message=".*websockets.*", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message=".*ws_handler.*", category=DeprecationWarning)
    main()