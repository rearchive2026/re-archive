#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

if load_dotenv:
    load_dotenv()


DEFAULT_SOURCE = Path("raw_data/verification_records.csv")
DEFAULT_ENCRYPTED = Path("raw_data/verification_records.csv.enc")
DEFAULT_DECRYPTED = Path("raw_data/verification_records.decrypted.csv")


def load_key(raw_key):
    key = str(raw_key or "").strip()
    if not key:
        raise SystemExit(
            "CSV 암호화 키가 필요합니다. --key 또는 CSV_ENCRYPTION_KEY로 전달하세요."
        )
    try:
        Fernet(key.encode("utf-8"))
    except Exception as exc:
        raise SystemExit(
            "CSV 암호화 키 형식이 올바르지 않습니다. "
            "`python3 scripts/crypt_verification_csv.py generate-key`로 새 키를 만드세요."
        ) from exc
    return key.encode("utf-8")


def encrypt_file(source_path, output_path, key):
    if not source_path.exists():
        raise SystemExit(f"원본 CSV 파일을 찾을 수 없습니다: {source_path}")

    plaintext = source_path.read_bytes()
    token = Fernet(key).encrypt(plaintext)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(token)
    print(f"Encrypted: {source_path} -> {output_path}")


def decrypt_file(source_path, output_path, key):
    if not source_path.exists():
        raise SystemExit(f"암호화 파일을 찾을 수 없습니다: {source_path}")

    token = source_path.read_bytes()
    try:
        plaintext = Fernet(key).decrypt(token)
    except InvalidToken as exc:
        raise SystemExit("복호화 실패: 키가 다르거나 파일이 손상되었습니다.") from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(plaintext)
    print(f"Decrypted: {source_path} -> {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Encrypt or decrypt the verification source CSV."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("generate-key", help="Generate a new CSV encryption key.")

    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt source CSV.")
    encrypt_parser.add_argument("--input", default=DEFAULT_SOURCE, type=Path)
    encrypt_parser.add_argument("--output", default=DEFAULT_ENCRYPTED, type=Path)
    encrypt_parser.add_argument("--key", default=os.getenv("CSV_ENCRYPTION_KEY"))

    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt encrypted CSV.")
    decrypt_parser.add_argument("--input", default=DEFAULT_ENCRYPTED, type=Path)
    decrypt_parser.add_argument("--output", default=DEFAULT_DECRYPTED, type=Path)
    decrypt_parser.add_argument("--key", default=os.getenv("CSV_ENCRYPTION_KEY"))

    return parser.parse_args()


def main():
    args = parse_args()

    if args.command == "generate-key":
        print(Fernet.generate_key().decode("utf-8"))
        return

    key = load_key(args.key)

    if args.command == "encrypt":
        encrypt_file(args.input, args.output, key)
    elif args.command == "decrypt":
        decrypt_file(args.input, args.output, key)


if __name__ == "__main__":
    main()
