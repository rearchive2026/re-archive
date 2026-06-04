#!/usr/bin/env python3
import argparse
import csv
import posixpath
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


XLSX_NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkg": "http://schemas.openxmlformats.org/package/2006/relationships",
}
INPUT_COLUMNS = [
    "이름",
    "동(단지)",
    "호수",
    "공유여부",
    "QR 업데이트 여부",
    "연락처 뒷자리",
    "동의서 발송상태",
    "동의서 참여상태",
    "동의서 url",
]
OUTPUT_COLUMNS = ["동", "호수", "이름", "전화번호 뒷자리", "상태", "url"]
AGREEMENT_READY_STATUS = "대상"
AGREEMENT_DONE_STATUS = "완료"
AGREEMENT_HOLD_STATUS = "보류"
AGREEMENT_VIEWED_STATUS = "열람"
PRIVACY_CONSENT_REQUIRED_STATUS = "개인정보동의필요"
MANUAL_PRIVACY_CONSENT_VALUES = {"발송", "동의", "수기동의", "개인정보동의"}
PARTICIPATION_PRIVACY_CONSENT_VALUES = {AGREEMENT_VIEWED_STATUS, AGREEMENT_DONE_STATUS}
CONSENT_TRUE_VALUES = {"O", "Y", "YES", "TRUE", "1", "동의", "완료", "예", "있음"}
CONSENT_FALSE_VALUES = {
    "",
    "X",
    "N",
    "NO",
    "FALSE",
    "0",
    "미동의",
    "미완료",
    "아니오",
    "없음",
}


def normalize_header(value):
    return str(value or "").strip()


def normalize_cell(value):
    return str(value or "").strip()


def normalize_status_flag(value):
    return re.sub(r"\s+", "", str(value or "")).upper()


def map_privacy_consent_status(value):
    normalized = normalize_status_flag(value)
    if normalized in CONSENT_TRUE_VALUES:
        return None
    if normalized in CONSENT_FALSE_VALUES:
        return PRIVACY_CONSENT_REQUIRED_STATUS
    raise ValueError(f"QR 업데이트 여부 값을 해석할 수 없습니다: {value}")


def has_privacy_consent(qr_update_status, send_status, participation_status):
    normalized_send_status = normalize_status_flag(send_status)
    if normalized_send_status in MANUAL_PRIVACY_CONSENT_VALUES:
        return True

    normalized_participation_status = normalize_status_flag(participation_status)
    if normalized_participation_status in PARTICIPATION_PRIVACY_CONSENT_VALUES:
        return True

    return map_privacy_consent_status(qr_update_status) is None


def map_agreement_status(send_status, participation_status):
    normalized_send_status = normalize_status_flag(send_status)
    normalized_participation_status = normalize_status_flag(participation_status)

    if normalized_participation_status == "완료":
        return AGREEMENT_DONE_STATUS
    if normalized_participation_status == AGREEMENT_VIEWED_STATUS:
        return AGREEMENT_READY_STATUS
    if normalized_send_status in {"발송", "동의"}:
        return AGREEMENT_READY_STATUS
    return AGREEMENT_HOLD_STATUS


def map_verification_status(source_row):
    if not has_privacy_consent(
        source_row["QR 업데이트 여부"],
        source_row["동의서 발송상태"],
        source_row["동의서 참여상태"],
    ):
        return PRIVACY_CONSENT_REQUIRED_STATUS
    return map_agreement_status(
        source_row["동의서 발송상태"],
        source_row["동의서 참여상태"],
    )


def resolve_record_url(source_url, status, privacy_consent_url):
    url = normalize_cell(source_url)
    if url:
        return url
    if status == PRIVACY_CONSENT_REQUIRED_STATUS and privacy_consent_url:
        return normalize_cell(privacy_consent_url)
    return ""


def split_ho_values(value):
    parts = [
        part.strip()
        for part in re.split(r"[,/\n]+", str(value or ""))
        if part.strip()
    ]
    if not parts:
        raise ValueError("호수가 비어 있습니다.")
    return parts


def column_index(cell_ref):
    match = re.match(r"([A-Z]+)", cell_ref or "")
    if not match:
        return None

    index = 0
    for char in match.group(1):
        index = index * 26 + ord(char) - ord("A") + 1
    return index - 1


def parse_xml(archive, path):
    return ET.fromstring(archive.read(path))


def read_shared_strings(archive):
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []

    root = parse_xml(archive, "xl/sharedStrings.xml")
    values = []
    for item in root.findall("main:si", XLSX_NS):
        values.append("".join(text.text or "" for text in item.iterfind(".//main:t", XLSX_NS)))
    return values


def worksheet_path(target):
    return posixpath.normpath(posixpath.join("xl", target.lstrip("/")))


def read_workbook_sheets(archive):
    workbook = parse_xml(archive, "xl/workbook.xml")
    relationships = parse_xml(archive, "xl/_rels/workbook.xml.rels")
    targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in relationships.findall("pkg:Relationship", XLSX_NS)
    }

    sheets = []
    for sheet in workbook.findall(".//main:sheet", XLSX_NS):
        relationship_id = sheet.attrib[
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        ]
        sheets.append(
            {
                "name": sheet.attrib["name"],
                "path": worksheet_path(targets[relationship_id]),
            }
        )
    return sheets


def read_worksheet_rows(archive, sheet_path, shared_strings):
    root = parse_xml(archive, sheet_path)
    rows = []
    for row in root.findall(".//main:sheetData/main:row", XLSX_NS):
        cells = []
        max_index = -1
        for cell in row.findall("main:c", XLSX_NS):
            index = column_index(cell.attrib.get("r"))
            if index is None:
                index = max_index + 1
            max_index = max(max_index, index)
            cells.append((index, read_cell_value(cell, shared_strings)))

        values = [None] * (max_index + 1)
        for index, value in cells:
            values[index] = value
        if any(value not in (None, "") for value in values):
            rows.append(values)
    return rows


def read_cell_value(cell, shared_strings):
    cell_type = cell.attrib.get("t")
    value = cell.find("main:v", XLSX_NS)

    if cell_type == "s" and value is not None:
        return shared_strings[int(value.text)]
    if cell_type == "inlineStr":
        inline = cell.find("main:is", XLSX_NS)
        if inline is None:
            return ""
        return "".join(text.text or "" for text in inline.iterfind(".//main:t", XLSX_NS))
    if cell_type == "b" and value is not None:
        return "TRUE" if value.text == "1" else "FALSE"
    if value is not None:
        return value.text or ""
    return ""


def load_xlsx_rows(path, sheet_name=None):
    with zipfile.ZipFile(path) as archive:
        shared_strings = read_shared_strings(archive)
        sheets = read_workbook_sheets(archive)
        if not sheets:
            raise SystemExit("엑셀 파일에 시트가 없습니다.")

        if sheet_name:
            matches = [sheet for sheet in sheets if sheet["name"] == sheet_name]
            if not matches:
                raise SystemExit(f"시트를 찾을 수 없습니다: {sheet_name}")
            sheet = matches[0]
        else:
            sheet = sheets[0]

        rows = read_worksheet_rows(archive, sheet["path"], shared_strings)

    if not rows:
        raise SystemExit("엑셀 시트에 데이터가 없습니다.")
    return rows


def rows_to_dicts(rows):
    headers = [normalize_header(value) for value in rows[0]]
    missing_columns = [column for column in INPUT_COLUMNS if column not in headers]
    if missing_columns:
        raise SystemExit(f"엑셀 필수 컬럼이 없습니다: {', '.join(missing_columns)}")

    records = []
    for row_number, row in enumerate(rows[1:], start=2):
        record = {
            header: normalize_cell(row[index] if index < len(row) else "")
            for index, header in enumerate(headers)
            if header
        }
        if any(record.get(column) for column in INPUT_COLUMNS):
            record["_row_number"] = row_number
            records.append(record)
    return records


def build_verification_rows(source_rows, privacy_consent_url=None):
    verification_rows = []
    for source_row in source_rows:
        row_number = source_row.get("_row_number", "?")
        try:
            name = normalize_cell(source_row["이름"])
            dong = normalize_cell(source_row["동(단지)"])
            phone_last4 = normalize_cell(source_row["연락처 뒷자리"])
            status = map_verification_status(source_row)
            url = resolve_record_url(
                source_row["동의서 url"],
                status,
                privacy_consent_url,
            )
            ho_values = split_ho_values(source_row["호수"])
        except ValueError as exc:
            raise SystemExit(f"엑셀 {row_number}행 오류: {exc}") from exc

        if not name:
            raise SystemExit(f"엑셀 {row_number}행 오류: 이름이 비어 있습니다.")
        if not dong:
            raise SystemExit(f"엑셀 {row_number}행 오류: 동(단지)이 비어 있습니다.")
        if status == PRIVACY_CONSENT_REQUIRED_STATUS and not url:
            raise SystemExit(
                f"엑셀 {row_number}행 오류: 개인정보 동의용 URL이 필요합니다. "
                "--privacy-consent-url로 전달하세요."
            )
        if status == AGREEMENT_READY_STATUS and not url:
            raise SystemExit(
                f"엑셀 {row_number}행 오류: 동의서 url이 비어 있습니다. "
                "2차 재건축 전자 동의 QR을 만들 수 없습니다."
            )

        for ho in ho_values:
            verification_rows.append(
                {
                    "동": dong,
                    "호수": ho,
                    "이름": name,
                    "전화번호 뒷자리": phone_last4,
                    "상태": status,
                    "url": url,
                }
            )
    return verification_rows


def write_csv(rows, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def parse_args():
    repo_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(
        description="Import verification records from local owner sample XLSX."
    )
    parser.add_argument("--input", required=True, type=Path, help="Source XLSX path.")
    parser.add_argument(
        "--output",
        default=repo_root / "raw_data" / "verification_records.csv",
        type=Path,
        help="Local-only output CSV path.",
    )
    parser.add_argument("--sheet", help="Worksheet name. Defaults to the first sheet.")
    parser.add_argument(
        "--privacy-consent-url",
        help="Fallback QR URL used when a record has no agreement URL and needs privacy consent.",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    rows = load_xlsx_rows(args.input, args.sheet)
    source_rows = rows_to_dicts(rows)
    verification_rows = build_verification_rows(source_rows, args.privacy_consent_url)
    write_csv(verification_rows, args.output)
    print(f"Imported {len(verification_rows)} records: {args.output}")


if __name__ == "__main__":
    main()
