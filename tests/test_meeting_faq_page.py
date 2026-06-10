import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_FAQ = REPO_ROOT / "_posts" / "2026-05-22-주민설명회-FAQ.md"


class MeetingFaqPageTests(unittest.TestCase):
    def test_important_clarifications_are_present(self):
        source = SOURCE_FAQ.read_text()

        self.assertIn("선 입찰공고 및 선정 절차", source)
        self.assertIn("비례율 109% 수준", source)
        self.assertIn("공개 입찰과 주민 참여 투표", source)
        self.assertIn("특정 건설사 또는 시공사가 선정되었다는 말은 사실이 아닙니다", source)

    def test_important_clarifications_use_highlight_boxes(self):
        source = SOURCE_FAQ.read_text()

        self.assertIn("faq-important-note--process", source)
        self.assertIn("faq-important-note--finance", source)
        self.assertIn("faq-important-note--correction", source)


if __name__ == "__main__":
    unittest.main()
