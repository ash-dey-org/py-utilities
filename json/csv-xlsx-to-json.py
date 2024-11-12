import pandas as pd
import json

def csv_to_json(csv_file_path, json_file_path):
    # Load the CSV file
    csv_data = pd.read_csv(csv_file_path)

    # Open the output file in write mode
    with open(json_file_path, 'w') as json_file:
        # Iterate through each row in the DataFrame and write it as a JSON object
        for _, row in csv_data.iterrows():
            json.dump(row.to_dict(), json_file)
            json_file.write('\n')  # Newline to separate JSON objects

    print("Output data written to file.... ", json_file_path)


def xlsx_to_json(xlsx_file_path, json_file_path):
    # Load the Excel file
    xlsx_data = pd.read_excel(xlsx_file_path)

     # Open the output file in write mode
    with open(json_file_path, 'w') as json_file:
        # Iterate through each row in the DataFrame and write it as a JSON object
        for _, row in xlsx_data.iterrows():
            json.dump(row.to_dict(), json_file)
            json_file.write('\n')

    print("Output data written to file.... ", json_file_path)


csv_to_json('./azure-bill-10-2024.csv', './azure-bill-10-2024.csv.json')
xlsx_to_json('./azure-bill-10-2024.xlsx', './azure-bill-10-2024.xlsx.json')