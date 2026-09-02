from pathlib import Path
import unittest


class OperationGuideTest(unittest.TestCase):
    def test_operation_guide_covers_key_flows(self):
        root = Path(__file__).resolve().parents[1]
        doc = root / "docs" / "wenkb_operation_guide.md"
        text = doc.read_text(encoding="utf-8")

        required_sections = [
            "代码运行流程",
            "如何导入大模型",
            "如何导入知识库",
            "如何运用知识库进行问答",
            "常见排查点",
        ]
        for item in required_sections:
            self.assertIn(item, text)

        required_refs = [
            "app.py",
            "Scheduler.py",
            "SettingApi.py",
            "DatasetApi.py",
            "ChatApi.py",
            "llm_client_tools.py",
            "ask_to_llm.py",
            "DocumentImportForm.vue",
            "LinkImportForm.vue",
            "Content.vue",
        ]
        for item in required_refs:
            self.assertIn(item, text)

        required_behaviors = [
            "16088",
            "idxSts = new",
            "enbSts = enb",
            "topK",
            "smlrTrval",
            "POST /knb/chat/message",
        ]
        for item in required_behaviors:
            self.assertIn(item, text)


if __name__ == "__main__":
    unittest.main()
