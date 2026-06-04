import hashlib
import io
import sys
import tempfile
import unittest
import zipfile
from contextlib import redirect_stdout
from pathlib import Path
from xml.sax.saxutils import escape

from cryptography.fernet import Fernet


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from scripts import crypt_verification_csv as crypt_csv
from scripts import generate_verification_data as verification
from scripts import import_verification_xlsx as import_xlsx


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


def cell_ref(column_index, row_index):
    letters = ""
    column = column_index + 1
    while column:
        column, remainder = divmod(column - 1, 26)
        letters = chr(ord("A") + remainder) + letters
    return f"{letters}{row_index}"


def write_minimal_xlsx(path, rows):
    sheet_rows = []
    for row_index, row in enumerate(rows, start=1):
        cells = []
        for column_index, value in enumerate(row):
            ref = cell_ref(column_index, row_index)
            cells.append(
                f'<c r="{ref}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'
            )
        sheet_rows.append(f'<row r="{row_index}">{"".join(cells)}</row>')

    worksheet = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
        f'<sheetData>{"".join(sheet_rows)}</sheetData>'
        "</worksheet>"
    )

    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
            '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
            "</Types>",
        )
        archive.writestr(
            "xl/workbook.xml",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
            'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
            '<sheets><sheet name="Sheet1" sheetId="1" r:id="rId1"/></sheets>'
            "</workbook>",
        )
        archive.writestr(
            "xl/_rels/workbook.xml.rels",
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
            "</Relationships>",
        )
        archive.writestr("xl/worksheets/sheet1.xml", worksheet)


class VerificationXlsxImportTests(unittest.TestCase):
    def test_build_verification_rows_splits_multi_ho_and_marks_sent_completed_as_done(self):
        rows = [
            {
                "이름": "테스트소유주",
                "동(단지)": "101",
                "호수": "104, 105",
                "QR 업데이트 여부": "X",
                "연락처 뒷자리": "6316",
                "동의서 발송상태": "발송",
                "동의서 참여상태": "완료",
                "동의서 url": "https://sign.example.com/privacy/101-104",
            }
        ]

        self.assertEqual(
            import_xlsx.build_verification_rows(rows),
            [
                {
                    "동": "101",
                    "호수": "104",
                    "이름": "테스트소유주",
                    "전화번호 뒷자리": "6316",
                    "상태": "완료",
                    "url": "https://sign.example.com/privacy/101-104",
                },
                {
                    "동": "101",
                    "호수": "105",
                    "이름": "테스트소유주",
                    "전화번호 뒷자리": "6316",
                    "상태": "완료",
                    "url": "https://sign.example.com/privacy/101-104",
                },
            ],
        )

    def test_build_verification_rows_marks_sent_unfinished_agreement_as_target(self):
        rows = [
            {
                "이름": "김민준",
                "동(단지)": "101",
                "호수": "301",
                "QR 업데이트 여부": "O",
                "연락처 뒷자리": "4821",
                "동의서 발송상태": "발송",
                "동의서 참여상태": "열람",
                "동의서 url": "https://sign.example.com/verify/topkn/101-301",
            }
        ]

        self.assertEqual(import_xlsx.build_verification_rows(rows)[0]["상태"], "대상")

    def test_build_verification_rows_treats_manual_privacy_consent_as_ready(self):
        rows = [
            {
                "이름": "김민준",
                "동(단지)": "101",
                "호수": "301",
                "QR 업데이트 여부": "X",
                "연락처 뒷자리": "4821",
                "동의서 발송상태": "동의",
                "동의서 참여상태": "열람",
                "동의서 url": "https://sign.example.com/verify/topkn/101-301",
            }
        ]

        self.assertEqual(import_xlsx.build_verification_rows(rows)[0]["상태"], "대상")

    def test_build_verification_rows_treats_sent_status_as_manual_privacy_consent(self):
        rows = [
            {
                "이름": "다필지소유주",
                "동(단지)": "101",
                "호수": "106, 107",
                "QR 업데이트 여부": "X",
                "연락처 뒷자리": "0181",
                "동의서 발송상태": "발송",
                "동의서 참여상태": "완료",
                "동의서 url": "https://sign.example.com/verify/topkn/101-106",
            }
        ]

        verification_rows = import_xlsx.build_verification_rows(rows)

        self.assertEqual([row["호수"] for row in verification_rows], ["106", "107"])
        self.assertEqual([row["상태"] for row in verification_rows], ["완료", "완료"])

    def test_build_verification_rows_marks_manual_privacy_completed_as_done(self):
        rows = [
            {
                "이름": "김민준",
                "동(단지)": "101",
                "호수": "301",
                "QR 업데이트 여부": "X",
                "연락처 뒷자리": "4821",
                "동의서 발송상태": "동의",
                "동의서 참여상태": "완료",
                "동의서 url": "https://sign.example.com/verify/topkn/101-301",
            }
        ]

        self.assertEqual(import_xlsx.build_verification_rows(rows)[0]["상태"], "완료")

    def test_build_verification_rows_marks_sent_completed_agreement_as_done(self):
        rows = [
            {
                "이름": "김민준",
                "동(단지)": "101",
                "호수": "301",
                "QR 업데이트 여부": "O",
                "연락처 뒷자리": "4821",
                "동의서 발송상태": "발송",
                "동의서 참여상태": "완료",
                "동의서 url": "https://sign.example.com/verify/topkn/101-301",
            }
        ]

        self.assertEqual(import_xlsx.build_verification_rows(rows)[0]["상태"], "완료")

    def test_build_verification_rows_treats_viewed_participation_as_target(self):
        rows = [
            {
                "이름": "김민준",
                "동(단지)": "101",
                "호수": "301",
                "QR 업데이트 여부": "X",
                "연락처 뒷자리": "4821",
                "동의서 발송상태": "",
                "동의서 참여상태": "열람",
                "동의서 url": "https://sign.example.com/verify/topkn/101-301",
            }
        ]

        self.assertEqual(import_xlsx.build_verification_rows(rows)[0]["상태"], "대상")

    def test_build_verification_rows_treats_completed_participation_as_done(self):
        rows = [
            {
                "이름": "김민준",
                "동(단지)": "101",
                "호수": "301",
                "QR 업데이트 여부": "X",
                "연락처 뒷자리": "4821",
                "동의서 발송상태": "",
                "동의서 참여상태": "완료",
                "동의서 url": "",
            }
        ]

        verification_row = import_xlsx.build_verification_rows(rows)[0]

        self.assertEqual(verification_row["상태"], "완료")
        self.assertEqual(verification_row["url"], "")

    def test_build_verification_rows_uses_privacy_fallback_when_not_registered(self):
        rows = [
            {
                "이름": "김민준",
                "동(단지)": "101",
                "호수": "301",
                "QR 업데이트 여부": "X",
                "연락처 뒷자리": "4821",
                "동의서 발송상태": "",
                "동의서 참여상태": "",
                "동의서 url": "",
            }
        ]

        verification_rows = import_xlsx.build_verification_rows(
            rows,
            privacy_consent_url="https://sign.example.com/privacy/101-301",
        )

        self.assertEqual(verification_rows[0]["상태"], "개인정보동의필요")
        self.assertEqual(
            verification_rows[0]["url"],
            "https://sign.example.com/privacy/101-301",
        )

    def test_build_verification_rows_allows_completed_agreement_without_url(self):
        rows = [
            {
                "이름": "김민준",
                "동(단지)": "101",
                "호수": "301",
                "QR 업데이트 여부": "O",
                "연락처 뒷자리": "4821",
                "동의서 발송상태": "발송",
                "동의서 참여상태": "완료",
                "동의서 url": "",
            }
        ]

        verification_row = import_xlsx.build_verification_rows(rows)[0]

        self.assertEqual(verification_row["상태"], "완료")
        self.assertEqual(verification_row["url"], "")

    def test_build_verification_rows_allows_qr_updated_unsent_without_url_as_hold(self):
        rows = [
            {
                "이름": "김민준",
                "동(단지)": "101",
                "호수": "301",
                "QR 업데이트 여부": "O",
                "연락처 뒷자리": "4821",
                "동의서 발송상태": "",
                "동의서 참여상태": "",
                "동의서 url": "",
            }
        ]

        verification_row = import_xlsx.build_verification_rows(rows)[0]

        self.assertEqual(verification_row["상태"], "보류")
        self.assertEqual(verification_row["url"], "")

    def test_build_verification_rows_rejects_sent_unfinished_without_agreement_url(self):
        rows = [
            {
                "이름": "김민준",
                "동(단지)": "101",
                "호수": "301",
                "QR 업데이트 여부": "O",
                "연락처 뒷자리": "4821",
                "동의서 발송상태": "발송",
                "동의서 참여상태": "열람",
                "동의서 url": "",
            }
        ]

        with self.assertRaises(SystemExit) as context:
            import_xlsx.build_verification_rows(rows)

        self.assertIn("동의서 url이 비어 있습니다", str(context.exception))

    def test_load_xlsx_rows_trims_headers_and_builds_verification_rows(self):
        rows = [
            [
                "이름",
                "생년월일",
                "성별",
                "동(단지)",
                "호수",
                "공유여부",
                "다필지여부",
                "연락처 뒷자리",
                "QR 업데이트 여부",
                "동의서 발송상태",
                "동의서 참여상태",
                "동의서 url ",
            ],
            [
                "샘플소유주",
                "19990125",
                "남",
                "101",
                "106, 107",
                "X",
                "O",
                "0181",
                "x",
                "발송",
                "열람",
                "https://sign.example.com/privacy/101-106",
            ],
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.xlsx"
            write_minimal_xlsx(path, rows)

            source_rows = import_xlsx.rows_to_dicts(import_xlsx.load_xlsx_rows(path))
            verification_rows = import_xlsx.build_verification_rows(source_rows)

        self.assertEqual(len(verification_rows), 2)
        self.assertEqual(verification_rows[0]["호수"], "106")
        self.assertEqual(verification_rows[1]["호수"], "107")
        self.assertEqual(verification_rows[0]["전화번호 뒷자리"], "0181")
        self.assertEqual(verification_rows[0]["상태"], "대상")


class VerificationDataTests(unittest.TestCase):
    def test_normalize_record_uses_shared_hash_input_format(self):
        row = record(이름="김 민 준")
        row["전화번호 뒷자리"] = "4821"

        self.assertEqual(verification.normalize_identity(row), "101|301|김민준")
        self.assertEqual(verification.normalize_record(row), "101|301|김민준|4821")

    def test_phone_last4_is_left_padded_when_leading_zero_was_lost(self):
        row = record()
        row["전화번호 뒷자리"] = "549"

        self.assertEqual(verification.normalize_record(row), "101|301|김민준|0549")

    def test_build_payload_exposes_hash_status_and_url_per_record(self):
        payload = verification.build_payload([record()], "5923575768")

        self.assertEqual(payload["hashAlgorithm"], "SHA-256")
        self.assertEqual(payload["phoneMissingUrl"], "https://www.naver.com")
        self.assertNotIn("passwordHash", payload)
        self.assertEqual(
            payload["records"],
            [
                {
                    "identityHash": sha256_hex("101|301|김민준"),
                    "status": "대상",
                    "url": "https://sign.example.com/verify/topkn/101-301",
                    "hash": sha256_hex("101|301|김민준|4821"),
                }
            ],
        )
        self.assertNotIn("이름", payload["records"][0])
        self.assertNotIn("동", payload["records"][0])
        self.assertNotIn("호수", payload["records"][0])
        self.assertNotIn("전화번호 뒷자리", payload["records"][0])

    def test_build_payload_marks_records_without_phone(self):
        row = record()
        row["전화번호 뒷자리"] = ""
        payload = verification.build_payload([row], "5923575768")

        self.assertEqual(
            payload["records"],
            [
                {
                    "identityHash": sha256_hex("101|301|김민준"),
                    "status": "대상",
                    "url": "https://sign.example.com/verify/topkn/101-301",
                    "phoneMissing": True,
                }
            ],
        )
        self.assertNotIn("hash", payload["records"][0])

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

    def test_build_payload_rejects_duplicate_identity_records(self):
        rows = [
            record(),
            record(),
        ]
        rows[1]["전화번호 뒷자리"] = "9154"

        with self.assertRaises(SystemExit) as context:
            verification.build_payload(rows, "5923575768")

        self.assertIn("중복된 동/호수/이름 정보", str(context.exception))

    def test_build_payload_rejects_invalid_url(self):
        with self.assertRaises(SystemExit) as context:
            verification.build_payload([record(url="javascript:alert(1)")], "5923575768")

        self.assertIn("url은 http:// 또는 https://로 시작", str(context.exception))

    def test_build_payload_rejects_empty_url_for_qr_required_status(self):
        with self.assertRaises(SystemExit) as context:
            verification.build_payload([record(url="")], "5923575768")

        self.assertIn("url은 http:// 또는 https://로 시작", str(context.exception))

    def test_build_payload_allows_empty_url_for_non_qr_status(self):
        payload = verification.build_payload(
            [record(상태="완료", url="")],
            "5923575768",
        )

        self.assertEqual(payload["records"][0]["status"], "완료")
        self.assertEqual(payload["records"][0]["url"], "")


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
                    "identityHash": sha256_hex("101|301|김민준"),
                    "status": "대상",
                    "url": "https://sign.example.com/verify/topkn/101-301",
                },
            )


if __name__ == "__main__":
    unittest.main()
