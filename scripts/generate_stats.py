import sys
import os
import json
import hashlib
import base64
from datetime import datetime
from collections import defaultdict
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

# Add scripts directory to path to import load_xlsx_rows
sys.path.append(os.path.join(os.getcwd(), 're-archive-data', 'scripts'))

from import_verification_xlsx import load_xlsx_rows

def sha256_hex(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()

def encrypt_data(data_dict, password):
    key = hashlib.sha256(password.encode()).digest()
    iv = os.urandom(16)
    json_data = json.dumps(data_dict, ensure_ascii=False).encode('utf-8')
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(json_data) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return {
        "iv": base64.b64encode(iv).decode('utf-8'),
        "ciphertext": base64.b64encode(ciphertext).decode('utf-8')
    }

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    path = os.path.join(project_root, 'raw_data', '발송현황.xlsx')
    
    if not os.path.exists(path):
        print(f"Error: {path} not found.")
        return

    stats_password = "72941" 

    try:
        rows = load_xlsx_rows(path)
        if not rows:
            print("No data found.")
            return

        data_rows = rows[1:]
        households = defaultdict(list)
        
        for row in data_rows:
            if len(row) < 11: continue
            bonbun = str(row[3]).strip()
            dong = str(row[4]).strip()
            ho = str(row[5]).strip()
            participation = str(row[10]).strip()
            is_shared = "공유 O" in str(row[0])
            submission = str(row[9]).strip() or "미제출"
            
            households[(bonbun, dong, ho)].append({
                "participation": participation,
                "is_shared": is_shared,
                "submission": submission,
                "dong": dong
            })

        def create_stat_structure():
            return {
                "total_households": 0,
                "full_done_households": 0,
                "partial_done_households": 0,
                "not_done_households": 0,
                "shared_households": 0,
                "single_households": 0,
                "participation_details": defaultdict(int),
                "submission_details": defaultdict(int),
                "dong_stats": defaultdict(lambda: {"total": 0, "done": 0})
            }

        stats = {
            "total": create_stat_structure(),
            "gyeongnam": create_stat_structure(),
            "byeoksan": create_stat_structure()
        }

        for (bonbun, dong, ho), members in households.items():
            apt = "gyeongnam" if bonbun in ["525", "526"] else "byeoksan"
            is_shared_household = any(m["is_shared"] for m in members) or len(members) > 1
            done_members = [m for m in members if m["participation"] == "완료"]
            
            status = "미동의"
            if len(done_members) == len(members): status = "전원완료"
            elif len(done_members) > 0: status = "일부완료"
            
            for category in ["total", apt]:
                s = stats[category]
                s["total_households"] += 1
                if is_shared_household: s["shared_households"] += 1
                else: s["single_households"] += 1
                if status == "전원완료": s["full_done_households"] += 1
                elif status == "일부완료": s["partial_done_households"] += 1
                else: s["not_done_households"] += 1
                
                # Dong stats
                if dong:
                    s["dong_stats"][dong]["total"] += 1
                    if status == "전원완료":
                        s["dong_stats"][dong]["done"] += 1

                for m in members:
                    s["participation_details"][m["participation"]] += 1
                    s["submission_details"][m["submission"]] += 1

        def finalize(cat_data):
            count = cat_data["total_households"]
            # Sort dongs numerically or alphabetically
            sorted_dongs = sorted(cat_data["dong_stats"].keys(), key=lambda x: (x.isdigit(), int(x) if x.isdigit() else x))
            dong_list = []
            for d in sorted_dongs:
                d_total = cat_data["dong_stats"][d]["total"]
                d_done = cat_data["dong_stats"][d]["done"]
                dong_list.append({
                    "label": f"{d}동",
                    "total": d_total,
                    "done": d_done,
                    "rate": round((d_done / d_total * 100), 1) if d_total > 0 else 0
                })

            return {
                "count": count,
                "full_done_count": cat_data["full_done_households"],
                "full_done_rate": round((cat_data["full_done_households"] / count * 100), 1) if count > 0 else 0,
                "partial_done_count": cat_data["partial_done_households"],
                "shared_count": cat_data["shared_households"],
                "single_count": cat_data["single_households"],
                "household_stats": [
                    {"label": "전원 동의 세대 (완료)", "value": cat_data["full_done_households"]},
                    {"label": "일부 동의 세대 (진행중)", "value": cat_data["partial_done_households"]},
                    {"label": "미동의 세대", "value": cat_data["not_done_households"]}
                ],
                "owner_type_stats": [
                    {"label": "단독 소유 세대", "value": cat_data["single_households"]},
                    {"label": "공동 소유 세대", "value": cat_data["shared_households"]}
                ],
                "participation_details": sorted([{"label": k, "value": v} for k, v in cat_data["participation_details"].items()], key=lambda x: x["value"], reverse=True),
                "submission_details": sorted([{"label": k, "value": v} for k, v in cat_data["submission_details"].items()], key=lambda x: x["value"], reverse=True),
                "dong_stats": dong_list
            }

        raw_stats = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": finalize(stats["total"]),
            "gyeongnam": finalize(stats["gyeongnam"]),
            "byeoksan": finalize(stats["byeoksan"])
        }
        
        final_payload = encrypt_data(raw_stats, stats_password)
        output_path = os.path.join(project_root, 'assets', 'data', 'stats.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_payload, f, ensure_ascii=False, indent=2)
            
        print(f"ENCRYPTED Stats with Dong-level data generated: {output_path}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
