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
            "代码维护交接文档中追加维护记录",
        ]
        for item in required_terms:
            self.assertIn(item, text)

    def test_agents_navigation_mentions_qa_doc(self):
        root = Path(__file__).resolve().parents[1]
        agents = (root / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("docs/architecture_knowledge_qa.md", agents)

    def test_vector_index_and_embedding_record_is_present(self):
        root = Path(__file__).resolve().parents[1]
        text = (root / "docs" / "architecture_knowledge_qa.md").read_text(encoding="utf-8")

        required_terms = [
            "## Q1：向量索引和 embedding 模型如何协作",
            "embedding 模型负责把文本转换成能够表达语义的数值向量",
            "向量索引负责保存这些向量并快速找出与查询向量最相近的内容",
            "PersistentClient",
            "resources/vector_store/<reposId>",
            "similarity_search_with_score",
            "分数越小越相似",
            "topK",
            "smlrTrval",
            "maxCtx",
            "embedding 模型一致",
            "设计与实现差异",
            "可改进方案",
        ]
        for item in required_terms:
            self.assertIn(item, text)

        self.assertIn("[Q1](#q1向量索引和-embedding-模型如何协作)", text)
        self.assertIn("repos_vector_db.py", text)
        self.assertIn("dataset_to_vector.py", text)
        self.assertIn("llm_client_tools.py", text)
        self.assertIn("ask_to_llm.py", text)


if __name__ == "__main__":
    unittest.main()
