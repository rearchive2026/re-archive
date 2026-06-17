import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class NoticeLinkTests(unittest.TestCase):
    def test_consent_rate_achievement_post_is_a_notice(self):
        source = (
            REPO_ROOT
            / "_posts"
            / "2026-06-16-특별정비구역-신청-동의율-50-달성.md"
        ).read_text()

        self.assertIn('title: "🎉 특별정비구역 신청 동의율 50% 달성"', source)
        self.assertIn("date: 2026-06-16 14:00:00 +0900", source)
        self.assertIn("categories: Notices", source)
        self.assertIn("consent-rate-50-achievement.png", source)
        self.assertIn("permalink: /notices/2026/06/16/특별정비구역-신청-동의율-50-달성.html", source)

    def test_electronic_consent_resume_post_is_a_notice(self):
        source = (
            REPO_ROOT
            / "_posts"
            / "2026-06-16-재건축-전자동의-재개-안내.md"
        ).read_text()

        self.assertIn('title: "📢 재건축 전자동의 재개 안내"', source)
        self.assertIn("date: 2026-06-16", source)
        self.assertIn("categories: Notices", source)

    def test_home_notice_list_uses_post_permalink(self):
        source = (REPO_ROOT / "index.md").read_text()

        self.assertIn(
            '{% assign notices = site.posts | where_exp: "p", "p.categories contains \'Notices\'" %}',
            source,
        )
        self.assertIn('href="{{ post.url | relative_url }}"', source)
        self.assertIn("{% for post in notices %}", source)
        self.assertNotIn("{% for post in notices limit:5 %}", source)
        self.assertNotIn('href="/agreement/" style="text-decoration: none;">{{ post.title }}', source)

    def test_home_notice_list_links_to_notice_index(self):
        source = (REPO_ROOT / "index.md").read_text()

        self.assertIn("{{ '/notices/' | relative_url }}", source)
        self.assertNotIn("/categories/#notices", source)

    def test_notice_index_lists_notice_category_posts(self):
        source = (REPO_ROOT / "_pages" / "notices.md").read_text()

        self.assertIn("permalink: /notices/", source)
        self.assertIn(
            '{% assign notice_posts = site.posts | where_exp: "post", "post.categories contains \'Notices\'" %}',
            source,
        )
        self.assertIn("{% include archive-single.html %}", source)

    def test_home_notice_layer_uses_consent_rate_achievement_notice(self):
        source = (REPO_ROOT / "index.md").read_text()

        self.assertIn("notice_layers:", source)
        self.assertIn("{% for notice_layer in page.notice_layers %}", source)
        self.assertIn("consent-rate-50-achievement.png", source)
        self.assertIn("/notices/2026/06/16/특별정비구역-신청-동의율-50-달성.html", source)
        self.assertIn("특별정비구역 신청 동의율 50% 달성", source)
        self.assertIn('key: "20260616ConsentRate50"', source)
        self.assertIn('data-notice-storage-key="briefingNoticeHiddenDate{{ notice_layer.key }}"', source)

    def test_home_notice_layer_uses_electronic_consent_resume_notice(self):
        source = (REPO_ROOT / "index.md").read_text()

        self.assertIn('key: "20260616ElectronicConsentResume"', source)
        self.assertIn("재건축 전자동의 재개 안내", source)
        self.assertIn("/notices/2026/06/16/재건축-전자동의-재개-안내.html", source)
        self.assertIn("electronic-consent-resume-notice.png", source)
        self.assertIn('max_width: "595px"', source)

    def test_home_notice_layers_are_explicitly_configured_only(self):
        source = (REPO_ROOT / "index.md").read_text()

        self.assertEqual(2, source.count('  - key: "20260616'))
        self.assertIn('querySelectorAll(".briefing-notice-layer")', source)
        self.assertIn("pendingLayers", source)
        self.assertIn("showNextLayer", source)
        self.assertIn('data-notice-storage-key="briefingNoticeHiddenDate{{ notice_layer.key }}"', source)
        self.assertNotIn("site.posts | where_exp", source.split("{% for notice_layer in page.notice_layers %}", 1)[0])

    def test_home_body_keeps_electronic_consent_resume_notice(self):
        source = (REPO_ROOT / "index.md").read_text()

        self.assertIn("## 📝 재건축 전자동의 재개 안내", source)
        self.assertIn("electronic-consent-resume-notice.png?v=20260616", source)
        self.assertIn("]({{ '/agreement/' | relative_url }})", source)


if __name__ == "__main__":
    unittest.main()
