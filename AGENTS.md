# 注意事项

- 每次改动完成后，都必须创建一个对应的 Git commit，以便后续追踪和回滚。
- 每次改动后，都必须编写或更新相关测试，并在交付给用户前确保所有测试和验证通过。
- 需求分析与概要设计应作为目标产品的基线，详细设计阶段再补充实现映射。
- 在编写文档的同时如对项目代码有修改需求可以一并完成，以确保代码忠于设计。
- 任何对于代码的修改与维护都应该在维护文档中记录下来，对于文档的修改需要记录在AGENTS.md中。

# WenKB 项目文档导航

本文件作为仓库根目录的文档入口，用于帮助后续开发、测试和维护快速定位基准资料。

## 软件工程阶段文档

- 需求分析：[docs/requirements_analysis.md](docs/requirements_analysis.md)
- 概要设计：[docs/architecture_design.md](docs/architecture_design.md)
- 详细设计：[docs/detailed_design.md](docs/detailed_design.md)
- 数据库设计：[docs/database_design.md](docs/database_design.md)
- 接口设计：[docs/api_design.md](docs/api_design.md)

## 学习与问答记录

- 架构与知识点问答记录：[docs/architecture_knowledge_qa.md](docs/architecture_knowledge_qa.md)

## 运行与操作文档

- 开发者与用户手册：[docs/wenkb_operation_guide.md](docs/wenkb_operation_guide.md)
- 代码维护交接：[docs/code_maintenance_handoff.md](docs/code_maintenance_handoff.md)
- 部署运维：[docs/deployment_guide.md](docs/deployment_guide.md)
- 变更管理：[docs/change_management.md](docs/change_management.md)

## 测试与验证文档

- 测试计划：[docs/test_plan.md](docs/test_plan.md)

## 维护记录

- 2026-09-04：在 [docs/architecture_knowledge_qa.md](docs/architecture_knowledge_qa.md) 追加 Q1“向量索引和 embedding 模型如何协作”，结合设计基线和当前代码记录 embedding、Chroma 持久化集合、索引构建、相似度检索、引用链路、模型一致性约束及设计与实现差异；扩展对应文档回归测试。

- 2026-09-04：为完成本轮全量回归，修正 `tests/test_architecture_design.py` 中与当前需求分析文档不一致的章节断言（“现状调研”改为“参考对象”），并在代码维护交接记录中补充该验证修正。

- 2026-09-04：依据需求分析、概要设计、详细设计、数据库设计、接口设计、测试计划、部署运维和代码维护交接文档，重建《第14小组_基于大模型的个人知识库系统_需求跟踪矩阵.xlsx》；矩阵覆盖 18 项功能需求与 7 项非功能需求，并补录 2026-09-02 至 2026-09-04 的 20 条现有变更记录；新增 Excel 结构与内容回归测试。

- 2026-09-04：新增 [docs/architecture_knowledge_qa.md](docs/architecture_knowledge_qa.md)，用于持续记录后续关于项目架构、技术概念和代码实现的疑问与解答；新增对应文档回归测试，确保记录模板和导航链接完整。

- 2026-09-03：修复 Windows 本地 m3e embedding 因 Torch 动态库和 Git LFS 占位权重导致的向量集合创建失败；固定 `torch==2.3.1`、`fsspec==2024.6.1`，补充模型资源校验、回归测试和操作手册说明，详细记录见 [docs/code_maintenance_handoff.md](docs/code_maintenance_handoff.md)。

- 2026-09-03：修复模型供应商 API Key 保存时因 AES 占位密钥 `xxxx` 无效而触发内部错误的问题；后端改用有效 AES 参数并增加环境变量覆盖、加解密回归测试，详细记录见 [docs/code_maintenance_handoff.md](docs/code_maintenance_handoff.md)。
- 2026-09-03：修复 OpenAI 兼容模型使用 `httpx 0.28.x` 时 `ChatOpenAI` 初始化传递 `proxies` 参数导致的对话错误；增加显式 HTTP 客户端、依赖固定和回归测试，详细记录见 [docs/code_maintenance_handoff.md](docs/code_maintenance_handoff.md)。
- 2026-09-03：检查并修复 OpenAI 兼容 embedding 客户端在相同依赖组合下的 `proxies` 初始化错误；覆盖 OpenAI、DeepSeek、Moonshot、通义、智谱和 NVIDIA，增加跨供应商回归测试，详细记录见 [docs/code_maintenance_handoff.md](docs/code_maintenance_handoff.md)。
