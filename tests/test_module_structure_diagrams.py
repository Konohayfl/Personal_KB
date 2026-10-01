import importlib.util
from pathlib import Path
import unittest

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
DELIVERABLE_DIR = ROOT / "outputs" / "architecture-design-deliverables"
SCRIPT_PATH = DELIVERABLE_DIR / "scripts" / "generate_module_structure_diagrams.py"
MODULE_SPEC = importlib.util.spec_from_file_location(
    "generate_module_structure_diagrams",
    SCRIPT_PATH,
)
MODULE = importlib.util.module_from_spec(MODULE_SPEC)
assert MODULE_SPEC.loader is not None
MODULE_SPEC.loader.exec_module(MODULE)
OUTPUT_DIR = MODULE.OUTPUT_DIR
generate_all = MODULE.generate_all


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
        generated_files = {
            path.stem for path in OUTPUT_DIR.glob("*.png")
            if path.stem in EXPECTED_SLUGS
        }
        self.assertEqual(generated_files, EXPECTED_SLUGS)

        for path in paths:
            self.assertTrue(path.is_file(), path)
            with Image.open(path) as image:
                self.assertEqual(image.size, (2700, 1700))
                self.assertGreaterEqual(image.info.get("dpi", (0, 0))[0], 299)
                self.assertGreaterEqual(image.info.get("dpi", (0, 0))[1], 299)

    def test_deliverables_are_co_located_under_outputs(self):
        self.assertTrue((DELIVERABLE_DIR / "概要设计模板.doc").is_file())
        self.assertTrue((DELIVERABLE_DIR / "scripts" / "generate_module_structure_diagrams.py").is_file())
        self.assertTrue((DELIVERABLE_DIR / "images").is_dir())

        output_root = Path(OUTPUT_DIR).resolve()
        self.assertEqual(output_root.name, "module-structure")
        self.assertEqual(output_root.parent.name, "images")
        self.assertEqual(output_root.parent.parent, DELIVERABLE_DIR.resolve())


if __name__ == "__main__":
    unittest.main()
