import flet as ft
from fletx.core import FletXController

def loading_indicator(
    controller: FletXController,
    page: ft.Page,
    message: str = 'loading',
):
        """Show loading when controller is in loading state."""

        if hasattr(loading_indicator,'dlg'):
            dlg = getattr(loading_indicator,'dlg')

        else: 
            dlg = ft.AlertDialog(
                content_padding = 10,
                title = ft.Text(
                    message,
                    size = 14,
                    text_align = ft.TextAlign.CENTER
                ),
                content = ft.Row(
                    expand = True,
                    alignment = ft.MainAxisAlignment.CENTER,
                    vertical_alignment = ft.CrossAxisAlignment.CENTER,
                    controls = [
                        ft.ProgressRing(
                            width=40, height=40
                        ),
                    ]
                ),
                alignment = ft.alignment.center,
                on_dismiss = lambda e: print("Dialog dismissed!"),
                title_padding = ft.padding.all(10),
            )
            loading_indicator.dlg = dlg

        if controller._is_loading.value:
            page.open(dlg)

        else: 
            page.close(dlg)