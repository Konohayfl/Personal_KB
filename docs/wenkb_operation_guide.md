# WenKB 操作文档与代码运行流程

## 1. 总体流程

WenKB 的主链路可以概括为：

`启动后端 -> 初始化数据库 -> 启动索引队列 -> 配置大模型 -> 创建知识库 -> 导入文档/链接 -> 构建向量索引 -> 在聊天页检索问答`

后端实际启动入口在 [app.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/app.py:80>)，代码里默认监听端口是 `16088`。

## 2. 代码运行流程

1. 启动时先执行数据库升级，然后在 lifespan 中启动两个后台任务：
   - 文档切分与向量化任务
   - 摘要 / Q&A / 三元组增强任务

2. 定时任务每 30 秒扫描一次待处理数据集：
   - `idxSts = new && enbSts = enb` 的数据集进入主索引队列
   - `prcsSts / qaSts / tpltSts = new` 的数据集进入增强队列

3. 主索引任务会：
   - 读取文件或网页内容
   - 按文本类型切分成 chunk
   - 写入数据库
   - 写入 Chroma 向量库

4. 问答任务会：
   - 根据知识库 ID 读取向量库
   - 按相似度检索相关片段
   - 拼接提示词
   - 调用用户选择的大模型流式返回答案

对应代码：
- [app.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/app.py:1>)
- [Scheduler.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/core/scheduler/Scheduler.py:11>)
- [DatasetToVectorQueue.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/core/queue/DatasetToVectorQueue.py:1>)
- [DatasetEnhanceVectorQueue.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/core/queue/DatasetEnhanceVectorQueue.py:1>)
- [dataset_to_vector.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/core/tools/dataset_to_vector.py:1>)
- [ask_to_llm.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/core/tools/ask_to_llm.py:1>)

## 3. 如何导入大模型

这里的“大模型”主要指聊天时使用的 LLM。

### 3.1 配置供应商

进入前端 `设置 -> 模型设置`，也就是 `/main/setting` 页面中的“模型设置”区域。

操作步骤：

1. 在“未设置模型”里找到目标供应商。
2. 点击“设置”，填写该供应商需要的参数，例如：
   - `api_key`
   - `base_url`
3. 如果供应商没有现成模型，点击“添加模型”补一个模型条目。

后端对应接口：
- `GET /sys/model/prvd/list`
- `POST /sys/model/param/prvd/{prvdId}`
- `POST /sys/model/prvd/modl/{prvdId}`

### 3.2 选择默认聊天模型

在“模型首选项”里选择 `LLM`。
这一步会写入用户的模型偏好，聊天时会优先使用这里的模型。

后端对应接口：
- `POST /sys/setting/user`

模型实际创建逻辑在：
- [SettingApi.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/api/sys/SettingApi.py:36>)
- [ModelPreference.vue](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-client/src/views/main/setting/llm/ModelPreference.vue:27>)

### 3.3 常见模型类型

- OpenAI / DeepSeek / Moonshot / 通义 / 智谱：通常配置 `api_key`
- Ollama：通常配置 `base_url`
- 默认本地 embedding：`default/m3e-small`

## 4. 如何导入知识库

知识库由“知识库本体 + 数据集 + 向量索引”组成。

### 4.1 新建知识库

进入 `/main/repository` 页面，点击“新建”：

1. 填写知识库名称。
2. 选择“索引”模型，也就是 embedding 模型。
3. 填写介绍。

默认索引模型是 `default/m3e-small`。
创建后一般不建议随意更改索引模型，因为已经构建好的向量库会和新模型不匹配。

对应代码：
- [RepositoryForm.vue](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-client/src/views/main/repository/form/RepositoryForm.vue:15>)
- [ReposInfoApi.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/api/knb/ReposInfoApi.py:81>)
- [llm_client_tools.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/core/tools/llm_client_tools.py:73>)

### 4.2 配置知识库参数

进入知识库详情页 `/main/repository/detail?id=...`，切到“设置”：

- `maxCtx`：每次送给大模型的上下文片段数
- `maxHist`：保留的历史对话轮数
- `llmTptur`：回答温度
- `smlrTrval`：相似度阈值
- `topK`：检索条数上限

对应页面：
- [RepositorySetting.vue](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-client/src/views/main/repository/setting/RepositorySetting.vue:1>)

### 4.3 导入文档

在知识库详情页的“数据集”页：

1. 点击“创建 -> 导入文档”。
2. 选择文件上传，支持 `PDF / DOCX / TXT / PPT / PPTX / MD`。
3. 上传后数据集记录会进入 `idxSts = new`。

后端会保存原文件，再由后台队列自动切分并构建索引。

注意：
- 扫描版 PDF 不支持
- 文档上传后默认 `enbSts = une`，需要启用后队列才会处理

对应代码：
- [DocumentImportForm.vue](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-client/src/views/main/repository/form/DocumentImportForm.vue:4>)
- [DatasetApi.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/api/knb/DatasetApi.py:58>)

### 4.4 导入网页链接

在“创建”菜单里选“网页链接”：

1. 每行输入一个 URL。
2. 系统会自动抓取网页标题。
3. 保存后数据集会直接启用，等待后台任务构建索引。

对应代码：
- [LinkImportForm.vue](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-client/src/views/main/repository/form/LinkImportForm.vue:4>)
- [DatasetApi.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/api/knb/DatasetApi.py:99>)

### 4.5 触发增强索引

主索引 ready 之后，可以在数据集列表里点击：

- 摘要
- Q&A
- 图谱

把状态从 `nobd` 改成 `new`，后台增强任务就会开始跑。

对应代码：
- [Dataset.vue](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-client/src/views/main/repository/Dataset.vue:379>)
- [DatasetEnhanceVectorQueue.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/core/queue/DatasetEnhanceVectorQueue.py:1>)
- [dataset_to_enhance.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/core/tools/dataset_to_enhance.py:1>)

## 5. 如何运用知识库进行问答

进入 `/main/chat` 页面：

1. 在左侧下拉框选择知识库。
2. 新建一个对话。
3. 输入问题并发送。

问答链路：

1. 前端把问题发到 `POST /knb/chat/message`。
2. 后端读取当前知识库设置。
3. 从向量库里找相关片段。
4. 用 `REPOSCHAT_PROMPT_TEMPLATE` 组装提示词。
5. 调用用户选择的大模型流式输出答案。
6. 返回引用来源，前端在消息里展示。

如果已有历史对话，系统还会先对历史内容做一次整理，再进入检索问答。

对应代码：
- [Chat.vue](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-client/src/views/main/Chat.vue:100>)
- [Content.vue](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-client/src/views/main/chat/Content.vue:107>)
- [ChatApi.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/api/knb/ChatApi.py:131>)
- [ask_to_llm.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/core/tools/ask_to_llm.py:41>)
- [llm_client_tools.py](<E:/111学习/4.1大四上/校内实习/wenkb-main/wenkb-server/server/core/tools/llm_client_tools.py:109>)

## 6. 常见排查点

1. 大模型回答异常
   - 检查供应商 `api_key` / `base_url`
   - 检查“模型首选项”是否选中了正确的 LLM

2. 知识库没有内容
   - 检查数据集是否 `enb = enb`
   - 检查 `idxSts` 是否已经 `ready`
   - 查看 `DatasetIndexError`

3. 检索不到答案
   - 检查知识库的 embedding 模型是否和已构建索引一致
   - 检查 `topK` 和 `smlrTrval`
   - 检查数据集是否真的被切分并写入向量库

4. 端口不一致
   - `README.md` 里写过 `6088`
   - 但 `app.py` 当前实际启动参数是 `16088`

