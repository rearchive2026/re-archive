import sys
import os
import re
import openpyxl
from openpyxl.chart import BarChart, Reference
from openpyxl.styles import Alignment, Font, PatternFill, Border, Side
from collections import defaultdict
from math import ceil
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))
from import_verification_xlsx import load_xlsx_rows
from stats_source import (
    build_stats_column_map,
    cell_value,
    display_dong_label,
    effective_submission,
    row_with_effective_submission,
    sort_dong_key,
)


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


def add_summary_charts(ws_summary, dong_header_row, dong_last_row):
    complex_chart = BarChart()
    complex_chart.title = "단지별 세대 완료율"
    complex_chart.y_axis.title = "완료율"
    complex_chart.y_axis.numFmt = "0.0%"
    complex_chart.y_axis.scaling.min = 0
    complex_chart.y_axis.scaling.max = 1
    complex_chart.x_axis.title = "구분"
    complex_chart.add_data(
        Reference(ws_summary, min_col=5, min_row=2, max_row=5),
        titles_from_data=True,
    )
    complex_chart.set_categories(Reference(ws_summary, min_col=1, min_row=3, max_row=5))
    complex_chart.width = 16
    complex_chart.height = 9
    ws_summary.add_chart(complex_chart, "I1")

    dong_rate_chart = BarChart()
    dong_rate_chart.type = "bar"
    dong_rate_chart.title = "동별 세대 완료율"
    dong_rate_chart.x_axis.title = "완료율"
    dong_rate_chart.x_axis.numFmt = "0.0%"
    dong_rate_chart.x_axis.scaling.min = 0
    dong_rate_chart.x_axis.scaling.max = 1
    dong_rate_chart.y_axis.title = "동"
    dong_rate_chart.add_data(
        Reference(ws_summary, min_col=4, min_row=dong_header_row, max_row=dong_last_row),
        titles_from_data=True,
    )
    dong_rate_chart.set_categories(
        Reference(ws_summary, min_col=1, min_row=dong_header_row + 1, max_row=dong_last_row)
    )
    dong_rate_chart.width = 18
    dong_rate_chart.height = 14
    ws_summary.add_chart(dong_rate_chart, "I16")

    shortage_chart = BarChart()
    shortage_chart.type = "bar"
    shortage_chart.title = "동별 50% 달성 부족분(서면)"
    shortage_chart.x_axis.title = "부족 세대"
    shortage_chart.y_axis.title = "동"
    shortage_chart.add_data(
        Reference(ws_summary, min_col=7, min_row=dong_header_row, max_row=dong_last_row),
        titles_from_data=True,
    )
    shortage_chart.set_categories(
        Reference(ws_summary, min_col=1, min_row=dong_header_row + 1, max_row=dong_last_row)
    )
    shortage_chart.width = 18
    shortage_chart.height = 14
    ws_summary.add_chart(shortage_chart, "I38")


def normalize_row(row, width):
    return list(row) + [None] * max(0, width - len(row))


def household_key(row, column_map):
    return (
        cell_value(row, column_map, "bonbun"),
        cell_value(row, column_map, "dong"),
        cell_value(row, column_map, "ho"),
    )


def classify_apt(bonbun):
    return "경남" if bonbun in {"525", "526"} else "벽산"


def build_dashboard_rows(data_rows, header_width, column_map):
    padded_rows = [
        row_with_effective_submission(normalize_row(row, header_width), column_map)
        for row in data_rows
    ]
    household_members = defaultdict(list)
    for index, row in enumerate(padded_rows):
        household_members[household_key(row, column_map)].append(index)

    helper_by_row = []
    leader_seen = set()
    household_summaries = {}

    for key, indexes in household_members.items():
        statuses = [cell_value(padded_rows[index], column_map, "participation") for index in indexes]
        submissions = [effective_submission(padded_rows[index], column_map) for index in indexes]
        done_count = sum(status == "완료" for status in statuses)
        written_count = sum(submission == "서면" for submission in submissions)
        size = len(indexes)
        is_full_done = int(size > 0 and done_count == size)
        is_written_done = int(is_full_done and written_count == size)
        is_partial = int(0 < done_count < size)
        bonbun, dong, ho = key
        household_summaries[key] = {
            "bonbun": bonbun,
            "dong": dong or "기타",
            "ho": ho,
            "apt": classify_apt(bonbun),
            "size": size,
            "done_count": done_count,
            "written_count": written_count,
            "is_full_done": is_full_done,
            "is_written_done": is_written_done,
            "is_partial": is_partial,
        }

    for row in padded_rows:
        key = household_key(row, column_map)
        summary = household_summaries[key]
        is_leader = int(key not in leader_seen)
        leader_seen.add(key)
        is_member_done = int(cell_value(row, column_map, "participation") == "완료")
        is_member_written = int(effective_submission(row, column_map) == "서면")
        helper_by_row.append(
            [
                "_".join(key),
                is_member_done,
                is_member_written,
                summary["size"],
                summary["done_count"],
                summary["is_full_done"],
                summary["is_written_done"],
                summary["is_partial"],
                is_leader,
                summary["apt"],
            ]
        )

    return padded_rows, helper_by_row, household_summaries


def summarize_complex(padded_rows, household_summaries, column_map, apt=None):
    if apt:
        member_rows = [row for row in padded_rows if classify_apt(cell_value(row, column_map, "bonbun")) == apt]
        households = [summary for summary in household_summaries.values() if summary["apt"] == apt]
    else:
        member_rows = padded_rows
        households = list(household_summaries.values())

    member_count = len(member_rows)
    done_members = sum(cell_value(row, column_map, "participation") == "완료" for row in member_rows)
    household_count = len(households)
    full_done_count = sum(summary["is_full_done"] for summary in households)
    written_done_count = sum(summary["is_written_done"] for summary in households)
    partial_count = sum(summary["is_partial"] for summary in households)

    return {
        "member_count": member_count,
        "member_done_rate": done_members / member_count if member_count else 0,
        "household_count": household_count,
        "household_done_rate": full_done_count / household_count if household_count else 0,
        "written_done_count": written_done_count,
        "partial_count": partial_count,
    }


def summarize_dongs(household_summaries):
    grouped = defaultdict(list)
    for summary in household_summaries.values():
        grouped[summary["dong"]].append(summary)

    result = []
    for dong in sorted(grouped, key=sort_dong_key):
        households = grouped[dong]
        total = len(households)
        full_done = sum(summary["is_full_done"] for summary in households)
        written_done = sum(summary["is_written_done"] for summary in households)
        partial = sum(summary["is_partial"] for summary in households)
        shortage = max(0, ceil(total / 2) - written_done)
        result.append(
            {
                "dong": dong,
                "total": total,
                "full_done": full_done,
                "rate": full_done / total if total else 0,
                "written_done": written_done,
                "partial": partial,
                "shortage": shortage,
            }
        )
    return result


def main():
    input_path = resolve_source_path(PROJECT_ROOT)
    output_path = PROJECT_ROOT / 'raw_data' / '발송현황_실시간대시보드_최종.xlsx'
    
    if not os.path.exists(input_path):
        print(f"Error: {input_path} not found.")
        return

    try:
        rows = load_xlsx_rows(input_path)
        if not rows: return
        header = rows[0]
        data_rows = rows[1:]
        column_map = build_stats_column_map(header, data_rows)
        padded_rows, helper_rows, household_summaries = build_dashboard_rows(data_rows, len(header), column_map)

        wb = openpyxl.Workbook()
        
        # --- 1. DATA_SOURCE SHEET ---
        ws_data = wb.active
        ws_data.title = "Data_Source"
        
        # Helper Column Labels
        # U:ID, V:IndivDone, W:IndivWritten, X:HouseSize, Y:HouseDoneCount, Z:IsHouseFullDone, AA:IsHouseWritten, AB:IsHousePartial, AC:IsLeaderRow, AD:AptType
        helper_headers = ["H_세대ID", "H_인원완료(1/0)", "H_인원서면(1/0)", "H_세대원수", "H_세대내완료수", "H_세대전원완료(1/0)", "H_세대서면완료(1/0)", "H_세대일부완료(1/0)", "H_세대대표행(1/0)", "H_아파트분류"]
        full_header = list(header) + helper_headers
        ws_data.append(full_header)
        
        for row_data, helper_data in zip(padded_rows, helper_rows):
            ws_data.append(row_data + helper_data)

        # Style Source sheet
        header_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
        for c in range(len(header) + 1, len(full_header) + 1): ws_data.cell(row=1, column=c).fill = header_fill

        # --- 2. SUMMARY SHEET ---
        ws_summary = wb.create_sheet("Summary", 0)
        
        # Style Definitions
        title_font = Font(bold=True, size=16, color="002060")
        tbl_header_fill = PatternFill(start_color="DDEBF7", end_color="DDEBF7", fill_type="solid")
        border = Border(left=Side(style='thin'), right=Side(style='thin'), top=Side(style='thin'), bottom=Side(style='thin'))
        center_align = Alignment(horizontal='center', vertical='center')

        # Section 1: Complex Stats
        ws_summary.merge_cells("A1:G1")
        ws_summary["A1"] = "▶ 단지별 입체 동의 현황 (실시간 업데이트)"
        ws_summary["A1"].font = title_font
        
        s_header = ["구분", "전체 인원", "인적 동의율", "전체 세대", "세대별 완료율", "전원 서면완료", "일부 동의(미합치)"]
        ws_summary.append(s_header)
        for header_cell in ws_summary[2]:
            header_cell.font = Font(bold=True)
            header_cell.fill = tbl_header_fill
            header_cell.border = border
            header_cell.alignment = center_align

        targets = [("통합", ""), ("경남", "경남"), ("벽산", "벽산")]
        for i, (label, apt) in enumerate(targets):
            r = i + 3
            summary = summarize_complex(padded_rows, household_summaries, column_map, apt or None)

            ws_summary.cell(r, 1, label)
            ws_summary.cell(r, 2, summary["member_count"])
            ws_summary.cell(r, 3, summary["member_done_rate"]).number_format = '0.0%'
            ws_summary.cell(r, 4, summary["household_count"])
            ws_summary.cell(r, 5, summary["household_done_rate"]).number_format = '0.0%'
            ws_summary.cell(r, 6, summary["written_done_count"])
            ws_summary.cell(r, 7, summary["partial_count"])
            for c in range(1, 8): 
                ws_summary.cell(r, c).border = border
                ws_summary.cell(r, c).alignment = Alignment(horizontal='center')

        ws_summary.append([]) # Spacer

        # Section 2: Dong Stats
        ws_summary.append(["▶ 동별 상세 지표 (서면 동의 관리)"])
        ws_summary.cell(ws_summary.max_row, 1).font = title_font
        
        d_header = ["동", "전체 세대", "전원 완료 세대", "세대 완료율", "서면 완료", "일부 동의", "50% 달성 부족분(서면)"]
        ws_summary.append(d_header)
        dong_header_row = ws_summary.max_row
        for header_cell in ws_summary[ws_summary.max_row]:
            header_cell.font = Font(bold=True)
            header_cell.fill = tbl_header_fill
            header_cell.border = border
            header_cell.alignment = center_align

        dong_summaries = summarize_dongs(household_summaries)
        for dong_summary in dong_summaries:
            d = dong_summary["dong"]
            r = ws_summary.max_row + 1
            ws_summary.cell(r, 1, display_dong_label(d))
            ws_summary.cell(r, 2, dong_summary["total"])
            ws_summary.cell(r, 3, dong_summary["full_done"])
            ws_summary.cell(r, 4, dong_summary["rate"]).number_format = '0.0%'
            ws_summary.cell(r, 5, dong_summary["written_done"])
            ws_summary.cell(r, 6, dong_summary["partial"])
            ws_summary.cell(r, 7, dong_summary["shortage"])
            for c in range(1, 8): ws_summary.cell(r, c).border = border
        dong_last_row = ws_summary.max_row

        # Column Widths
        from openpyxl.utils import get_column_letter
        for i in range(1, 10):
            ws_summary.column_dimensions[get_column_letter(i)].width = 16
        add_summary_charts(ws_summary, dong_header_row, dong_last_row)

        # --- 3. DONG SHEETS ---
        dong_groups = defaultdict(list)
        for row in padded_rows:
            dong_groups[cell_value(row, column_map, "dong") or "기타"].append(row)
            
        for dong_summary in dong_summaries:
            d = dong_summary["dong"]
            ws = wb.create_sheet(title=display_dong_label(d)[:31])
            ws.append(header)
            for r in dong_groups[d]:
                ws.append(r)

        wb.save(output_path)
        print(f"ULTRA-STABLE Dashboard Created: {output_path}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
