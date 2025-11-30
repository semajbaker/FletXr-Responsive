import flet as ft
from utils.responsive_manager import MediaQuery

class ResponsiveInputField(ft.Container):
    """Reactive input field that automatically updates when breakpoints change."""
    
    def __init__(self, hint_text: str, icon: ft.Icons, hide: bool = False, rx_value=None, on_change=None):
        # Get reactive properties
        self.container_width_rx = MediaQuery.get_shared_container_width_rx()
        self.field_width_rx = MediaQuery.get_text_field_width_rx()
        
        # Store the reactive value
        self.rx_value = rx_value
        
        # CRITICAL: Store observer references for cleanup
        self._container_width_observer = None
        self._field_width_observer = None
        self._rx_value_observer = None
        
        # Create the text field first
        self.text_field = ft.TextField(
            border_color="transparent",
            bgcolor="transparent",  
            hint_text=hint_text,
            hint_style=ft.TextStyle(size=14, color=ft.Colors.BLUE_GREY_400),
            height=40,
            width=self.field_width_rx.value,
            text_size=14,
            content_padding=0,
            cursor_color=ft.Colors.BLUE_600,
            password=hide,
            can_reveal_password=hide,
            text_style=ft.TextStyle(color=ft.Colors.BLUE_GREY_800, weight=ft.FontWeight.W_500),
            on_change=self._handle_text_change if rx_value else on_change
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
                    ft.Icon(icon, color=ft.Colors.BLUE_600, size=20),
                    self.text_field
                ]
            ),
        )
        
        # Set up listeners and STORE observer references
        self._container_width_observer = self.container_width_rx.listen(self._on_container_width_changed)
        self._field_width_observer = self.field_width_rx.listen(self._on_field_width_changed)
        
        if self.rx_value:
            self._rx_value_observer = self.rx_value.listen(self._on_rx_value_changed)
    
    def will_unmount(self):
        """Clean up listeners when widget is unmounted"""
        try:
            # Dispose observers properly using the Observer.dispose() method
            if self._container_width_observer:
                self._container_width_observer.dispose()
                self._container_width_observer = None
            
            if self._field_width_observer:
                self._field_width_observer.dispose
                self._field_width_observer = None
            
            if self._rx_value_observer:
                self._rx_value_observer.dispose()
                self._rx_value_observer = None
            
            print(f"ResponsiveInputField cleaned up")
        except Exception as e:
            print(f"Error cleaning up ResponsiveInputField: {e}")
    
    def _handle_text_change(self, e):
        if self.rx_value:
            self.rx_value.value = e.control.value
    
    def _on_rx_value_changed(self):
        if self.text_field.value != self.rx_value.value:
            self.text_field.value = self.rx_value.value
            if hasattr(self, 'page') and self.page:
                self.update()
    
    def _on_container_width_changed(self):
        self.width = self.container_width_rx.value
        if hasattr(self, 'page') and self.page:
            self.update()
    
    def _on_field_width_changed(self):
        self.text_field.width = self.field_width_rx.value
        if hasattr(self, 'page') and self.page:
            self.update()


def input_field(hint_text: str, icon: ft.Icons, hide: bool = False, rx_value=None, on_change=None):
    return ResponsiveInputField(hint_text, icon, hide, rx_value, on_change)
