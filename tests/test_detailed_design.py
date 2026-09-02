from pathlib import Path
import unittest


class DetailedDesignTest(unittest.TestCase):
    def test_detailed_design_doc_exists_and_is_specific(self):
        root = Path(__file__).resolve().parents[1]
        doc = root / "docs" / "detailed_design.md"
        text = doc.read_text(encoding="utf-8")

        required_sections = [
            "设计目标",
            "设计依据",
            "逻辑架构",
            "核心数据对象",
            "关键流程设计",
            "状态机设计",
            "一致性与事务规则",
            "异常处理设计",
            "可测试性设计",
        ]
        for item in required_sections:
            self.assertIn(item, text)

        required_entities = [
            "模型供应商",
            "模型首选项",
            "知识库设置",
            "数据集",
            "分段",
            "摘要",
            "Q&A",
            "三元组",
            "对话",
            "消息",
            "引用",
        ]
        for item in required_entities:
            self.assertIn(item, text)

        forbidden_markers = [
            ".py",
            "wenkb-server/",
            "wenkb-client/",
        ]
        for item in forbidden_markers:
            self.assertNotIn(item, text)

    def test_agents_navigation_includes_detailed_design(self):
        root = Path(__file__).resolve().parents[1]
        agents = root / "AGENTS.md"
        text = agents.read_text(encoding="utf-8")
        self.assertIn("docs/detailed_design.md", text)


if __name__ == "__main__":
    unittest.main()
