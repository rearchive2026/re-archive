import hashlib
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from cryptography.fernet import Fernet


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts import crypt_verification_csv as crypt_csv
from scripts import generate_verification_data as verification


CSV_HEADER = "동,호수,이름,전화번호 뒷자리,상태,url\n"


def sha256_hex(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def record(**overrides):
    row = {
        "동": "00101",
        "호수": "0301",
        "이름": " 김 민준 ",
        "전화번호 뒷자리": "4821",
        "상태": "대상",
        "url": "https://sign.example.com/verify/topkn/101-301",
    }
    row.update(overrides)
    return row


class VerificationDataTests(unittest.TestCase):
    def test_normalize_record_uses_shared_hash_input_format(self):
        row = record(이름="김 민 준")
        row["전화번호 뒷자리"] = "4821"

        self.assertEqual(verification.normalize_record(row), "101|301|김민준|4821")

    def test_phone_last4_is_left_padded_when_leading_zero_was_lost(self):
        row = record()
        row["전화번호 뒷자리"] = "549"

        self.assertEqual(verification.normalize_record(row), "101|301|김민준|0549")

    def test_build_payload_exposes_hash_status_and_url_per_record(self):
        payload = verification.build_payload([record()], "5923575768")

        self.assertEqual(payload["hashAlgorithm"], "SHA-256")
        self.assertEqual(payload["passwordHash"], sha256_hex("5923575768"))
        self.assertEqual(
            payload["records"],
            [
                {
                    "hash": sha256_hex("101|301|김민준|4821"),
                    "status": "대상",
                    "url": "https://sign.example.com/verify/topkn/101-301",
                }
            ],
        )
        self.assertNotIn("이름", payload["records"][0])
        self.assertNotIn("동", payload["records"][0])
        self.assertNotIn("호수", payload["records"][0])
        self.assertNotIn("전화번호 뒷자리", payload["records"][0])

    def test_build_payload_rejects_empty_status(self):
        with self.assertRaises(SystemExit) as context:
            verification.build_payload([record(상태="")], "5923575768")

        self.assertIn("상태가 비어 있습니다", str(context.exception))

    def test_build_payload_rejects_duplicate_normalized_records(self):
        rows = [
            record(),
            record(동="101", 호수="301", 이름="김민준"),
        ]

        with self.assertRaises(SystemExit) as context:
            verification.build_payload(rows, "5923575768")

        self.assertIn("중복된 인증 정보", str(context.exception))

    def test_build_payload_rejects_invalid_url(self):
        with self.assertRaises(SystemExit) as context:
            verification.build_payload([record(url="javascript:alert(1)")], "5923575768")

        self.assertIn("url은 http:// 또는 https://로 시작", str(context.exception))


class VerificationCsvCryptoTests(unittest.TestCase):
    def test_encrypt_and_decrypt_file_round_trip(self):
        key = Fernet.generate_key()
        source_text = CSV_HEADER + (
            "101,301,김민준,4821,대상,https://sign.example.com/verify/topkn/101-301\n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_path = temp_path / "verification_records.csv"
            encrypted_path = temp_path / "verification_records.csv.enc"
            decrypted_path = temp_path / "verification_records.decrypted.csv"
            source_path.write_text(source_text, encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                crypt_csv.encrypt_file(source_path, encrypted_path, key)
                crypt_csv.decrypt_file(encrypted_path, decrypted_path, key)

            self.assertNotEqual(encrypted_path.read_bytes(), source_path.read_bytes())
            self.assertEqual(decrypted_path.read_text(encoding="utf-8"), source_text)

    def test_generate_data_can_read_encrypted_csv_without_decrypted_file(self):
        key = Fernet.generate_key()
        source_text = CSV_HEADER + (
            "00101,0301,김 민준,4821,대상,https://sign.example.com/verify/topkn/101-301\n"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            source_path = temp_path / "verification_records.csv"
            encrypted_path = temp_path / "verification_records.csv.enc"
            source_path.write_text(source_text, encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                crypt_csv.encrypt_file(source_path, encrypted_path, key)
            rows = verification.load_encrypted_rows(encrypted_path, key.decode("utf-8"))
            payload = verification.build_payload(rows, "5923575768")

            self.assertEqual(len(rows), 1)
            self.assertFalse((temp_path / "verification_records.decrypted.csv").exists())
            self.assertEqual(
                payload["records"][0],
                {
                    "hash": sha256_hex("101|301|김민준|4821"),
                    "status": "대상",
                    "url": "https://sign.example.com/verify/topkn/101-301",
                },
            )


if __name__ == "__main__":
    unittest.main()
