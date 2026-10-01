from __future__ import annotations

from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "docs" / "images" / "module-structure"
WIDTH, HEIGHT = 2700, 1700
FONT = Path(r"C:\Windows\Fonts\msyh.ttc")
FONT_BOLD = Path(r"C:\Windows\Fonts\msyhbd.ttc")

COLORS = {
    "ink": "#19324A",
    "muted": "#60788A",
    "line": "#C8D5DE",
    "input_fill": "#F2F7FA",
    "input_line": "#75A2B8",
    "service_fill": "#FFF9ED",
    "service_line": "#D2B45E",
    "storage_fill": "#F1F7F3",
    "storage_line": "#77A98D",
    "external_fill": "#FFF3EE",
    "external_line": "#CD866B",
    "note_fill": "#F7F9FB",
}


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    path = FONT_BOLD if bold else FONT
    return ImageFont.truetype(str(path), size)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    box = draw.multiline_textbbox((0, 0), text, font=font, spacing=8, align="center")
    return box[2] - box[0], box[3] - box[1]


def draw_centered(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: str = COLORS["ink"],
    spacing: int = 8,
) -> None:
    x1, y1, x2, y2 = box
    text_box = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    width = text_box[2] - text_box[0]
    height = text_box[3] - text_box[1]
    x = x1 + (x2 - x1 - width) / 2
    y = y1 + (y2 - y1 - height) / 2 - text_box[1]
    draw.multiline_text((x, y), text, font=font, fill=fill, spacing=spacing, align="center")


def rounded_box(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    fill: str,
    outline: str,
    radius: int = 24,
    width: int = 4,
) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str = COLORS["muted"],
    width: int = 7,
) -> None:
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=color, width=width)
    head = 22
    if x2 >= x1:
        points = [(x2, y2), (x2 - head, y2 - head), (x2 - head, y2 + head)]
    else:
        points = [(x2, y2), (x2 + head, y2 - head), (x2 + head, y2 + head)]
    draw.polygon(points, fill=color)


def draw_node(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    height: int,
    title: str,
    detail: str = "",
    fill: str = "#FFFFFF",
    outline: str = COLORS["line"],
    title_size: int = 34,
    detail_size: int = 25,
) -> None:
    box = (x, y, x + width, y + height)
    rounded_box(draw, box, fill, outline, radius=20, width=4)
    content = title if not detail else f"{title}\n{detail}"
    font = load_font(title_size if not detail else min(title_size, 32), bold=True)
    draw_centered(draw, box, content, font, fill=COLORS["ink"], spacing=9)


def draw_header(draw: ImageDraw.ImageDraw, title: str, subtitle: str) -> None:
    draw.text((120, 58), title, font=load_font(60, True), fill=COLORS["ink"])
    draw.text((124, 132), subtitle, font=load_font(30), fill=COLORS["muted"])
    draw.line((120, 194, WIDTH - 120, 194), fill=COLORS["line"], width=3)


def draw_column_label(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    width: int,
    height: int,
    text: str,
    fill: str,
    outline: str,
) -> None:
    rounded_box(draw, (x, y, x + width, y + height), fill, outline, radius=24, width=4)
    draw_centered(draw, (x, y, x + width, y + height), text, load_font(34, True), fill=COLORS["ink"])


def draw_footer(draw: ImageDraw.ImageDraw, text: str) -> None:
    draw.line((120, 1510, WIDTH - 120, 1510), fill=COLORS["line"], width=3)
    draw.text((125, 1560), text, font=load_font(27), fill=COLORS["muted"])


def make_diagram(
    slug: str,
    title: str,
    subtitle: str,
    inputs: Iterable[tuple[str, str]],
    services: Iterable[tuple[str, str]],
    resources: Iterable[tuple[str, str]],
    footer: str,
    service_color: str = COLORS["service_line"],
) -> Path:
    image = Image.new("RGB", (WIDTH, HEIGHT), "#FFFFFF")
    draw = ImageDraw.Draw(image)
    draw_header(draw, title, subtitle)

    left_x, left_w = 140, 560
    center_x, center_w = 850, 970
    right_x, right_w = 2000, 560
    top_y = 290
    node_h = 190
    gap = 52

    draw_column_label(draw, left_x, 235, left_w, 70, "输入 / 触发", COLORS["input_fill"], COLORS["input_line"])
    draw_column_label(draw, center_x, 235, center_w, 70, "模块核心处理", COLORS["service_fill"], service_color)
    draw_column_label(draw, right_x, 235, right_w, 70, "数据与外部依赖", COLORS["storage_fill"], COLORS["storage_line"])

    input_list = list(inputs)
    service_list = list(services)
    resource_list = list(resources)

    for index, (name, detail) in enumerate(input_list):
        y = top_y + index * (node_h + gap)
        draw_node(draw, left_x, y, left_w, node_h, name, detail, COLORS["input_fill"], COLORS["input_line"])

    service_y = top_y
    for index, (name, detail) in enumerate(service_list):
        y = service_y + index * (node_h + gap)
        draw_node(draw, center_x, y, center_w, node_h, name, detail, COLORS["service_fill"], service_color)

    for index, (name, detail) in enumerate(resource_list):
        y = top_y + index * (node_h + gap)
        fill = COLORS["external_fill"] if "服务" in name or "模型" in name else COLORS["storage_fill"]
        outline = COLORS["external_line"] if fill == COLORS["external_fill"] else COLORS["storage_line"]
        draw_node(draw, right_x, y, right_w, node_h, name, detail, fill, outline)

    input_center = [top_y + index * (node_h + gap) + node_h // 2 for index in range(len(input_list))]
    service_center = [service_y + index * (node_h + gap) + node_h // 2 for index in range(len(service_list))]
    resource_center = [top_y + index * (node_h + gap) + node_h // 2 for index in range(len(resource_list))]

    for index, y in enumerate(input_center):
        target = service_center[min(index, len(service_center) - 1)]
        arrow(draw, (left_x + left_w, y), (center_x - 18, target))

    for index, y in enumerate(service_center):
        target = resource_center[min(index, len(resource_center) - 1)]
        arrow(draw, (center_x + center_w, y), (right_x - 18, target))

    # Add a visible vertical flow cue where the module has more core steps than
    # external dependencies, so Word readers can follow the internal sequence.
    for current, next_y in zip(service_center, service_center[1:]):
        draw.line((center_x + center_w // 2, current + node_h // 2 - 8, center_x + center_w // 2, next_y - node_h // 2 + 8),
                  fill=service_color, width=4)

    draw_footer(draw, footer)
    output = OUTPUT_DIR / f"{slug}.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    image.save(output, dpi=(300, 300), optimize=True)
    return output


def generate_all() -> list[Path]:
    diagrams = [
        (
            "01-model-configuration",
            "模型配置模块结构",
            "负责供应商、模型、参数和用户首选项的统一管理",
            [
                ("用户 / 管理界面", "配置供应商、模型与参数"),
                ("系统初始化", "加载内置供应商与模型"),
            ],
            [
                ("供应商管理", "查询可用供应商和支持的模型类型"),
                ("模型与参数管理", "保存模型实例、参数定义和值"),
                ("首选项管理", "维护默认 LLM 与 embedding 模型"),
            ],
            [
                ("关系型数据库", "供应商、模型、参数、首选项"),
                ("敏感信息保护", "API Key 加密存储、脱敏回显"),
                ("大语言模型 / Embedding 服务", "运行时模型适配与调用"),
            ],
            "调用方向：配置请求 → 参数校验 → 持久化 → 运行时解析模型实例",
        ),
        (
            "02-knowledge-base",
            "知识库管理模块结构",
            "作为数据集、对话和搜索记录的业务归属容器",
            [
                ("用户操作", "创建、查看、编辑和删除知识库"),
                ("知识库维护", "调整权限、问答参数和问答对"),
            ],
            [
                ("知识库基本信息", "名称、描述、权限范围与绑定模型"),
                ("知识库设置", "问答参数、检索参数和运行配置"),
                ("关联对象管理", "目录、数据集、对话、搜索历史、问答对"),
            ],
            [
                ("关系型数据库", "repository / setting / QA\n及关联关系"),
                ("向量数据库", "按知识库维护 Collection"),
                ("清理与一致性处理", "删除时同步处理关联对象和索引"),
            ],
            "调用方向：知识库操作 → 权限校验 → 事务保存 → 关联对象与索引维护",
        ),
        (
            "03-dataset-management",
            "数据集管理模块结构",
            "负责文件、网页链接及其衍生知识对象的全生命周期管理",
            [
                ("文件上传", "文档文件与文件元数据"),
                ("网页导入", "链接数组与网页标题"),
                ("维护操作", "目录、启用状态、重建和删除"),
            ],
            [
                ("资料接入", "文件解析入口、网页链接登记"),
                ("数据集与目录", "数据集基本信息、分类和排序"),
                ("衍生知识对象", "分段、摘要、问答对、三元组"),
                ("状态与错误", "启用、索引、增强状态和错误记录"),
            ],
            [
                ("关系型数据库", "dataset / catalog / chunk\nsummary / QA / triplet"),
                ("本地文件系统", "原始资料、解析中间文件"),
                ("后台任务", "触发索引构建和知识增强"),
            ],
            "调用方向：资料导入 → 数据集登记 → 状态管理 → 索引与增强任务",
        ),
        (
            "04-index-building",
            "索引构建模块结构",
            "将原始资料转换为可语义检索的向量索引",
            [
                ("数据集导入完成", "主索引进入 new / order 状态"),
                ("重建索引请求", "用户触发指定数据集或类型重建"),
                ("后台任务调度", "扫描待处理任务并执行"),
            ],
            [
                ("资料解析", "读取文件或网页内容并统一为文本"),
                ("文本切分", "生成带顺序和来源信息的文档分段"),
                ("向量化", "调用 embedding 模型生成向量"),
                ("索引写入与状态回写", "写入向量库并更新 ready / error"),
            ],
            [
                ("本地文件系统", "原始资料与解析中间文件"),
                ("Embedding 服务", "文本向量生成"),
                ("向量数据库", "chunk 向量及来源元数据"),
                ("关系型数据库", "数据集状态与 index error"),
            ],
            "状态流转：new → order → index → ready；失败时转为 error 并支持重试",
        ),
        (
            "05-chat-retrieval",
            "问答与检索模块结构",
            "基于知识库检索结果和历史上下文生成可追溯回答",
            [
                ("用户问题", "选择知识库并发送消息"),
                ("历史对话", "加载消息链路和上下文"),
            ],
            [
                ("对话与消息管理", "保存用户消息、助手消息和重生成关系"),
                ("知识检索", "按知识库查询相关分段、摘要、QA 或三元组"),
                ("提示词与回答生成", "拼接上下文并调用 LLM"),
                ("流式输出与引用", "发送片段、引用、错误并保存最终结果"),
            ],
            [
                ("向量数据库", "语义检索候选结果"),
                ("关系型数据库", "chat / message / quote\n及来源快照"),
                ("大语言模型服务", "流式生成回答"),
            ],
            "调用方向：消息落库 → 检索 → 提示词编排 → SSE 输出 → 回答与引用落库",
        ),
        (
            "06-enhancement-generation",
            "增强生成模块结构",
            "在主索引完成后生成摘要、问答对和三元组等结构化知识",
            [
                ("主索引完成", "仅对 ready 数据集触发增强"),
                ("后台增强任务", "按摘要、QA、三元组分别排队执行"),
            ],
            [
                ("片段读取", "读取已切分的文档片段"),
                ("摘要生成", "批量生成和维护数据集摘要"),
                ("问答生成", "生成可检索的知识库问答对"),
                ("三元组抽取", "抽取主体、关系和客体"),
                ("结果保存与同步", "写回数据库并同步向量索引"),
            ],
            [
                ("大语言模型服务", "摘要、问答和结构化抽取"),
                ("关系型数据库", "summary / QA / triplet\n及任务状态"),
                ("向量数据库", "增强对象的语义检索向量"),
            ],
            "状态约束：主索引 ready → 增强任务执行 → 结果保存 → 向量同步",
        ),
        (
            "07-search",
            "搜索模块结构",
            "提供面向指定知识库的语义搜索和搜索历史管理",
            [
                ("搜索请求", "知识库、搜索文本和历史记录开关"),
                ("历史操作", "查询或删除当前用户搜索历史"),
            ],
            [
                ("查询处理", "校验知识库权限和搜索条件"),
                ("语义检索", "将查询向量化并检索匹配对象"),
                ("结果整理", "补充来源名称、类型、分数和片段"),
                ("历史记录", "按用户和知识库保存、查询、删除"),
            ],
            [
                ("Embedding 服务", "生成查询向量"),
                ("向量数据库", "按知识库执行相似度检索"),
                ("关系型数据库", "搜索历史与来源业务数据"),
            ],
            "调用方向：查询条件 → 向量检索 → 来源补全 → 结果返回与历史记录",
        ),
        (
            "08-document-orchestration",
            "文档与编排模块结构",
            "管理文档集、文档版本，并支持文档转入知识库",
            [
                ("文档集操作", "创建、查询、编辑和权限维护"),
                ("文档编辑", "层级、标题、内容和状态维护"),
                ("转换请求", "选择文档或版本转为数据集"),
            ],
            [
                ("文档集管理", "维护文档集基本信息和可见范围"),
                ("文档与层级管理", "维护父子关系、路径和正文"),
                ("版本管理", "保存内容更新形成的版本快照"),
                ("文档转数据集", "记录来源并调用数据集导入流程"),
            ],
            [
                ("关系型数据库", "docset / document / version"),
                ("数据集管理服务", "接收文档转换结果"),
                ("索引与向量存储", "转换后进入切分、索引和检索流程"),
            ],
            "调用方向：文档编辑 → 版本快照 → 转数据集 → 索引构建与知识检索",
        ),
    ]
    return [
        make_diagram(
            slug,
            title,
            subtitle,
            inputs,
            services,
            resources,
            footer,
        )
        for slug, title, subtitle, inputs, services, resources, footer in diagrams
    ]


if __name__ == "__main__":
    for path in generate_all():
        print(path)
