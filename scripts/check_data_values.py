import sys
import os

sys.path.append(os.path.join(os.getcwd(), 're-archive-data', 'scripts'))
from import_verification_xlsx import load_xlsx_rows

def main():
    path = 're-archive-data/raw_data/발송현황.xlsx'
    rows = load_xlsx_rows(path)
    data_rows = rows[1:]
    
    print("Searching for Shared/Multi-parcel/Shared Consent rows...")
    found_shared = 0
    found_multi = 0
    found_shared_consent = 0
    
    for i, row in enumerate(data_rows):
        if row[0] and str(row[0]).strip():
            print(f"Row {i+1} Shared: '{row[0]}'")
            found_shared += 1
        if row[2] and str(row[2]).strip():
            print(f"Row {i+1} Multi: '{row[2]}'")
            found_multi += 1
        if row[1] and str(row[1]).strip():
            print(f"Row {i+1} Shared Consent: '{row[1]}'")
            found_shared_consent += 1
            
        if found_shared > 5 and found_multi > 5: break

    print(f"\nSummary: Shared={found_shared}, Multi={found_multi}, SharedConsent={found_shared_consent}")

if __name__ == "__main__":
    main()
