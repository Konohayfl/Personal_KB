from pathlib import Path
import unittest


class TestPlanTest(unittest.TestCase):
    def test_test_plan_doc_exists_and_covers_core_content(self):
        root = Path(__file__).resolve().parents[1]
        doc = root / "docs" / "test_plan.md"
        text = doc.read_text(encoding="utf-8")

        required_sections = [
            "文档目的",
            "设计依据",
            "测试目标",
            "测试范围",
            "测试策略",
            "测试类型",
            "测试环境与准备",
            "测试数据与基线",
            "主要测试项",
            "缺陷管理与回归",
            "通过标准",
            "风险与注意事项",
            "交付物与维护建议",
            "验收标准",
        ]
        for item in required_sections:
            self.assertIn(item, text)

        required_terms = [
            "知识库导入",
            "索引",
            "问答",
            "引用",
            "搜索",
            "文档集",
            "回归测试",
            "数据一致性",
            "静态文档测试",
            "TP-007",
        ]
        for item in required_terms:
            self.assertIn(item, text)

    def test_test_plan_is_implementation_agnostic(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "test_plan.md").read_text(encoding="utf-8")

        forbidden_markers = [
            ".py",
            "wenkb-server/",
            "wenkb-client/",
        ]
        for item in forbidden_markers:
            self.assertNotIn(item, text)

    def test_agents_navigation_mentions_test_plan(self):
        root = Path(__file__).resolve().parents[1]
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("docs/test_plan.md", agents)


if __name__ == "__main__":
    unittest.main()
