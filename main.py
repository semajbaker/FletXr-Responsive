import flet as ft
from fletx.app import FletXApp
from utils.responsive_manager import MediaQuery
from fletx.navigation import NavigationMode
from utils.routes import AppRouter

def main():
    async def on_startup(page: ft.Page):
        print("App is running")
        # Initialize MediaQuery
        MediaQuery.initialize_with_page(page)
        MediaQuery.register("mobile", 0, 768)
        MediaQuery.register("tablet", 768, 1024)
        MediaQuery.register("desktop", 1024, float('inf'))
        MediaQuery.complete_registration()
        print("MediaQuery breakpoints registered")

    def on_system_exit(page: ft.Page):
        print("App has shutdown")

    app = FletXApp(
        title="FletXr Responsive UI",
        initial_route="/signin",
        debug=False,
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