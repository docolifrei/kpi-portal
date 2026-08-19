import pandas as pd

# Replace 'your_data.csv' with the actual filename of your raw CSV
file_path = "your_data.csv"

try:
    # Read the dataset into a pandas DataFrame
    df = pd.read_csv(file_path)

    print("=== DATA OVERVIEW ===")
    print(f"Total Rows: {len(df)}")
    print(f"Columns Detected: {list(df.columns)}")

    print("\n=== SAMPLE DATA (First 5 Rows) ===")
    print(df.head())

    print("\n=== MISSING VALUES PER COLUMN ===")
    print(df.isnull().sum())

except FileNotFoundError:
    print(
        f"Error: Could not find '{file_path}'. Place the CSV in the same folder as this script."
    )
except Exception as e:
    print(f"An unexpected error occurred: {e}")