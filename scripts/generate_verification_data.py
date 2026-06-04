#!/usr/bin/env python3
import argparse
import csv
import hashlib
import io
import json
import os
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()


REQUIRED_COLUMNS = ["동", "호수", "이름", "전화번호 뒷자리", "상태", "url"]
DEFAULT_PHONE_MISSING_URL = "https://www.naver.com"
QR_REQUIRED_STATUSES = {"대상", "개인정보동의필요"}


def sha256_hex(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize_number(value):
    normalized = re.sub(r"\s+", "", str(value or ""))
    normalized = normalized.lstrip("0")
    return normalized or "0"


def normalize_name(value):
    return re.sub(r"\s+", "", str(value or "").strip())


def normalize_phone_last4(value):
    digits = re.sub(r"\D+", "", str(value or ""))
    if not digits:
        return None
    if len(digits) > 4:
        raise ValueError("전화번호 뒷자리는 4자리 이하여야 합니다.")
    return digits.zfill(4)


def normalize_identity(row):
    dong = normalize_number(row["동"])
    ho = normalize_number(row["호수"])
    name = normalize_name(row["이름"])

    if not name:
        raise ValueError("이름이 비어 있습니다.")

    return "|".join([dong, ho, name])


def normalize_record(row):
    identity = normalize_identity(row)
    phone_last4 = normalize_phone_last4(row["전화번호 뒷자리"])
    if not phone_last4:
        return None

    return "|".join([identity, phone_last4])


def validate_url(value, required=True):
    url = str(value or "").strip()
    if not url and not required:
        return ""
    if not url.startswith(("https://", "http://")):
        raise ValueError("url은 http:// 또는 https://로 시작해야 합니다.")
    return url


def load_rows(csv_path):
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        return read_rows(csv_file)


def load_encrypted_rows(csv_path, key):
    try:
        from cryptography.fernet import Fernet, InvalidToken
    except ImportError as exc:
        raise SystemExit(
            "암호화 CSV를 읽으려면 cryptography 패키지가 필요합니다. "
            "`pip install -r requirements.txt`를 실행하세요."
        ) from exc

    if not key:
        raise SystemExit(
            "암호화 CSV 키가 필요합니다. --csv-key 또는 CSV_ENCRYPTION_KEY로 전달하세요."
        )

    try:
        plaintext = Fernet(str(key).strip().encode("utf-8")).decrypt(csv_path.read_bytes())
    except InvalidToken as exc:
        raise SystemExit("암호화 CSV 복호화 실패: 키가 다르거나 파일이 손상되었습니다.") from exc

    csv_file = io.StringIO(plaintext.decode("utf-8-sig"), newline="")
    return read_rows(csv_file)


def read_rows(csv_file):
    reader = csv.DictReader(csv_file)
    if reader.fieldnames != REQUIRED_COLUMNS:
        raise SystemExit(
            "CSV 헤더가 올바르지 않습니다.\n"
            f"expected: {','.join(REQUIRED_COLUMNS)}\n"
            f"actual: {','.join(reader.fieldnames or [])}"
        )
    return list(reader)


def build_payload(rows, admin_password=None, phone_missing_url=DEFAULT_PHONE_MISSING_URL):
    records = []
    seen_hashes = {}
    seen_identity_hashes = {}
    phone_missing_url = validate_url(phone_missing_url)

    for row_number, row in enumerate(rows, start=2):
        try:
            identity_hash_input = normalize_identity(row)
            identity_hash = sha256_hex(identity_hash_input)
            hash_input = normalize_record(row)
            record_hash = sha256_hex(hash_input) if hash_input else None
            status = str(row["상태"] or "").strip()
            url = validate_url(row["url"], required=status in QR_REQUIRED_STATUSES)
        except ValueError as exc:
            raise SystemExit(f"CSV {row_number}행 오류: {exc}") from exc

        if not status:
            raise SystemExit(f"CSV {row_number}행 오류: 상태가 비어 있습니다.")

        if record_hash:
            if record_hash in seen_hashes:
                raise SystemExit(
                    f"CSV {row_number}행 오류: 중복된 인증 정보입니다. "
                    f"이전 행: {seen_hashes[record_hash]}"
                )
            seen_hashes[record_hash] = row_number

        if identity_hash in seen_identity_hashes:
            raise SystemExit(
                f"CSV {row_number}행 오류: 중복된 동/호수/이름 정보입니다. "
                f"이전 행: {seen_identity_hashes[identity_hash]}"
            )
        seen_identity_hashes[identity_hash] = row_number

        public_record = {
            "identityHash": identity_hash,
            "status": status,
            "url": url,
        }
        if record_hash:
            public_record["hash"] = record_hash
        else:
            public_record["phoneMissing"] = True

        records.append(public_record)

    generated_at = datetime.now(ZoneInfo("Asia/Seoul")).isoformat(timespec="seconds")

    return {
        "version": 1,
        "generatedAt": generated_at,
        "hashAlgorithm": "SHA-256",
        "phoneMissingUrl": phone_missing_url,
        "normalization": {
            "fields": ["동", "호수", "이름", "전화번호 뒷자리"],
            "separator": "|",
            "dong": "remove whitespace and leading zeros",
            "ho": "remove whitespace and leading zeros",
            "name": "trim and remove all whitespace",
            "phoneLast4": "digits only, left-pad to 4 digits",
            "identityHash": "SHA-256 of dong|ho|name",
            "hash": "SHA-256 of dong|ho|name|phoneLast4",
            "phoneMissing": "records without phoneLast4 have no full hash",
        },
        "records": records,
    }


def parse_args():
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Generate public verification hash data from raw CSV records."
    )
    parser.add_argument(
        "--input",
        default=repo_root / "raw_data" / "verification_records.csv",
        type=Path,
        help="Source CSV path.",
    )
    parser.add_argument(
        "--encrypted-input",
        type=Path,
        help="Encrypted source CSV path. When provided, --input is ignored.",
    )
    parser.add_argument(
        "--output",
        default=repo_root / "assets" / "data" / "verification-data.json",
        type=Path,
        help="Public JSON output path.",
    )
    parser.add_argument(
        "--admin-password",
        help="Legacy option kept for old commands. It is no longer used.",
    )
    parser.add_argument(
        "--password-hash",
        help="Legacy option kept for old commands. It is no longer used.",
    )
    parser.add_argument(
        "--csv-key",
        default=os.getenv("CSV_ENCRYPTION_KEY"),
        help="Encryption key for --encrypted-input. Can also be provided by CSV_ENCRYPTION_KEY.",
    )
    parser.add_argument(
        "--phone-missing-url",
        default=os.getenv("PHONE_MISSING_URL", DEFAULT_PHONE_MISSING_URL),
        help="QR URL used when a matched owner record has no phone number.",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if args.encrypted_input:
        rows = load_encrypted_rows(args.encrypted_input, args.csv_key)
    else:
        rows = load_rows(args.input)
    payload = build_payload(rows, phone_missing_url=args.phone_missing_url)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, ensure_ascii=False, indent=2)
        output_file.write("\n")

    print(f"Generated {len(payload['records'])} records: {args.output}")


if __name__ == "__main__":
    main()
