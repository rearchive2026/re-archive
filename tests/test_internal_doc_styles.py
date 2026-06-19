import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
CUSTOM_HEAD = REPO_ROOT / "_includes" / "head" / "custom.html"


class InternalDocStyleTests(unittest.TestCase):
    def test_internal_tables_use_native_table_layout(self):
        source = CUSTOM_HEAD.read_text()

        self.assertIn(".internal-doc table {", source)
        self.assertIn("display: table;", source)
        self.assertIn("width: 100%;", source)


if __name__ == "__main__":
    unittest.main()
