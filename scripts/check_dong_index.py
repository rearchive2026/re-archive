import sys
import os

# Add scripts directory to path to import load_xlsx_rows
sys.path.append(os.path.join(os.getcwd(), 're-archive-data', 'scripts'))
from import_verification_xlsx import load_xlsx_rows

def main():
    path = 're-archive-data/raw_data/발송현황_20260607.xlsx'
    rows = load_xlsx_rows(path)
    if not rows: return
    
    dongs = set()
    for row in rows[1:]:
        if len(row) > 4:
            dongs.add(str(row[4]))
    
    print(f"Dongs found at index 4: {dongs}")

if __name__ == "__main__":
    main()
