from pathlib import Path
import unittest


class ChangeManagementTest(unittest.TestCase):
    def test_change_management_doc_exists_and_covers_core_process(self):
        root = Path(__file__).resolve().parents[1]
        doc = root / "docs" / "change_management.md"
        text = doc.read_text(encoding="utf-8")

        required_sections = [
            "文档目的",
            "管理范围",
            "变更分类",
            "变更等级",
            "变更流程",
            "代码与文档同步规则",
            "数据库与索引变更",
            "测试与质量门禁",
            "版本与提交管理",
            "回滚与应急处理",
            "变更记录模板",
            "当前项目执行要求",
            "验收标准",
        ]
        for item in required_sections:
            self.assertIn(item, text)

        required_terms = [
            "C1",
            "C2",
            "C3",
            "C4",
            "影响分析",
            "评审与批准",
            "Git commit",
            "数据库",
            "向量索引",
            "回滚",
            "测试结果",
            "维护交接记录",
            "进度审查与追踪依据",
        ]
        for item in required_terms:
            self.assertIn(item, text)

    def test_change_management_is_implementation_agnostic(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "change_management.md").read_text(encoding="utf-8")

        forbidden_markers = [
            ".py",
            "wenkb-server/",
            "wenkb-client/",
        ]
        for item in forbidden_markers:
            self.assertNotIn(item, text)

    def test_agents_navigation_removes_completed_user_manual_and_adds_change_management(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("docs/change_management.md", text)
        self.assertNotIn("用户手册：`docs/user_manual.md`", text)

    def test_agents_contains_navigation_only_for_maintenance_history(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("项目进度审查与维护历史统一记录在代码维护交接文档中", text)
        self.assertNotIn("## 维护记录", text)
        self.assertNotIn("2026-09-04：", text)
        self.assertNotIn("## 后续待补充", text)

    def test_maintenance_handoff_is_the_progress_review_and_history_source(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "code_maintenance_handoff.md").read_text(encoding="utf-8")

        required_sections = [
            "项目进度审查与追踪",
            "审查顺序",
            "进度追踪要求",
            "交付前审查门禁",
            "当前未完成事项",
            "当前工作区状态",
            "验证状态",
            "维护记录",
        ]
        for item in required_sections:
            self.assertIn(item, text)

        required_terms = [
            "唯一记录源",
            "主动使用本文档进行核对",
            "每次变更交付时",
            "Git commit",
            "向量索引和 embedding 模型如何协作",
            "tests/test_architecture_design.py",
            "“现状调研”改为“参考对象”",
            "第14小组_基于大模型的个人知识库系统_需求跟踪矩阵.xlsx",
            "torch==2.3.1",
            "WENKB_AES_KEY",
            "httpx 0.28.x",
            "OpenAI、DeepSeek、Moonshot、通义、智谱和 NVIDIA",
        ]
        for item in required_terms:
            self.assertIn(item, text)


if __name__ == "__main__":
    unittest.main()
