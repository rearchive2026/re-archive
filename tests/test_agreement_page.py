import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
PRIVACY_CONSENT_URL = (
    "https://www.buonestop.com/h/bs124/member-info-verification/intro"
)


class AgreementPageTests(unittest.TestCase):
    def test_privacy_consent_link_and_qr_use_current_url(self):
        source = (REPO_ROOT / "_pages" / "agreement.md").read_text()

        self.assertIn(PRIVACY_CONSENT_URL, source)
        self.assertIn("data-url=\"{{ privacy_consent_url }}\"", source)
        self.assertIn("assets/js/vendor/qrcode.min.js", source)
        self.assertIn("window.qrcode", source)
        self.assertNotIn("paperless.kt.com", source)
        self.assertNotIn("소유주인증QR.svg", source)


if __name__ == "__main__":
    unittest.main()
