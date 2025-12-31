import flet as ft

class SnackbarType:
    """Enum-like class for snackbar types"""
    ERROR = "error"
    SUCCESS = "success"
    INFO = "info"
    WARNING = "warning"

class SnackbarMessage:
    """Reusable snackbar message utility for consistent notifications across the app"""
    
    def _get_snackbar_config(self, snackbar_type):
        """Get configuration for different snackbar types"""
        configs = {
            SnackbarType.ERROR: {
                "icon": ft.Icons.ERROR_OUTLINE,
                "bgcolor": ft.Colors.RED_400,
                "duration": 5000
            },
            SnackbarType.SUCCESS: {
                "icon": ft.Icons.CHECK_CIRCLE_OUTLINE,
                "bgcolor": ft.Colors.GREEN,
                "duration": 3000
            },
            SnackbarType.INFO: {
                "icon": ft.Icons.INFO_OUTLINE,
                "bgcolor": ft.Colors.BLUE_400,
                "duration": 4000
            },
            SnackbarType.WARNING: {
                "icon": ft.Icons.WARNING_OUTLINED,
                "bgcolor": ft.Colors.ORANGE_400,
                "duration": 4000
            }
        }
        return configs.get(snackbar_type, configs[SnackbarType.INFO])
    
    def _format_message(self, message, snackbar_type):
        """Format message for display, handling multi-line validation errors"""
        if snackbar_type == SnackbarType.ERROR and "Validation Errors:" in message:
            lines = message.split("\n")
            error_list = [error.strip() for error in lines[1:] if error.strip()]
            if error_list:
                return "Validation Errors: " + " • ".join(error_list)
        return message
    
    def show(self, page, message, snackbar_type=SnackbarType.INFO):
        """
        Show a snackbar message
        
        Args:
            page: Flet page object
            message: Message to display
            snackbar_type: Type of snackbar (error, success, info, warning)
        """
        try:
            config = self._get_snackbar_config(snackbar_type)
            formatted_message = self._format_message(message, snackbar_type)
            
            snackbar = ft.SnackBar(
                content=ft.Row([
                    ft.Icon(
                        config["icon"], 
                        color=ft.Colors.WHITE, 
                        size=20
                    ),
                    ft.Text(
                        formatted_message,
                        color=ft.Colors.WHITE,
                        size=14,
                        expand=True,
                        no_wrap=False
                    )
                ]),
                bgcolor=config["bgcolor"],
                duration=config["duration"],
                action="DISMISS",
                action_color=ft.Colors.WHITE,
                behavior=ft.SnackBarBehavior.FLOATING,
                margin=ft.margin.all(10),
            )
            
            page.overlay.append(snackbar)
            snackbar.open = True
            page.update()
            
            print(f"[SNACKBAR] {snackbar_type.upper()} message displayed: {formatted_message}")
            
        except Exception as e:
            print(f"[ERROR] Failed to show {snackbar_type} snackbar: {e}")
    
    def show_error(self, page, message):
        """Show error snackbar"""
        self.show(page, message, SnackbarType.ERROR)
    
    def show_success(self, page, message):
        """Show success snackbar"""
        self.show(page, message, SnackbarType.SUCCESS)
    
    def show_info(self, page, message):
        """Show info snackbar"""
        self.show(page, message, SnackbarType.INFO)
    
    def show_warning(self, page, message):
        """Show warning snackbar"""
        self.show(page, message, SnackbarType.WARNING)

# Utility functions for quick access
def show_error_message(page, message):
    """Quick function to show error message"""
    snackbar = SnackbarMessage()
    snackbar.show_error(page, message)

def show_success_message(page, message):
    """Quick function to show success message"""
    snackbar = SnackbarMessage()
    snackbar.show_success(page, message)

def show_info_message(page, message):
    """Quick function to show info message"""
    snackbar = SnackbarMessage()
    snackbar.show_info(page, message)

def show_warning_message(page, message):
    """Quick function to show warning message"""
    snackbar = SnackbarMessage()
    snackbar.show_warning(page, message)