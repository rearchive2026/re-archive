import unittest

from scripts.stats_source import (
    build_stats_column_map,
    cell_value,
    effective_submission,
    final_submission,
    normalize_cell,
    row_with_excel_numeric_dong_ho,
    row_with_effective_submission,
)
from scripts.split_by_dong import build_dashboard_workbook


class StatsSourceTests(unittest.TestCase):
    def test_new_dashboard_format_uses_populated_duplicate_bonbun_column(self):
        header = [
            "본번",
            "부번",
            "공유여부",
            "공유물건 동의상태",
            "대표선임",
            "선임결과",
            "다필지",
            "본번",
            "부번",
            "동",
            "호수",
            "동호수",
            "성명",
            "생년월일",
            "성별",
            "휴대폰번호",
            "연번",
            "제출 형태",
            "참여 상태",
            "메모",
        ]
        rows = [
            ["", "", "", "", "", "", "", "517", "", "601", "103", "601 103", "홍길동", "", "", "01012345678", "", "전자", "완료", "서면 동의 완료"],
            ["", "", "공유 O", "✅ 동의 완료", "", "", "", "526", "", "701", "703", "701 703", "김길동", "", "", "", "", "서면", "비대상", ""],
            ["", "", "", "", "", "", "", "526", "", "702", "1201", "702 1201", "박길동", "", "", "", "", "전자", "예약", "서면동의"],
        ]

        column_map = build_stats_column_map(header, rows)

        self.assertEqual(column_map["bonbun"], 7)
        self.assertEqual(column_map["submission"], 17)
        self.assertEqual(column_map["participation"], 18)
        self.assertEqual(column_map["memo"], 19)
        self.assertEqual(cell_value(rows[0], column_map, "bonbun"), "517")
        self.assertEqual(cell_value(rows[1], column_map, "shared"), "공유 O")
        self.assertEqual(effective_submission(rows[0], column_map), "서면")
        self.assertEqual(effective_submission(rows[2], column_map), "서면")
        self.assertEqual(row_with_effective_submission(rows[0], column_map)[17], "서면")

    def test_old_dashboard_format_still_maps_existing_columns(self):
        header = ["본번", "동", "호수", "성명", "성별", "공유여부", "휴대폰번호", "공유물건 동의상태", "제출 형태", "참여 상태"]
        rows = [["517", "601", "103", "홍길동", "", "", "01012345678", "", "전자", "완료"]]

        column_map = build_stats_column_map(header, rows)

        self.assertEqual(column_map["bonbun"], 0)
        self.assertEqual(column_map["dong"], 1)
        self.assertEqual(column_map["ho"], 2)
        self.assertEqual(column_map["submission"], 8)
        self.assertEqual(column_map["participation"], 9)

    def test_numeric_excel_values_normalize_to_plain_integer_text(self):
        self.assertEqual(normalize_cell(601.0), "601")
        self.assertEqual(normalize_cell(103), "103")
        self.assertEqual(normalize_cell(" 0103 "), "0103")

    def test_dong_and_ho_are_written_as_numbers_when_possible(self):
        header = ["본번", "동", "호수", "공유여부", "제출 형태", "참여 상태"]
        rows = [["517", "601", "0103", "", "전자", "완료"]]
        column_map = build_stats_column_map(header, rows)

        output_row = row_with_excel_numeric_dong_ho(rows[0], column_map)

        self.assertEqual(output_row[1], 601)
        self.assertEqual(output_row[2], 103)

    def test_non_numeric_dong_and_ho_stay_as_text(self):
        header = ["본번", "동", "호수", "공유여부", "제출 형태", "참여 상태"]
        rows = [["517", "상가", "1층, 유치원", "", "전자", "완료"]]
        column_map = build_stats_column_map(header, rows)

        output_row = row_with_excel_numeric_dong_ho(rows[0], column_map)

        self.assertEqual(output_row[1], "상가")
        self.assertEqual(output_row[2], "1층, 유치원")

    def test_dashboard_workbook_outputs_only_operational_columns(self):
        header = [
            "본번",
            "부번",
            "공유여부",
            "공유물건 동의상태",
            "대표선임",
            "선임결과",
            "다필지",
            "본번",
            "부번",
            "동",
            "호수",
            "동호수",
            "성명",
            "생년월일",
            "성별",
            "휴대폰번호",
            "연번",
            "제출 형태",
            "참여 상태",
            "발송 상태 메시지",
            "발송일시",
            "열람일시",
            "완료일시",
            "KT 본인인증",
            "신분증",
            "가족관계증명서",
            "주민등록등본",
            "URL 발송",
            "최종 완료 여부",
            "메모",
        ]
        rows = [[
            "",
            "",
            "공유 O",
            "✅ 동의 완료",
            "",
            "대표자 X",
            "다필지 O",
            "517",
            "",
            "601",
            "103",
            "601 103",
            "홍길동",
            "19700101",
            "남",
            "01012345678",
            "",
            "전자",
            "완료",
            "",
            "2026-05-16 13:55:58",
            "2026-05-16 14:02:07",
            "2026-05-23 14:38:40",
            "true",
            "false",
            "false",
            "false",
            "false",
            "NOT_DONE",
            "서면동의",
        ]]

        workbook = build_dashboard_workbook(header, rows, "test.xlsx")
        output_header = [
            workbook["Data_Source"].cell(1, column).value
            for column in range(1, workbook["Data_Source"].max_column + 1)
        ]

        self.assertEqual(
            output_header,
            [
                "본번",
                "동",
                "호수",
                "성명",
                "공유여부",
                "공유물건 동의상태",
                "다필지",
                "제출형태",
                "최종동의방식",
                "참여상태",
                "발송 상태 메시지",
                "발송일시",
                "열람일시",
                "완료일시",
                "메모",
            ],
        )
        data_row = [
            workbook["Data_Source"].cell(2, column).value
            for column in range(1, workbook["Data_Source"].max_column + 1)
        ]
        self.assertEqual(data_row[7], "전자")
        self.assertEqual(data_row[8], "서면")
        self.assertEqual(data_row[9], "완료")
        self.assertNotIn("생년월일", output_header)
        self.assertNotIn("휴대폰번호", output_header)
        self.assertNotIn("최종 완료 여부", output_header)
        self.assertNotIn("H_세대ID", output_header)
        self.assertNotIn("세대 통합 메모", output_header)
        self.assertEqual(workbook["Data_Source"].auto_filter.ref, "A1:O2")
        self.assertEqual(workbook["601동"].auto_filter.ref, "A1:O2")
        self.assertEqual(workbook["통합통계"].auto_filter.ref, "A8:G9")

    def test_written_consent_is_checked_per_owner_not_household(self):
        header = ["본번", "동", "호수", "성명", "공유여부", "제출 형태", "참여 상태", "메모"]
        rows = [
            ["517", "601", "103", "홍길동", "", "전자", "완료", ""],
            ["517", "601", "103", "김길동", "공유 O", "전자", "완료", "서면 동의 완료"],
        ]

        workbook = build_dashboard_workbook(header, rows, "test.xlsx")
        source = workbook["Data_Source"]
        headers = [source.cell(1, column).value for column in range(1, source.max_column + 1)]
        submission_col = headers.index("제출형태") + 1
        final_col = headers.index("최종동의방식") + 1

        self.assertEqual(source.cell(2, submission_col).value, "전자")
        self.assertEqual(source.cell(3, submission_col).value, "전자")
        self.assertEqual(source.cell(2, final_col).value, "전자")
        self.assertEqual(source.cell(3, final_col).value, "서면")
        self.assertNotIn("세대 통합 메모", headers)

    def test_combined_memo_column_does_not_mark_written_consent(self):
        header = ["본번", "동", "호수", "공유여부", "제출 형태", "참여 상태", "메모", "세대 통합 메모"]
        rows = [["517", "601", "103", "", "전자", "완료", "", "서면동의"]]
        column_map = build_stats_column_map(header, rows)

        self.assertEqual(final_submission(rows[0], column_map), "전자")

    def test_shared_household_written_consent_stays_per_owner(self):
        header = ["본번", "동", "호수", "성명", "공유여부", "제출 형태", "참여 상태", "메모"]
        rows = [
            ["526", "703", "1402", "이규호", "공유 O", "전자", "완료", "서면 동의 완료"],
            ["526", "703", "1402", "김윤희", "공유 O", "전자", "완료", ""],
        ]

        workbook = build_dashboard_workbook(header, rows, "test.xlsx")
        source = workbook["Data_Source"]
        headers = [source.cell(1, column).value for column in range(1, source.max_column + 1)]
        final_col = headers.index("최종동의방식") + 1
        memo_col = headers.index("메모") + 1

        self.assertEqual(source.cell(2, final_col).value, "서면")
        self.assertEqual(source.cell(3, final_col).value, "전자")
        self.assertIn(source.cell(3, memo_col).value, (None, ""))
        self.assertNotIn("세대 통합 메모", headers)


if __name__ == "__main__":
    unittest.main()
