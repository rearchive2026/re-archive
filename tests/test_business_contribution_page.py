import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE = REPO_ROOT / "_pages" / "internal" / "260613-business-contribution.md"


class BusinessContributionPageTests(unittest.TestCase):
    def test_representative_contribution_amount_is_clear(self):
        source = SOURCE.read_text()

        self.assertIn("공사비 평당 880만원, 일반분양가 평균 평당 6,000만원", source)
        self.assertIn("대표 사례의 추정분담금은 약 6,100만 원", source)
        self.assertIn("32평에서 35평 선택 기준", source)
        self.assertIn("부담 약 6,100만 원", source)
        self.assertIn("주민 안내 대표 사례", source)
        self.assertNotIn("대표 추정분담금 약 6,000만 원", source)

    def test_alternative_values_are_labeled_as_hypothetical_examples(self):
        source = SOURCE.read_text()

        self.assertIn("사업조건 변화에 따른 가상 예시자료", source)
        self.assertIn("공개 대표 금액이 아닙니다", source)
        self.assertIn("가상 예시 1", source)
        self.assertIn("가상 예시 2", source)
        self.assertNotIn("조건 변화안", source)

    def test_default_case_keeps_exact_source_numbers(self):
        source = SOURCE.read_text()

        self.assertIn("<td class=\"num amount-burden\">+0.61억</td>", source)
        self.assertIn("대표 산정 기준<br>880만원 / 6,000만원", source)


if __name__ == "__main__":
    unittest.main()
