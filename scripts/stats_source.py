import re
from collections import defaultdict


FIELD_HEADERS = {
    "bonbun": ["본번"],
    "dong": ["동"],
    "ho": ["호수"],
    "shared": ["공유여부"],
    "submission": ["제출형태"],
    "participation": ["참여상태"],
}
OPTIONAL_FIELD_HEADERS = {
    "memo": ["메모"],
}
WRITTEN_CONSENT_MEMO_TEXT = "서면동의"


def normalize_header(value):
    return re.sub(r"\s+", "", str(value or ""))


def normalize_cell(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return str(value).strip()
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def excel_number_if_possible(value):
    text = normalize_cell(value)
    if re.fullmatch(r"\d+", text):
        return int(text)
    return text


def cell_value(row, column_map, field):
    if field not in column_map:
        return ""
    index = column_map[field]
    if index >= len(row):
        return ""
    return normalize_cell(row[index])


def build_column_candidates(header):
    candidates = defaultdict(list)
    for index, value in enumerate(header):
        normalized = normalize_header(value)
        if normalized:
            candidates[normalized].append(index)
    return candidates


def nonblank_count(rows, index):
    return sum(1 for row in rows if index < len(row) and normalize_cell(row[index]))


def pick_column(header, rows, header_names):
    candidates_by_header = build_column_candidates(header)
    candidates = []
    for name in header_names:
        candidates.extend(candidates_by_header.get(normalize_header(name), []))

    if not candidates:
        return None

    return max(candidates, key=lambda index: (nonblank_count(rows, index), index))


def build_stats_column_map(header, rows):
    column_map = {}
    missing = []
    for field, header_names in FIELD_HEADERS.items():
        index = pick_column(header, rows, header_names)
        if index is None:
            missing.append(header_names[0])
        else:
            column_map[field] = index

    if missing:
        raise ValueError(f"통계 생성 필수 컬럼이 없습니다: {', '.join(missing)}")

    for field, header_names in OPTIONAL_FIELD_HEADERS.items():
        index = pick_column(header, rows, header_names)
        if index is not None:
            column_map[field] = index
    return column_map


def has_written_consent_text(value):
    return WRITTEN_CONSENT_MEMO_TEXT in normalize_header(value)


def has_written_consent_memo(row, column_map):
    return has_written_consent_text(cell_value(row, column_map, "memo"))


def final_submission(row, column_map):
    if has_written_consent_memo(row, column_map):
        return "서면"
    return cell_value(row, column_map, "submission") or "미제출"


def effective_submission(row, column_map):
    return final_submission(row, column_map)


def row_with_effective_submission(row, column_map):
    output = list(row)
    submission_index = column_map.get("submission")
    if submission_index is None:
        return output
    while len(output) <= submission_index:
        output.append(None)
    output[submission_index] = effective_submission(row, column_map)
    return output


def row_with_excel_numeric_dong_ho(row, column_map):
    output = list(row)
    for field in ("dong", "ho"):
        index = column_map.get(field)
        if index is None:
            continue
        while len(output) <= index:
            output.append(None)
        output[index] = excel_number_if_possible(output[index])
    return output


def display_dong_label(dong):
    if dong == "기타":
        return "기타"
    if str(dong).endswith("동"):
        return str(dong)
    return f"{dong}동"


def sort_dong_key(dong):
    text = str(dong)
    return (text != "기타", not text.isdigit(), int(text) if text.isdigit() else text)
