import sys
import os

# Add scripts directory to path to import load_xlsx_rows
sys.path.append(os.path.join(os.getcwd(), 're-archive-data', 'scripts'))

from import_verification_xlsx import load_xlsx_rows

def main():
    path = 're-archive-data/raw_data/참여자_현황.xlsx'
    try:
        rows = load_xlsx_rows(path)
        if not rows:
            print("No data found.")
            return

        headers = rows[0]
        print("Headers:")
        for i, header in enumerate(headers):
            print(f"{i}: {header}")

        print("\nSample Rows (first 3):")
        for row in rows[1:4]:
            print(row)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
