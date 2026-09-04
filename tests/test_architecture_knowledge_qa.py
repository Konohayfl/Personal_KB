from pathlib import Path
import unittest


class ArchitectureKnowledgeQATest(unittest.TestCase):
    def test_qa_doc_exists_and_covers_recording_contract(self):
        root = Path(__file__).resolve().parents[1]
        doc = root / "docs" / "architecture_knowledge_qa.md"
        text = doc.read_text(encoding="utf-8")

        required_sections = [
            "文档目的",
            "适用范围",
            "解答约定",
            "记录格式",
            "问答索引",
            "维护要求",
            "初始使用说明",
        ]
        for item in required_sections:
            self.assertIn(item, text)

        required_terms = [
            "项目设计目标",
            "当前代码实现",
            "可改进方案",
            "简明结论",
            "详细解答",
            "在 WenKB 中的对应关系",
            "Git commit",
        ]
        for item in required_terms:
            self.assertIn(item, text)

    def test_agents_navigation_mentions_qa_doc(self):
        root = Path(__file__).resolve().parents[1]
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("docs/architecture_knowledge_qa.md", agents)


if __name__ == "__main__":
    unittest.main()
