import unittest
from pathlib import Path

import fitz


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PDF = ROOT / "outputs" / "pdf" / "杨帆-WenKB.pdf"


class ResumePdfTest(unittest.TestCase):
    def test_replaced_resume_exists_and_keeps_one_page_layout(self):
        self.assertTrue(OUTPUT_PDF.is_file(), OUTPUT_PDF)
        document = fitz.open(OUTPUT_PDF)
        try:
            self.assertEqual(len(document), 1)
            self.assertEqual(round(document[0].rect.width, 2), 594.96)
            self.assertEqual(round(document[0].rect.height, 2), 841.92)
        finally:
            document.close()

    def test_replaced_resume_contains_wenkb_project_and_preserves_next_project(self):
        document = fitz.open(OUTPUT_PDF)
        try:
            text = document[0].get_text()
        finally:
            document.close()
        self.assertIn("WenKB", text)
        self.assertIn("知识库", text)
        self.assertNotIn("小众点评", text)
        self.assertIn("分布式在线购票系统", text)
        self.assertIn("Chroma", text)
        self.assertIn("引用快照", text)


if __name__ == "__main__":
    unittest.main()
