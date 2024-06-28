import os
import openpyxl

# sheet_name = "reference_entities_crypto_domain.xlsx"
sheet_name = "reference_entities_crypto_domain _updated.xlsx"

def normalize_data_from_user_input():
    # Get the current working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory
    parent_dir = os.path.dirname(current_dir)
    # Get the grand parent directory
    grand_parent_dir = os.path.dirname(parent_dir)

    file_path = os.path.join(grand_parent_dir, "resources", sheet_name)

    # Load the XLSX file
    workbook = openpyxl.load_workbook(file_path)
    # Select the "crypto_transactions" sheet
    sheet = workbook["crypto_transactions"]
    
    categories = [cell.value for cell in sheet[1]]
    tx_data = []
    for i in range(2, sheet.max_row + 1, 1):
        # Read a specific row
        row_data = [cell.value for cell in sheet[i]]
        tx_obj = {}

        # Skip rows where all cell values are None or empty
        if all(cell is None or cell == "" for cell in row_data):
            continue
        
        # Append the row data to the tx_data list
        for j in range(0, len(row_data), 1):
            tx_obj[categories[j]] = row_data[j]

        tx_data.append(tx_obj)

    return {"transaction" : tx_data}