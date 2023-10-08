import ralph.ui as ui
import ralph.kroger as kg
import gspread
import PySimpleGUI as sg
import warnings

class Ralph:
    '''Main class for accessing ordering functionality'''
    def __init__(self, google_sheets_token: str, kroger_secret: str, kroger_location: int) -> None:
        self.google_sheets_token = google_sheets_token
        self.kroger = kg.krogerAPI(kroger_secret, kroger_location)
        self.gc = gspread.service_account(filename='service_account.json')
        warnings.filterwarnings('ignore')

    def testing(self):
        
        shopping_sheet = self.gc.open('Ralphs Shopping List')
        ui.process_recipe(shopping_sheet, self.kroger, "Jonah")
        #ui.combine_recipies(gc, self.kroger)
    
    def launch(self):
        layout = [
            [sg.Text('ralph moment')],
            [sg.Button('Process All Recipes'), sg.Button('Add All to Cart')]
        ]

        window = sg.Window("Ralph", layout)

        while True:
            event, values = window.read()
            if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
                break
            if event == 'Process All Recipes':
                #sheet = self.gc.open('Ralphs Shopping List')
                ui.combine_recipies(self.gc, self.kroger)
            if event == 'Add All to Cart':
                ui.add_all_to_cart(self.gc, self.kroger)
    
        window.close()
        