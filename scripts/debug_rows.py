import sys
import os

# Add scripts directory to path to import load_xlsx_rows
sys.path.append(os.path.join(os.getcwd(), 're-archive-data', 'scripts'))
from import_verification_xlsx import load_xlsx_rows

def main():
    path = 're-archive-data/raw_data/발송현황_20260607.xlsx'
    rows = load_xlsx_rows(path)
    if not rows: return
    
    print("Header:", rows[0])
    print("Row 1:", rows[1])
    print("Row 2:", rows[2])

if __name__ == "__main__":
    main()
