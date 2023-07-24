import ralph.ui as ui
import ralph.kroger as kg

class Ralph:
    '''Main class for accessing ordering functionality'''
    def __init__(self, google_sheets_token: str, kroger_secret: str, kroger_location: int) -> None:
        self.google_sheets_token = google_sheets_token
        self.kroger = kg.krogerAPI(kroger_secret, kroger_location)

    