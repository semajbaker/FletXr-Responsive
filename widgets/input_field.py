import flet as ft
from utils.responsive_manager import MediaQuery


class ResponsiveInputField(ft.Container):
    """Reactive input field that automatically updates when breakpoints change."""
    
    def __init__(self, hint_text: str, icon: ft.Icons, hide: bool = False):
        # Get reactive properties
        self.container_width_rx = MediaQuery.get_container_width_rx()
        self.field_width_rx = MediaQuery.get_field_width_rx()
        
        # Create the text field first so we can reference it in the listener
        self.text_field = ft.TextField(
            border_color="transparent",
            bgcolor="transparent",  
            hint_text=hint_text,
            hint_style=ft.TextStyle(
                size=14,
                color=ft.Colors.BLUE_GREY_400
            ),
            height=40,
            width=self.field_width_rx.value,
            text_size=14,
            content_padding=0,
            cursor_color=ft.Colors.BLUE_600,
            password=hide,
            can_reveal_password=hide,
            text_style=ft.TextStyle(
                color=ft.Colors.BLUE_GREY_800,
                weight=ft.FontWeight.W_500
            )
        )
        
        # Initialize the container
        super().__init__(
            width=self.container_width_rx.value,
            height=55,
            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_GREY_100),
            border_radius=15,
            border=ft.border.all(1.5, ft.Colors.with_opacity(0.3, ft.Colors.BLUE_400)),
            padding=ft.padding.symmetric(horizontal=15, vertical=8),
            content=ft.Row(
                spacing=15,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        icon, 
                        color=ft.Colors.BLUE_600,
                        size=20,
                    ),
                    self.text_field
                ]
            ),
        )
        
        # Set up listeners after initialization
        self.container_width_rx.listen(self._on_container_width_changed)
        self.field_width_rx.listen(self._on_field_width_changed)
    
    def _on_container_width_changed(self):
        """Called when container width changes"""
        print(f"Container width changed to: {self.container_width_rx.value}")
        self.width = self.container_width_rx.value
        if hasattr(self, 'page') and self.page:
            self.update()
    
    def _on_field_width_changed(self):
        """Called when field width changes"""
        print(f"Field width changed to: {self.field_width_rx.value}")
        self.text_field.width = self.field_width_rx.value
        if hasattr(self, 'page') and self.page:
            self.update()


def input_field(hint_text: str, icon: ft.Icons, hide: bool = False):
    """Factory function to create a responsive input field."""
    return ResponsiveInputField(hint_text, icon, hide)