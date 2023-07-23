import ralph.ui as ui
import ralph.kroger as kg

class Ralph:
    '''Main class for accessing ordering functionality'''
    def __init__(self, google_sheets_token: str, kroger_token: str) -> None:
        self.google_sheets_token = google_sheets_token
        self.kroger_token = kroger_token

    def ui_stub(self) -> list[int]:
        return ui.get_UPCs('dummy_url')

    def kroger_stub(self) -> int:
        return kg.buy_item(123)