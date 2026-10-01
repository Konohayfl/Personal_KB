from pathlib import Path
import unittest

from PIL import Image

from docs.scripts.generate_module_structure_diagrams import OUTPUT_DIR, generate_all


EXPECTED_SLUGS = {
    "01-model-configuration",
    "02-knowledge-base",
    "03-dataset-management",
    "04-index-building",
    "05-chat-retrieval",
    "06-enhancement-generation",
    "07-search",
    "08-document-orchestration",
}


class ModuleStructureDiagramTests(unittest.TestCase):
    def test_generation_creates_all_word_ready_images(self):
        paths = generate_all()
        self.assertEqual({path.stem for path in paths}, EXPECTED_SLUGS)
        self.assertEqual(len(list(OUTPUT_DIR.glob("*.png"))), len(EXPECTED_SLUGS))

        for path in paths:
            self.assertTrue(path.is_file(), path)
            with Image.open(path) as image:
                self.assertEqual(image.size, (2700, 1700))
                self.assertGreaterEqual(image.info.get("dpi", (0, 0))[0], 299)
                self.assertGreaterEqual(image.info.get("dpi", (0, 0))[1], 299)

    def test_output_is_inside_documentation_images_directory(self):
        output_root = Path(OUTPUT_DIR).resolve()
        self.assertEqual(output_root.name, "module-structure")
        self.assertEqual(output_root.parent.name, "images")


if __name__ == "__main__":
    unittest.main()
