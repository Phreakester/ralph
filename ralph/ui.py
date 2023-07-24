from kroger import get_item_price, get_item_size
import gspread
import pandas as pd

import warnings
warnings.filterwarnings('ignore')

shopping_list_sheet_name = "Ralphs Shopping List"
number_of_recipies = 2
start_row_of_ingredients = 7
stop_row_of_ingredients = 50
columns_names=['description', 'UPC',  'UPC quantity','UPC size', 'is stocked', 'item price', 'row price']
required_columns = ['UPC',  'UPC quantity']

def check_required_columns(df, required_columns):
    """
    Check if required columns in a DataFrame have non-empty values for each row.

    Parameters:
        df (pd.DataFrame): The DataFrame to check.
        required_columns (list): A list of column names that must be filled.

    Raises:
        ValueError: If any of the required columns have missing values for any row.
    """
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' not found in the DataFrame.")

        if df[col].isnull().any():
            raise ValueError(f"Column '{col}' has missing values in the DataFrame.")

def process_recipe(shopping_sheet, kroger_token: str, recipe_index: int) -> pd.DataFrame:
    # load in ingredients from recipe sheet in the shopping list spreadsheet
    worksheet = shopping_sheet.worksheet(f"Recipe {recipe_index}")

    recipe_ingredients = pd.DataFrame(worksheet.get_values(f'A{start_row_of_ingredients-1}:G{stop_row_of_ingredients}'))
    recipe_ingredients.columns = recipe_ingredients.iloc[0]  # Set the first row as the header
    recipe_ingredients = recipe_ingredients[1:]  # Remove the first row (it's now duplicated as the header)
    
    recipe_ingredients['UPC quantity'] = pd.to_numeric(recipe_ingredients['UPC quantity'], errors='coerce') # convert quantity to be numeric

    check_required_columns(recipe_ingredients, required_columns)

    # find price of each line item
    recipe_ingredients["item price"] = recipe_ingredients.apply(lambda row: get_item_price(row['UPC'], kroger_token), axis=1)
    recipe_ingredients["UPC size"] = recipe_ingredients.apply(lambda row: get_item_size(row['UPC'], kroger_token), axis=1)
    recipe_ingredients["row price"] = recipe_ingredients["item price"]*recipe_ingredients["UPC quantity"]

    # iterate through items and paste in prices
    total_price = 0
    for index, row in recipe_ingredients.iterrows():
        print("    processing: " + row["description"])
        worksheet.update(f"D{start_row_of_ingredients+index-1}", row['UPC size'])
        worksheet.update_acell(f"F{start_row_of_ingredients+index-1}", row['item price'])
        worksheet.update_acell(f"G{start_row_of_ingredients+index-1}", row['row price'])
        
        if not row['is stocked']:
            total_price += row['row price']
    worksheet.update('B5', total_price)
    return recipe_ingredients

def combine_recipies(service_acount, kroger_token: str) -> None:
    shopping_sheet = service_acount.open(shopping_list_sheet_name)
    all_ingredients = pd.DataFrame(columns=columns_names)

    for recipe_index in range(number_of_recipies):
        print("Processing recipe: " + str(recipe_index))
        all_ingredients = pd.concat([all_ingredients, 
                                     process_recipe(shopping_sheet, kroger_token, recipe_index)], 
                                     axis=0, 
                                     ignore_index=True) 
        
    # group by UPC and sum quantity
    all_ingredients = all_ingredients.groupby(['UPC']).agg({'UPC quantity': 'sum', 'item price': 'max', 'row price': 'sum', 'is stocked':'max', 'description':'sum'}).reset_index()
    # sort by is stocked
    all_ingredients = all_ingredients.sort_values(by=['is stocked'], ascending=False)
    # write to shopping list
    print("writing to shopping list")
    shopping_list = shopping_sheet.worksheet("Shopping List")
    shopping_list.clear()
    shopping_list.update([all_ingredients.columns.values.tolist()] + all_ingredients.values.tolist())
    return 

def get_UPC_and_quantity(shopping_sheet) -> dict[int:int]:
    return

def write_to_cookbook() -> int:
    return


if __name__ == "__main__":
    gc = gspread.service_account()
    combine_recipies(gc, 'hihi')