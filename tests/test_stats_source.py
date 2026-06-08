import unittest

from scripts.stats_source import (
    build_stats_column_map,
    cell_value,
    effective_submission,
    row_with_effective_submission,
)


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


if __name__ == "__main__":
    unittest.main()
