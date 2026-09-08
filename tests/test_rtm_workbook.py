import unittest
from datetime import date, datetime
from pathlib import Path

from openpyxl import load_workbook


ROOT = Path(__file__).resolve().parents[1]
WORKBOOK = (
    ROOT
    / "outputs"
    / "rtm-maintenance-final"
    / "第14小组_基于大模型的个人知识库系统_需求跟踪矩阵.xlsx"
)
REMOVED_DUPLICATE = ROOT / "第14小组_基于大模型的个人知识库系统_需求跟踪矩阵.xlsx"


class RequirementTraceabilityMatrixTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workbook = load_workbook(WORKBOOK, data_only=False)
        cls.rtm = cls.workbook["设计用RTM"]
        cls.history = cls.workbook["变更履历"]

    def test_workbook_has_wenkb_sheets_and_no_template_project_content(self):
        self.assertFalse(REMOVED_DUPLICATE.exists())
        self.assertIn("需求跟踪矩阵封面", self.workbook.sheetnames)
        self.assertIn("变更履历", self.workbook.sheetnames)
        self.assertIn("设计用RTM", self.workbook.sheetnames)

        all_values = [
            str(cell.value)
            for worksheet in self.workbook.worksheets
            for row in worksheet.iter_rows()
            for cell in row
            if cell.value is not None
        ]
        content = "\n".join(all_values)
        self.assertNotIn("旧衣回收", content)
        self.assertNotIn("积分商城", content)
        self.assertIn("WenKB", content)

    def test_rtm_contains_all_baseline_requirements_and_statuses(self):
        expected_ids = [
            *(f"FR-{index:03d}" for index in range(1, 19)),
            *(f"NFR-{index:03d}" for index in range(1, 8)),
        ]
        requirement_rows = [
            row
            for row in range(1, self.rtm.max_row + 1)
            if self.rtm.cell(row, 2).value in expected_ids
        ]
        actual_ids = []
        for row in requirement_rows:
            requirement_id = self.rtm.cell(row, 2).value
            if requirement_id not in actual_ids:
                actual_ids.append(requirement_id)
        self.assertEqual(expected_ids, actual_ids)

        allowed_statuses = {"○", "△", "×", "N/A"}
        for row in requirement_rows:
            self.assertTrue(self.rtm.cell(row, 5).value)
            self.assertTrue(self.rtm.cell(row, 6).value)
            for column in (7, 8, 9):
                self.assertIn(self.rtm.cell(row, column).value, allowed_statuses)
            self.assertTrue(self.rtm.cell(row, 10).value)
            self.assertTrue(self.rtm.cell(row, 11).value)

    def test_change_history_has_twenty_two_numbered_records_and_key_changes(self):
        records = []
        for row in range(3, 25):
            sequence = self.history.cell(row, 2).value
            self.assertEqual(row - 2, sequence)
            change_date = self.history.cell(row, 3).value
            self.assertIsInstance(change_date, (date, datetime))
            normalized_date = change_date.date() if isinstance(change_date, datetime) else change_date
            self.assertLessEqual(normalized_date, date(2026, 9, 6))
            self.assertTrue(self.history.cell(row, 4).value)
            self.assertTrue(self.history.cell(row, 5).value)
            self.assertEqual(self.history.cell(row, 12).value, 25)
            records.append(str(self.history.cell(row, 4).value))

        content = "\n".join(records)
        for keyword in (
            "健康检查",
            "引用",
            "AES",
            "OpenAI",
            "embedding",
            "架构与知识点",
            "283e2c8",
            "变更履历",
        ):
            self.assertIn(keyword, content)

    def test_history_summary_and_workbook_formula_are_present(self):
        self.assertEqual(self.history.cell(25, 2).value, "SUM")
        self.assertEqual(self.history.cell(25, 12).value, 25)
        self.assertEqual(self.history.cell(25, 13).value, "=SUM(M3:M24)")

    def test_new_maintenance_history_records_are_present(self):
        self.assertEqual(self.history.cell(23, 2).value, 21)
        self.assertEqual(self.history.cell(24, 2).value, 22)
        self.assertEqual(self.history.cell(23, 3).value, datetime(2026, 9, 6))
        self.assertEqual(self.history.cell(24, 3).value, datetime(2026, 9, 6))

        first_change = str(self.history.cell(23, 4).value)
        second_change = str(self.history.cell(24, 4).value)
        self.assertIn("设计用RTM", first_change)
        self.assertIn("283e2c8", first_change)
        self.assertIn("未完成鉴权", first_change)
        self.assertIn("Excel 需求跟踪矩阵", second_change)
        self.assertEqual(self.history.cell(23, 12).value, 25)
        self.assertEqual(self.history.cell(24, 12).value, 25)

    def test_maintenance_records_are_reflected_in_requirement_details(self):
        expected_keywords = {
            "FR-001": ("AES", "WENKB_AES_KEY"),
            "FR-004": ("embedding 模型", "删除后清理"),
            "FR-009": ("数据库版本 5", "Git LFS"),
            "FR-014": ("兜底消息", "持久化"),
            "FR-015": ("引用快照", "稳定来源标识"),
            "FR-016": ("dtsetId", "元数据缺失"),
            "FR-017": ("级联清理文档版本", "访问权限"),
            "NFR-001": ("GET /health", "数据库健康检查"),
            "NFR-003": ("失败回落", "资源完整性提示"),
            "NFR-004": ("AES 参数校验", "访问控制"),
            "NFR-005": ("变更管理", "需求跟踪矩阵"),
            "NFR-006": ("六类 OpenAI 兼容供应商", "embedding 依赖校验"),
            "NFR-007": ("torch/fsspec", "Git LFS 模型权重"),
        }
        details_by_id = {}
        for row in range(1, self.rtm.max_row + 1):
            requirement_id = self.rtm.cell(row, 2).value
            if requirement_id:
                details_by_id.setdefault(requirement_id, []).append(
                    str(self.rtm.cell(row, 6).value)
                )

        for requirement_id, keywords in expected_keywords.items():
            with self.subTest(requirement_id=requirement_id):
                detail = "\n".join(details_by_id[requirement_id])
                for keyword in keywords:
                    self.assertIn(keyword, detail)

    def test_design_rtm_details_omit_basis_text_and_split_broad_categories(self):
        requirement_rows = [
            row
            for row in range(1, self.rtm.max_row + 1)
            if self.rtm.cell(row, 2).value
        ]
        detail_text = "\n".join(
            str(self.rtm.cell(row, 6).value)
            for row in requirement_rows
            if self.rtm.cell(row, 6).value
        )
        self.assertNotIn("依据：", detail_text)

        fr004_rows = [row for row in requirement_rows if self.rtm.cell(row, 2).value == "FR-004"]
        fr017_rows = [row for row in requirement_rows if self.rtm.cell(row, 2).value == "FR-017"]
        self.assertEqual(5, len(fr004_rows))
        self.assertEqual(3, len(fr017_rows))

        fr004_categories = [self.rtm.cell(row, 5).value for row in fr004_rows]
        self.assertEqual(
            [
                "知识库创建",
                "知识库查看",
                "知识库编辑",
                "知识库删除",
                "向量集合与关联清理",
            ],
            fr004_categories,
        )
        fr017_categories = [self.rtm.cell(row, 5).value for row in fr017_rows]
        self.assertEqual(
            [
                "文档集创建与维护",
                "文档维护与版本快照",
                "文档转数据集",
            ],
            fr017_categories,
        )

        for row in [*fr004_rows, *fr017_rows]:
            self.assertTrue(self.rtm.cell(row, 6).value)
            self.assertEqual("杨帆", self.rtm.cell(row, 10).value)
            self.assertEqual("杨帆", self.rtm.cell(row, 11).value)


if __name__ == "__main__":
    unittest.main()
