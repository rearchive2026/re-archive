import sys
import os

# Add scripts directory to path to import load_xlsx_rows
sys.path.append(os.path.join(os.getcwd(), 're-archive-data', 'scripts'))

from import_verification_xlsx import load_xlsx_rows

def main():
    path = 're-archive-data/raw_data/발송현황.xlsx'
    try:
        rows = load_xlsx_rows(path)
        if not rows:
            print("No data found.")
            return

        headers = rows[0]
        print("Headers (Row 0):")
        for i, h in enumerate(headers):
            print(f"{i}: {h}")

        print("\nRow 1:")
        print(rows[1])
        
        print("\nRow 2:")
        print(rows[2])

        print("\nSample Data Row (Row 3):")
        if len(rows) > 3:
            print(rows[3])
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
