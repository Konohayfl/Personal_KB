from __future__ import annotations

import argparse
import re
from pathlib import Path

import fitz


PAGE_WIDTH = 594.96
PROJECT_RECT = fitz.Rect(30, 397, 565, 582)
BODY_X = 35.7
BODY_INDENT_X = 46.41
BODY_RIGHT = 559.4
BODY_FONT_SIZE = 8.925
BODY_LINE_HEIGHT = 10.11
TITLE_BASELINE = 410.08
BODY_FIRST_BASELINE = 424.35

PROJECT_BODY = [
    (
        "bullet",
        "这是一个面向个人与小团队的本地 AI 知识工作台，基于 FastAPI + Vue3/Tauri + SQLite + Chroma 构建，"
        "支持知识库管理、资料导入、语义检索与问答。",
    ),
    ("label", "Situation："),
    (
        "bullet",
        "针对学习资料、研发文档和网页内容分散、检索效率低且答案缺少依据的问题，打通“导入 - 索引 - 检索 - 问答 - 沉淀”闭环。",
    ),
    ("label", "Task："),
    (
        "bullet",
        "负责知识库、数据集、向量索引和问答链路设计，落地多模型配置、文档解析切分、异步处理、RAG 检索和引用溯源。",
    ),
    ("label", "Action："),
    (
        "bullet",
        "模型适配与安全：封装 OpenAI 兼容、Ollama 和本地 HuggingFace embedding 客户端，支持模型首选项、参数覆盖、API Key 加密与脱敏。",
    ),
    (
        "bullet",
        "索引与知识增强：按知识库持久化 Chroma 向量集合，支持 PDF、DOCX、TXT、PPT/PPTX、Markdown 和网页链接导入，以及摘要、Q&A、三元组增强。",
    ),
    (
        "bullet",
        "问答与可靠性：结合 TopK、相似度阈值和历史对话组装上下文，通过 SSE 流式生成并保存引用快照，支持失败回退、重试和级联清理。",
    ),
    ("label", "Result："),
    (
        "bullet",
        "形成可本地部署的知识库产品闭环，支持资料管理、语义搜索、多轮问答、来源查看和文档沉淀，并配套工程文档与回归测试。",
    ),
]


def _font_path() -> Path:
    candidates = (
        Path(r"C:\Windows\Fonts\msyh.ttc"),
        Path(r"C:\Windows\Fonts\simsun.ttc"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("未找到可用于中文排版的 Windows 字体")


def _bold_font_path() -> Path:
    candidates = (
        Path(r"C:\Windows\Fonts\msyhbd.ttc"),
        Path(r"C:\Windows\Fonts\simsunb.ttf"),
        _font_path(),
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError("未找到可用于中文标题排版的字体")


def _wrap_text(text: str, font: fitz.Font, max_width: float) -> list[str]:
    lines: list[str] = []
    current = ""
    units: list[str] = []
    index = 0
    while index < len(text):
        char = text[index]
        if re.match(r"[A-Za-z0-9]", char):
            match = re.match(r"[A-Za-z0-9][A-Za-z0-9_+./-]*", text[index:])
            assert match is not None
            units.append(match.group(0))
            index += len(match.group(0))
        else:
            units.append(char)
            index += 1

    for unit in units:
        candidate = current + unit
        if current and font.text_length(candidate, fontsize=BODY_FONT_SIZE) > max_width:
            lines.append(current.rstrip())
            current = unit.lstrip()
        else:
            current = candidate
    if current:
        lines.append(current.rstrip())
    return lines or [""]


def _insert_text(
    page: fitz.Page,
    point: tuple[float, float],
    text: str,
    *,
    fontname: str,
    fontfile: str,
    size: float,
    color: int,
) -> None:
    page.insert_text(
        point,
        text,
        fontname=fontname,
        fontfile=fontfile,
        fontsize=size,
        color=fitz.sRGB_to_pdf(color),
        overlay=True,
    )


def replace_project(input_pdf: Path, output_pdf: Path) -> None:
    if not input_pdf.is_file():
        raise FileNotFoundError(f"简历文件不存在: {input_pdf}")

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    font_path = str(_font_path())
    bold_font_path = str(_bold_font_path())
    document = fitz.open(input_pdf)
    if len(document) != 1:
        raise ValueError(f"预期单页简历，实际页数为 {len(document)}")

    page = document[0]
    if abs(page.rect.width - PAGE_WIDTH) > 1 or abs(page.rect.height - 841.92) > 1:
        raise ValueError("输入简历不是预期的 A4 页面")

    page.add_redact_annot(PROJECT_RECT, fill=(1, 1, 1))
    page.apply_redactions()

    _insert_text(
        page,
        (35.7, TITLE_BASELINE),
        "WenKB 知识库",
        fontname="resume-title",
        fontfile=bold_font_path,
        size=9.52,
        color=0x000000,
    )
    _insert_text(
        page,
        (105.315, TITLE_BASELINE),
        "核心开发",
        fontname="resume-role",
        fontfile=font_path,
        size=8.33,
        color=0x586765,
    )
    _insert_text(
        page,
        (493.85, TITLE_BASELINE),
        "2026-05 至 2026-06",
        fontname="resume-date",
        fontfile=font_path,
        size=6.7,
        color=0x999999,
    )

    body_font = fitz.Font(fontfile=font_path)
    baseline = BODY_FIRST_BASELINE
    for kind, text in PROJECT_BODY:
        if kind == "label":
            _insert_text(
                page,
                (BODY_X, baseline),
                text,
                fontname="resume-body-label",
                fontfile=font_path,
                size=BODY_FONT_SIZE,
                color=0x333333,
            )
            baseline += BODY_LINE_HEIGHT
            continue

        first_prefix = "· "
        first_width = BODY_RIGHT - BODY_INDENT_X
        lines = _wrap_text(
            text,
            body_font,
            first_width - body_font.text_length(first_prefix, fontsize=BODY_FONT_SIZE),
        )
        _insert_text(
            page,
            (BODY_INDENT_X, baseline),
            first_prefix + lines[0],
            fontname="resume-body",
            fontfile=font_path,
            size=BODY_FONT_SIZE,
            color=0x333333,
        )
        baseline += BODY_LINE_HEIGHT
        for line in lines[1:]:
            wrapped = _wrap_text(line, body_font, BODY_RIGHT - BODY_X)[0]
            _insert_text(
                page,
                (BODY_X, baseline),
                wrapped,
                fontname="resume-body",
                fontfile=font_path,
                size=BODY_FONT_SIZE,
                color=0x333333,
            )
            baseline += BODY_LINE_HEIGHT

    if baseline > PROJECT_RECT.y1 - 2:
        raise ValueError(f"项目内容超出原区域，末行基线为 {baseline:.2f}")

    document.save(output_pdf, garbage=4, deflate=True)
    document.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="替换简历中的首个项目经历")
    parser.add_argument("input_pdf", type=Path)
    parser.add_argument("output_pdf", type=Path)
    args = parser.parse_args()
    replace_project(args.input_pdf, args.output_pdf)


if __name__ == "__main__":
    main()
