# WenKB 代码维护交接记录

版本：v0.1  
日期：2026-09-02  
状态：暂停维护，待下次继续

## 1. 交接目的

本文记录依据需求分析、概要设计、详细设计、数据库设计和接口设计对项目代码进行维护时已经完成的工作、当前工作区状态、未完成事项和验证情况。

下次继续维护时，应先阅读本文，再结合以下基线文档恢复工作：

- [需求分析](requirements_analysis.md)
- [概要设计](architecture_design.md)
- [详细设计](detailed_design.md)
- [数据库设计](database_design.md)
- [接口设计](api_design.md)
- [操作流程](wenkb_operation_guide.md)

## 2. 已完成工作

### 2.1 系统能力

- 新增 `GET /health` 健康检查接口。
- 健康检查会验证数据库连接，并使用统一成功或失败响应结构。
- 已在 `wenkb-server/app.py` 注册健康检查接口。

### 2.2 聊天与引用

- 新增聊天消息引用 ORM、实体和 `t_knb_chat_quote` 表。
- 问答检索结果会保存为引用快照，包含数据集、文件、相似度、正文和来源对象标识。
- 聊天消息查询会附带引用列表。
- 删除消息、对话、知识库聊天或知识库时会清理关联引用。
- 接口设计文档已补充聊天引用字段和流式事件约定。

### 2.3 知识库

- 当前用户的知识库列表会包含本人知识库和公开知识库。
- 创建知识库时会校验 embedding 模型，并初始化默认问答设置。
- 已有索引的数据集禁止直接切换 embedding 模型。
- 删除知识库时会清理数据集、聊天、搜索历史、引用、知识增强对象、关系库设置和向量集合。

### 2.4 数据集与索引

- 删除数据集时会清理分段、摘要、Q&A、三元组、索引错误记录和文件。
- 手工维护的摘要、Q&A、三元组也会随数据集删除。
- 向量不存在时，分段、摘要和三元组仍会更新关系库。
- 索引成功或重试成功后会清理旧错误记录。
- 数据库升级脚本会按文件名排序执行，并使用上下文管理器关闭 SQL 文件。

### 2.5 文档集

- 当前用户的文档集列表会包含本人文档集和公开文档集。
- 删除文档集或文档时会级联清理文档版本。
- 修改文档内容时会自动保存版本快照。
- 文档转数据集前会校验知识库存在性和访问权限。

### 2.6 搜索和数据库版本

- 修复搜索结果元数据缺失时 `dtsetId` 可能未定义的问题。
- 数据库版本号已调整为 `5`。
- `ddl/0.sql`、`ddl/1.sql` 和 `ddl/4.sql` 已加入聊天引用表相关结构。

## 3. 当前未完成事项

以下事项在暂停前已确认，但没有继续实施：

1. 新增 `wenkb-server/server/db/upgrade/ddl/5.sql`，把旧的联合主键索引错误表迁移为 `error_id` 主键，并补充 `(dtset_id, idx_typ, crt_tm)` 索引。
2. 同步检查 `ddl/0.sql`、`ddl/1.sql`、`ddl/2.sql` 的索引错误表结构，使全新安装和升级安装一致。
3. 修复 `ask_to_llm_stream` 在模型异常、历史整理异常或检索异常时提前返回的问题，确保助手消息保存最终错误或兜底内容。
4. 为知识库名称、介绍、权限修改和相关问答接口补充拥有者或访问权限校验。
5. 为数据集上传、编辑、删除、目录、分段、摘要、三元组和增强对象接口补充知识库访问或修改权限校验。
6. 为文档集名称、描述、权限以及文档标题编辑接口补充拥有者校验。
7. 为聊天查询、发送、修改、删除、清空和重新生成接口补充对话及知识库访问权限校验。
8. 更新 `tests/test_code_maintenance.py` 中仍断言 `DB_SCHEMA_VERSION = 4` 的测试，并增加 `ddl/5.sql` 迁移检查。
9. 完成上述代码后重新运行完整编译和测试，并检查数据库升级器在旧版本数据库上的实际迁移结果。

## 4. 当前工作区状态

暂停时存在尚未提交的代码改动，涉及以下文件或目录：

- `wenkb-server/app.py`
- `wenkb-server/config/common.py`
- `wenkb-server/server/api/sys/HealthApi.py`
- `wenkb-server/server/api/knb/ReposInfoApi.py`
- `wenkb-server/server/api/knb/DatasetApi.py`
- `wenkb-server/server/api/knb/ChatApi.py`
- `wenkb-server/server/api/knb/SearchApi.py`
- `wenkb-server/server/api/doc/DocsetInfoApi.py`
- `wenkb-server/server/core/knb/DatasetService.py`
- `wenkb-server/server/core/knb/ReposService.py`
- `wenkb-server/server/core/doc/DocsetService.py`
- `wenkb-server/server/core/queue/DatasetToVectorQueue.py`
- `wenkb-server/server/core/queue/DatasetEnhanceVectorQueue.py`
- `wenkb-server/server/core/tools/ask_to_llm.py`
- `wenkb-server/server/core/tools/repos_vector_db.py`
- `wenkb-server/server/db/DbUpgrade.py`
- `wenkb-server/server/db/upgrade/ddl/0.sql`
- `wenkb-server/server/db/upgrade/ddl/1.sql`
- `wenkb-server/server/db/upgrade/ddl/4.sql`
- `wenkb-server/server/model/orm_knb.py`
- `docs/api_design.md`
- `tests/test_api_design.py`
- `tests/test_code_maintenance.py`

这些改动可能包含用户此前的导航修正，不应使用回退命令整体撤销。下次开始前应先查看 `git diff`，区分已有改动和新改动。

## 5. 验证状态

已完成过以下验证：

```powershell
.venv\Scripts\python.exe -m compileall -q wenkb-server/server wenkb-server/app.py
.venv\Scripts\python.exe -m unittest discover -s tests
```

此前一次测试结果为 `Ran 16 tests - OK`。但该结果发生在数据库索引错误 ORM、数据库版本号和队列错误记录逻辑再次调整之前，因此不能作为当前工作区最终通过的依据。

暂停前尚未重新完成以下验证：

```powershell
.venv\Scripts\python.exe -m compileall -q wenkb-server/server wenkb-server/app.py
.venv\Scripts\python.exe -m unittest discover -s tests
```

特别注意：当前 `tests/test_code_maintenance.py` 仍然检查版本号 `4`，而代码中的 `DB_SCHEMA_VERSION` 已为 `5`。在未更新测试和完成 `ddl/5.sql` 前，完整测试结果不应标记为通过。

## 6. 下次恢复建议

1. 先运行 `git status --short` 和 `git diff --stat`，确认没有新的用户改动。
2. 先完成数据库迁移和测试断言修正，确保数据库版本链路闭合。
3. 再处理聊天失败落库，补充失败路径测试。
4. 统一抽取或复用资源访问权限校验，逐组补充接口测试。
5. 运行编译、完整测试和必要的 SQLite 升级验证。
6. 检查差异后按仓库规则创建 Git commit。

