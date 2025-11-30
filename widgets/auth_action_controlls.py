import flet as ft
from utils.responsive_manager import MediaQuery
class ResponsiveAuthActionControls(ft.Container):
    """Reactive auth action controls that automatically update when breakpoints change."""
    
    def __init__(self, primary_action_text: str, primary_action_on_click, 
                 show_forgot_password: bool = False, forgot_password_on_click = None):
        self.primary_action_text = primary_action_text
        self.primary_action_on_click = primary_action_on_click
        self.show_forgot_password = show_forgot_password
        self.forgot_password_on_click = forgot_password_on_click
        
        self.container_width_rx = MediaQuery.get_auth_navigation_controls_width_rx()
        
        # CRITICAL: Store observer reference for cleanup
        self._container_width_observer = None
        
        # Determine prefix text
        if primary_action_text.lower() == "sign in":
            self.prefix_text = "Already have an account? "
        elif primary_action_text.lower() in ["sign up", "create account"]:
            self.prefix_text = "Don't have an account? "
        else:
            self.prefix_text = ""
        
        # Create sections
        self.primary_section = ft.Container(
            content=ft.Row(
                spacing=2,
                tight=True,
                controls=[
                    ft.Text(self.prefix_text, size=12, color=ft.Colors.BLUE_GREY_600),
                    ft.TextButton(
                        text=primary_action_text,
                        on_click=primary_action_on_click,
                        style=ft.ButtonStyle(
                            color=ft.Colors.BLUE_600,
                            overlay_color=ft.Colors.BLUE_50,
                            padding=ft.padding.all(0),
                        ),
                    ),
                ]
            )
        )
        
        if show_forgot_password and forgot_password_on_click:
            self.forgot_section = ft.Container(
                content=ft.TextButton(
                    text="Forgot Password?",
                    on_click=forgot_password_on_click,
                    style=ft.ButtonStyle(
                        color=ft.Colors.BLUE_600,
                        overlay_color=ft.Colors.BLUE_50,
                    ),
                )
            )
        else:
            self.forgot_section = ft.Container()
        
        self.content_layout = self._create_layout()
        
        super().__init__(
            width=self.container_width_rx.value,
            padding=ft.padding.symmetric(horizontal=20),
            content=self.content_layout
        )
        
        # Store observer reference
        self._container_width_observer = self.container_width_rx.listen(self._on_container_width_changed)
        
        # Register breakpoint listeners
        MediaQuery.on('mobile', self._on_mobile_breakpoint)
        MediaQuery.on('tablet', self._on_desktop_breakpoint)
        MediaQuery.on('desktop', self._on_desktop_breakpoint)
    
    def will_unmount(self):
        """Clean up listeners when widget is unmounted"""
        try:
            # Dispose observer properly
            if self._container_width_observer:
                self._container_width_observer.dispose()
                self._container_width_observer = None
            
            # Remove breakpoint listeners
            MediaQuery.off('mobile', self._on_mobile_breakpoint)
            MediaQuery.off('tablet', self._on_desktop_breakpoint)
            MediaQuery.off('desktop', self._on_desktop_breakpoint)
            
            print(f"ResponsiveAuthActionControls cleaned up")
        except Exception as e:
            print(f"Error cleaning up ResponsiveAuthActionControls: {e}")
    
    def _create_layout(self):
        current_breakpoint = MediaQuery.get_current_breakpoint()
        print(f"Creating layout for breakpoint: {current_breakpoint}")
        
        if current_breakpoint == 'mobile':
            return ft.Column(
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[self.primary_section, self.forgot_section]
            )
        else:
            return ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[self.primary_section, self.forgot_section]
            )
    
    def _on_mobile_breakpoint(self):
        self._update_layout()
    
    def _on_desktop_breakpoint(self):
        self._update_layout()
    
    def _update_layout(self):
        new_layout = self._create_layout()
        self.content = new_layout
        if hasattr(self, 'page') and self.page:
            self.update()
    
    def _on_container_width_changed(self):
        print(f"Auth controls container width changed to: {self.container_width_rx.value}")
        self.width = self.container_width_rx.value
        if hasattr(self, 'page') and self.page:
            self.update()


def auth_action_controlls(primary_action_text: str, primary_action_on_click,
                          show_forgot_password: bool = False, forgot_password_on_click = None):
    return ResponsiveAuthActionControls(
        primary_action_text,
        primary_action_on_click,
        show_forgot_password,
        forgot_password_on_click
    )