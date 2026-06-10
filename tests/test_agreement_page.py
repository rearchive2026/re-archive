import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class AgreementPageTests(unittest.TestCase):
    def test_agreement_page_uses_written_consent_notice(self):
        source = (REPO_ROOT / "_pages" / "agreement.md").read_text()

        self.assertIn("서면동의서 제출", source)
        self.assertIn("written-consent-notice.png", source)
        self.assertIn("2026년 6월 13일(토)", source)
        self.assertIn("2026년 6월 14일(일)", source)
        self.assertIn("모바일 신분증 불가", source)
        self.assertIn("공동소유자", source)
        self.assertIn("https://pf.kakao.com/_FlxkGX", source)
        self.assertIn("https://pf.kakao.com/_FlxkGX/chat", source)
        self.assertNotIn("010-3036-1158", source)
        self.assertNotIn("010-4712-8123", source)
        self.assertNotIn("재건축, 꼭 알아야 할 핵심만 정리했습니다", source)
        self.assertNotIn("분담금이 너무 커서 무조건 손해다", source)

    def test_electronic_signature_flow_is_removed(self):
        source = (REPO_ROOT / "_pages" / "agreement.md").read_text()

        self.assertNotIn("assets/js/vendor/qrcode.min.js", source)
        self.assertNotIn("window.qrcode", source)
        self.assertNotIn("privacy-consent-qr", source)
        self.assertNotIn("buonestop.com", source)
        self.assertNotIn("paperless.kt.com", source)
        self.assertNotIn("소유주인증QR.svg", source)
        self.assertNotIn("레디포스트", source)
        self.assertNotIn("Readypost", source)


if __name__ == "__main__":
    unittest.main()
