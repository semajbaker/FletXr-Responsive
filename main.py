import flet as ft
from fletx.app import FletXApp
from fletx.navigation import NavigationMode

from app.utils.responsive_manager import MediaQuery
from app.routes import AppRouter
from app.utils.theme import light_theme, dark_theme

def main():

    async def on_startup(page: ft.Page):
        print("App is running")
        # remove page padding bby default
        page.padding = 0 
        # Register MediaQuery breakpoints (only once at startup)
        MediaQuery.register("mobile", 0, 768)
        MediaQuery.register("tablet", 768, 1024)
        MediaQuery.register("desktop", 1024, float('inf'))
        MediaQuery.complete_registration()
        print("MediaQuery breakpoints registered")

    def on_system_exit(page: ft.Page):
        MediaQuery.shutdown()
        print("App has shutdown")

    app = FletXApp(
        title="FletXr Responsive UI",
        initial_route="/",
        debug=False,
        theme = light_theme,
        dark_theme = dark_theme,
        theme_mode= ft.ThemeMode.SYSTEM,
        on_startup=on_startup,
        on_system_exit=on_system_exit,
        navigation_mode=NavigationMode.NATIVE,
        window_config={
            "resizable": True,
            "maximizable": True,
            "width": 600,
            "height": 810,
        }
    ).with_theme(
        ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    )
    app.run_async()

if __name__ == "__main__":
    main()