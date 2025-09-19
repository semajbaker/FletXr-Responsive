"""
Main application file with responsive system integration.

File: main.py
"""
import warnings
import flet as ft
from fletx.app import FletXApp
from fletx.navigation import router_config
from pages.auth.signin_screen import SignInScreen

def main():
    # Add your route
    router_config.add_route(path="/", component=SignInScreen)
    
    # Create the FletXr app
    app = FletXApp(
        title="Counter App",
        initial_route="/",
        debug=True
    ).with_theme(
        ft.Theme(color_scheme_seed=ft.Colors.BLACK)
    )
    
    # Run the app
    app.run()

if __name__ == "__main__":
    warnings.filterwarnings("ignore", message=".*websockets.*", category=DeprecationWarning)
    warnings.filterwarnings("ignore", message=".*ws_handler.*", category=DeprecationWarning)
    main()