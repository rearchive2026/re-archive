import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class AgreementPageTests(unittest.TestCase):
    def test_agreement_page_uses_electronic_consent_resume_notice(self):
        source = (REPO_ROOT / "_pages" / "agreement.md").read_text()

        self.assertIn("재건축 전자동의 안내", source)
        self.assertIn("electronic-consent-resume-notice.png", source)
        self.assertIn("전자동의를 다시 시작", source)
        self.assertIn("서면동의도 함께 접수", source)
        self.assertIn("/verification/", source)
        self.assertIn("공동소유자", source)
        self.assertIn("1인의 동의로만 반영", source)
        self.assertIn("https://pf.kakao.com/_FlxkGX", source)
        self.assertIn("https://pf.kakao.com/_FlxkGX/chat", source)
        self.assertNotIn("written-consent-notice.png", source)
        self.assertNotIn("2026년 6월 13일(토)", source)
        self.assertNotIn("2026년 6월 14일(일)", source)
        self.assertNotIn("모바일 신분증 불가", source)
        self.assertNotIn("재건축, 꼭 알아야 할 핵심만 정리했습니다", source)
        self.assertNotIn("분담금이 너무 커서 무조건 손해다", source)

    def test_legacy_external_e_signature_vendors_are_not_reintroduced(self):
        source = (REPO_ROOT / "_pages" / "agreement.md").read_text()

        self.assertNotIn("assets/js/vendor/qrcode.min.js", source)
        self.assertNotIn("window.qrcode", source)
        self.assertNotIn("privacy-consent-qr", source)
        self.assertNotIn("buonestop.com", source)
        self.assertNotIn("paperless.kt.com", source)
        self.assertNotIn("레디포스트", source)
        self.assertNotIn("Readypost", source)


if __name__ == "__main__":
    unittest.main()
