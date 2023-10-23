from ralph.kroger import krogerAPI
import gspread
import pandas as pd
import numpy as np
import PySimpleGUI as sg

import warnings
warnings.filterwarnings('ignore')

shopping_list_sheet_name = "Ralphs Shopping List"
number_of_recipies = 7
start_row_of_ingredients = 7
stop_row_of_ingredients = 107
columns_names=['Description', 'Recipe Quantity', 'Already Stocked?', 'UPC',  'UPC Quantity','UPC Size', 'Unit Price', 'Total Price']
required_columns = ['UPC',  'UPC Quantity']
recipe_names = ['Incedentals','Cameron', 'Jonah', 'Aidan', 'Getty', 'Drew', 'Trevor']
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

        #if df[col].isnull().any():
        #    raise ValueError(f"Column '{col}' has missing values in the DataFrame.")

def process_recipe(shopping_sheet, cartAPI: krogerAPI, recipe_name: str) -> pd.DataFrame:
    # load in ingredients from recipe sheet in the shopping list 
    #shopping_sheet = service_account.open(shopping_list_sheet_name)
    print(f"Proccessing recipe: {recipe_name}")

    worksheet = shopping_sheet.worksheet(recipe_name)

    recipe_ingredients = pd.DataFrame(worksheet.get_values(f'A{start_row_of_ingredients-1}:H{stop_row_of_ingredients}'))
    recipe_ingredients.columns = recipe_ingredients.iloc[0]  # Set the first row as the header
    recipe_ingredients = recipe_ingredients[1:]  # Remove the first row (it's now duplicated as the header)
    recipe_ingredients = recipe_ingredients.dropna(how='all')
    
    recipe_ingredients['UPC Quantity'] = pd.to_numeric(recipe_ingredients['UPC Quantity'], errors='coerce') # convert quantity to be numeric

    check_required_columns(recipe_ingredients, required_columns)

    # find price of each line item
    # detect missing UPCs
    get_missing_upc_ingredients = recipe_ingredients[(recipe_ingredients['UPC'] == "") & (recipe_ingredients['Already Stocked?'] == "FALSE") & (recipe_ingredients['Description'] != "")]
   
    for ingredient in get_missing_upc_ingredients['Description']:
        print(f"Warning --- missing UPC for {ingredient}")

    get_ingred = recipe_ingredients[(recipe_ingredients['UPC'] != "") & (recipe_ingredients['Already Stocked?'] == "FALSE") & (recipe_ingredients['UPC Quantity'].astype('float') >= 0)]
    upcList = get_ingred['UPC'].tolist()

    if len(upcList):
        item_data = cartAPI.getMultipleProductDetails(upcList)
        for i in item_data:
            try:
                if(i['items'][0]['fulfillment']['curbside'] == True):
                    print(f"Getting information for UPC: {i['items'][0]['itemId']}")
                    unit_price = float(i['items'][0]['price']['promo'] if i['items'][0]['price']['promo'] else i['items'][0]['price']['regular'])
                    recipe_ingredients.loc[recipe_ingredients['UPC'] == i['items'][0]['itemId'], 'Unit Price'] = unit_price
                    recipe_ingredients.loc[recipe_ingredients['UPC'] == i['items'][0]['itemId'], 'UPC Size'] = str(i['items'][0]['size'])
                    recipe_ingredients.loc[recipe_ingredients['UPC'] == i['items'][0]['itemId'], 'Total Price'] = unit_price * float(recipe_ingredients.loc[recipe_ingredients['UPC'] == i['items'][0]['itemId'], 'UPC Quantity'])
                else:
                    raise Exception(recipe_ingredients.loc[recipe_ingredients['UPC'] == i['items'][0]['itemId'], 'Description'] + " is not available!")
            except:
                print("Error getting information for UPC: " + i['items'][0]['itemId'])

        out = recipe_ingredients.loc[:, ['UPC Size', 'Unit Price', 'Total Price']]

        worksheet.update(f"F{start_row_of_ingredients}:H{start_row_of_ingredients+recipe_ingredients.shape[0]}", out.values.tolist())

        recipe_ingredients['Unit Price'].replace('', np.nan, inplace=True)    
                
        worksheet.update('B5', recipe_ingredients['Unit Price'].sum())
    return recipe_ingredients

def combine_recipies(service_acount, cartAPI: krogerAPI) -> None:
    shopping_sheet = service_acount.open(shopping_list_sheet_name)
    all_ingredients = pd.DataFrame(columns=columns_names)

    for recipe_name in recipe_names:
        sg.Print("Processing recipe: " + recipe_name)
        all_ingredients = pd.concat([all_ingredients, 
                                     process_recipe(shopping_sheet, cartAPI, recipe_name)], 
                                     axis=0, 
                                     ignore_index=True) 
        
    #all_ingredients['Already Stocked?'] = all_ingredients['Already Stocked?'].replace('', 'FALSE')
    all_ingredients[['UPC Quantity', 'Unit Price', 'Total Price']] = all_ingredients[['UPC Quantity', 'Unit Price', 'Total Price']].replace('', np.nan)
        
    all_ingredients = all_ingredients.astype({'UPC Quantity':'float', 
                                              'Unit Price':'float',
                                              'Total Price':'float', 
                                              'UPC Size':'str', 
                                              'Already Stocked?':'str',
                                              'Description':'str',
                                              'Recipe Quantity':'str'})
    # group by UPC and sum quantity
    all_ingredients = all_ingredients.groupby(['UPC']).agg({'UPC Quantity': 'sum', 'UPC Size':'sum', 'Unit Price': 'max', 'Total Price': 'sum', 'Already Stocked?':'max', 'Description':'sum', 'Recipe Quantity':'sum'}).reset_index()
    # sort by is stocked
    all_ingredients = all_ingredients.sort_values(by=['Already Stocked?'], ascending=False)
    # write to shopping list
    sg.Print("writing to shopping list")
    shopping_list = shopping_sheet.worksheet("Shopping List")
    shopping_list.clear()

    all_ingredients.replace(np.nan, '', inplace=True)  

    shopping_list.update([all_ingredients.columns.values.tolist()] + all_ingredients.values.tolist())
    sg.easy_print_close()
    return 

def get_UPC_and_quantity(shopping_sheet) -> dict[int:int]:
    return

def write_to_cookbook() -> int:
    return

def add_all_to_cart(service_account, cartAPI: krogerAPI):
    shopping_sheet = service_account.open(shopping_list_sheet_name)
    worksheet = shopping_sheet.worksheet("Shopping List")
    all_ingredients = pd.DataFrame(worksheet.get_values(f'A{2-1}:H{stop_row_of_ingredients}'))
    all_ingredients.rename(columns=all_ingredients.iloc[0], inplace=True)
    all_ingredients.drop(all_ingredients.index[0], inplace=True)
    all_ingredients = all_ingredients.astype({'UPC Quantity' : 'int16'})
    
    all_ingredients = all_ingredients[(all_ingredients['Already Stocked?'] == "FALSE") & (all_ingredients['UPC Quantity'] > 0)]
    all_ingredients = all_ingredients[['UPC', 'UPC Quantity']]
    ing_list = all_ingredients.values.tolist()
    #print(ing_list)
    sg.Print("Ordering", len(ing_list), "items.")
    cartAPI.putListInCart(ing_list)
    sg.Print("Success")
    sg.easy_print_close()



if __name__ == "__main__":
    gc = gspread.service_account()
    combine_recipies(gc, 'hihi')