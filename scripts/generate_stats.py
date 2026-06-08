import sys
import os
import json
import hashlib
import base64
import re
from datetime import datetime
from collections import defaultdict
from pathlib import Path
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from import_verification_xlsx import load_xlsx_rows
from stats_source import (
    build_stats_column_map,
    cell_value,
    display_dong_label,
    effective_submission,
    sort_dong_key,
)

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

PRIVACY_NEEDED_STATUS = "비대상"
DONE_STATUS = "완료"
SENT_STATUS = "발송"
VIEWED_STATUS = "열람"
RESERVED_STATUS = "예약"


def display_participation_label(status):
    labels = {
        PRIVACY_NEEDED_STATUS: "개인정보 동의 필요(비대상)",
        DONE_STATUS: "2차 전자 동의 완료",
        SENT_STATUS: "발송 후 미열람",
        VIEWED_STATUS: "열람 후 미완료",
        RESERVED_STATUS: "예약",
        "": "상태 없음",
    }
    return labels.get(status, status)


def resolve_source_path(project_root):
    raw_data_path = project_root / "raw_data"
    dated_sources = []
    for path in raw_data_path.glob("발송현황_*.xlsx"):
        match = re.fullmatch(r"발송현황_(\d{8})\.xlsx", path.name)
        if match:
            dated_sources.append((match.group(1), path))

    if dated_sources:
        return max(dated_sources, key=lambda item: item[0])[1]
    return raw_data_path / "발송현황.xlsx"


def main():
    project_root = PROJECT_ROOT
    path = resolve_source_path(project_root)
    
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
        column_map = build_stats_column_map(rows[0], data_rows)
        households = defaultdict(list)
        
        for row in data_rows:
            bonbun = cell_value(row, column_map, "bonbun")
            dong = cell_value(row, column_map, "dong")
            ho = cell_value(row, column_map, "ho")
            participation = cell_value(row, column_map, "participation")
            is_shared = "공유 O" in cell_value(row, column_map, "shared")
            submission = effective_submission(row, column_map)
            if not any([bonbun, dong, ho, participation, submission]):
                continue
            
            households[(bonbun, dong, ho)].append({
                "participation": participation,
                "is_shared": is_shared,
                "submission": submission,
                "dong": dong or "기타"
            })

        def create_stat_structure():
            return {
                "total_households": 0,
                "full_done_households": 0,
                "partial_done_households": 0,
                "not_done_households": 0,
                "privacy_needed_households": 0,
                "sent_households": 0,
                "viewed_households": 0,
                "reserved_households": 0,
                "shared_households": 0,
                "single_households": 0,
                "privacy_needed_members": 0,
                "sent_members": 0,
                "viewed_members": 0,
                "reserved_members": 0,
                "done_members": 0,
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
            member_statuses = [m["participation"] for m in members]
            done_members = [m for m in members if m["participation"] == DONE_STATUS]
            has_privacy_needed = any(status == PRIVACY_NEEDED_STATUS for status in member_statuses)
            has_sent = any(status == SENT_STATUS for status in member_statuses)
            has_viewed = any(status == VIEWED_STATUS for status in member_statuses)
            has_reserved = any(status == RESERVED_STATUS for status in member_statuses)
            
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
                if has_privacy_needed: s["privacy_needed_households"] += 1
                if has_sent: s["sent_households"] += 1
                if has_viewed: s["viewed_households"] += 1
                if has_reserved: s["reserved_households"] += 1
                
                # Dong stats
                dong_key = members[0]["dong"]
                s["dong_stats"][dong_key]["total"] += 1
                if status == "전원완료":
                    s["dong_stats"][dong_key]["done"] += 1

                for m in members:
                    participation = m["participation"]
                    s["participation_details"][display_participation_label(participation)] += 1
                    s["submission_details"][m["submission"]] += 1
                    if participation == PRIVACY_NEEDED_STATUS:
                        s["privacy_needed_members"] += 1
                    elif participation == SENT_STATUS:
                        s["sent_members"] += 1
                    elif participation == VIEWED_STATUS:
                        s["viewed_members"] += 1
                    elif participation == RESERVED_STATUS:
                        s["reserved_members"] += 1
                    elif participation == DONE_STATUS:
                        s["done_members"] += 1

        def finalize(cat_data):
            count = cat_data["total_households"]
            # Sort dongs numerically or alphabetically
            sorted_dongs = sorted(cat_data["dong_stats"].keys(), key=sort_dong_key)
            dong_list = []
            for d in sorted_dongs:
                d_total = cat_data["dong_stats"][d]["total"]
                d_done = cat_data["dong_stats"][d]["done"]
                dong_list.append({
                    "label": display_dong_label(d),
                    "total": d_total,
                    "done": d_done,
                    "rate": round((d_done / d_total * 100), 1) if d_total > 0 else 0
                })

            return {
                "count": count,
                "full_done_count": cat_data["full_done_households"],
                "full_done_rate": round((cat_data["full_done_households"] / count * 100), 1) if count > 0 else 0,
                "partial_done_count": cat_data["partial_done_households"],
                "remaining_household_count": count - cat_data["full_done_households"],
                "privacy_needed_household_count": cat_data["privacy_needed_households"],
                "privacy_needed_member_count": cat_data["privacy_needed_members"],
                "sent_household_count": cat_data["sent_households"],
                "sent_member_count": cat_data["sent_members"],
                "viewed_household_count": cat_data["viewed_households"],
                "viewed_member_count": cat_data["viewed_members"],
                "reserved_household_count": cat_data["reserved_households"],
                "reserved_member_count": cat_data["reserved_members"],
                "done_member_count": cat_data["done_members"],
                "shared_count": cat_data["shared_households"],
                "single_count": cat_data["single_households"],
                "household_stats": [
                    {"label": "전원 완료 세대", "value": cat_data["full_done_households"]},
                    {"label": "일부 완료 세대", "value": cat_data["partial_done_households"]},
                    {"label": "미완료 세대", "value": cat_data["not_done_households"]}
                ],
                "owner_type_stats": [
                    {"label": "단독 소유 세대", "value": cat_data["single_households"]},
                    {"label": "공동 소유 세대", "value": cat_data["shared_households"]}
                ],
                "followup_details": [
                    {
                        "label": "1차 개인정보 동의 독려",
                        "value": cat_data["privacy_needed_members"],
                        "unit": "명",
                        "sub": f"{cat_data['privacy_needed_households']}세대 포함",
                    },
                    {
                        "label": "발송 후 미열람 리마인드",
                        "value": cat_data["sent_members"],
                        "unit": "명",
                        "sub": f"{cat_data['sent_households']}세대 포함",
                    },
                    {
                        "label": "열람 후 미완료 안내",
                        "value": cat_data["viewed_members"],
                        "unit": "명",
                        "sub": f"{cat_data['viewed_households']}세대 포함",
                    },
                    {
                        "label": "일부 완료 공유세대 추가 확인",
                        "value": cat_data["partial_done_households"],
                        "unit": "세대",
                        "sub": "전원 완료 전환 가능 세대",
                    },
                    {
                        "label": "예약 상태 확인",
                        "value": cat_data["reserved_members"],
                        "unit": "명",
                        "sub": f"{cat_data['reserved_households']}세대 포함",
                    },
                ],
                "participation_details": sorted([{"label": k, "value": v} for k, v in cat_data["participation_details"].items()], key=lambda x: x["value"], reverse=True),
                "submission_details": sorted([{"label": k, "value": v} for k, v in cat_data["submission_details"].items()], key=lambda x: x["value"], reverse=True),
                "dong_stats": dong_list
            }

        raw_stats = {
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source_file": Path(path).name,
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
