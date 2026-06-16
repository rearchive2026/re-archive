import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class FaqPageTests(unittest.TestCase):
    def test_core_reconstruction_summary_has_dedicated_post(self):
        source = (
            REPO_ROOT
            / "_posts"
            / "2026-06-10-재건축-꼭-알아야-할-핵심만-정리.md"
        ).read_text()

        self.assertIn("재건축, 꼭 알아야 할 핵심만 정리했습니다", source)
        self.assertIn("분담금이 너무 커서 무조건 손해다", source)
        self.assertIn("고령 세대는 이주와 비용 때문에 무조건 불리하다", source)
        self.assertIn("핵심만", source)

    def test_faq_index_links_to_core_summary_without_inline_detail(self):
        source = (REPO_ROOT / "_pages" / "faq.md").read_text()
        post = (
            REPO_ROOT
            / "_posts"
            / "2026-06-10-재건축-꼭-알아야-할-핵심만-정리.md"
        )

        self.assertNotIn("분담금이 너무 커서 무조건 손해다", source)
        self.assertTrue(post.exists())
        self.assertIn("categories: FAQ", post.read_text())

    def test_second_special_district_qna_has_faq_post(self):
        post = (
            REPO_ROOT
            / "_posts"
            / "2026-06-13-2차-특별정비구역-주민-설명회-QnA.md"
        )
        source = post.read_text()

        self.assertTrue(post.exists())
        self.assertIn('title: "2차 특별정비구역 주민 설명회 QnA"', source)
        self.assertIn("categories: FAQ", source)
        self.assertIn("permalink: /FAQ/2026/06/13/2차-특별정비구역-주민-설명회-QnA.html", source)
        self.assertIn(".qna-detail h3", source)
        self.assertIn('<section class="qna-detail"', source)
        self.assertIn("일반분양 756세대", source)
        self.assertIn("전자동의와 서면동의를 합쳐 경남·벽산 통합 기준 약 50% 수준", source)


if __name__ == "__main__":
    unittest.main()
