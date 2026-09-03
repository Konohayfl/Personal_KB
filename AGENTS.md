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

## 运行与操作文档

- 开发者与用户手册：[docs/wenkb_operation_guide.md](docs/wenkb_operation_guide.md)
- 代码维护交接：[docs/code_maintenance_handoff.md](docs/code_maintenance_handoff.md)
- 部署运维：[docs/deployment_guide.md](docs/deployment_guide.md)
- 变更管理：[docs/change_management.md](docs/change_management.md)

## 测试与验证文档

- 测试计划：[docs/test_plan.md](docs/test_plan.md)

## 后续待补充

### 维护记录

- 2026-09-03：修复模型供应商 API Key 保存时因 AES 占位密钥 `xxxx` 无效而触发内部错误的问题；后端改用有效 AES 参数并增加环境变量覆盖、加解密回归测试，详细记录见 [docs/code_maintenance_handoff.md](docs/code_maintenance_handoff.md)。
- 2026-09-03：修复 OpenAI 兼容模型使用 `httpx 0.28.x` 时 `ChatOpenAI` 初始化传递 `proxies` 参数导致的对话错误；增加显式 HTTP 客户端、依赖固定和回归测试，详细记录见 [docs/code_maintenance_handoff.md](docs/code_maintenance_handoff.md)。
- 2026-09-03：检查并修复 OpenAI 兼容 embedding 客户端在相同依赖组合下的 `proxies` 初始化错误；覆盖 OpenAI、DeepSeek、Moonshot、通义、智谱和 NVIDIA，增加跨供应商回归测试，详细记录见 [docs/code_maintenance_handoff.md](docs/code_maintenance_handoff.md)。
