from ralph.kroger import get_item_price

def combine_recipies(google_sheets_token: str, kroger_token: str) -> int:
    '''Combines all recipies on the google sheets into preliminary lists

    Args:
        google_sheets_token (str): secret for editing google sheets
        kroger_token (str): secret for accessing item price through kroger fn
    Returns:
        int: a return code of 0 for success
    '''
    return 

def get_UPC_and_quantity(google_sheets_token: str) -> dict[int:int]:
    return

def write_to_cookbook() -> int:
    return