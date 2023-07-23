import ralph.ui
import ralph.kroger as kg

class Ralph:
    def __init__(self, name: str) -> None:
        pass

    def ui_stub(self) -> list[int]:
        return ui.get_UPCs('dummy_url')
    
    def kroger_stub(self) -> int:
        return kg.buy_item(123)