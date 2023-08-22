import csv

# Read the CSV file and print column names
with open('Logging.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    column_names = next(reader)  # Read the first row containing column names
    print(column_names)