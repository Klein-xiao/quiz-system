import re
from pypdf import PdfReader
from io import BytesIO

# 需要过滤的水印/广告关键词列表
WATERMARK_KEYWORDS = [
    "IT 认证轻松过",
    "IT认证轻松过",
    "Examtopics",
    "PMBOK7",
    "英⽂⽆答案版",
    "英文无答案版",
    "下载时间",
    "使⽤指南",
    "使用指南",
    "章节与题序",
    "答案参考",
    "扫码关注",
    "淘宝",
    "闲⻥",
    "闲鱼",
    "微信",
    "考试主题",
    "主题 1",
    "主题1",
    "Topic 1",
    "Topic1"
]


def clean_watermarks(text: str) -> str:
    """清理包含 '/' 到 ': IT' 之间的跨行水印以及其他广告关键词"""
    # 1. 消除类似 '/' 到 ': IT' 或 ':IT' 及其随后的水印碎片（跨行匹配）
    text = re.sub(r'/\s*\n?\s*:\s*IT[\s\S]*?(?=\n\n|\n[A-D]\.|\n[一-龥]|$)', '', text)
    text = re.sub(r'/\s*:\s*IT.*', '', text)
    text = re.sub(r'认证轻松过.*', '', text)

    lines = text.splitlines()
    cleaned_lines = []

    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue

        # 2. 过滤显式水印关键词
        if any(keyword in line_str for keyword in WATERMARK_KEYWORDS):
            continue

        # 3. 过滤残留的单独标点符号或单字碎片（如仅有 '/' 或仅有 '信'）
        if line_str in ["/", ":", "信", "微", "信:"]:
            continue

        cleaned_lines.append(line_str)

    return "\n".join(cleaned_lines)


def contains_chinese(text: str) -> bool:
    """判断文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fa5]', text))


def parse_pdf_questions(pdf_bytes: bytes):
    reader = PdfReader(BytesIO(pdf_bytes))
    full_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            cleaned = clean_watermarks(text)
            if cleaned:
                full_text += cleaned + "\n"

    # 按中文题号“问题 #数字”切割
    raw_blocks = re.split(r'\n(?=(?:主题\s*\d+\s*)?问题\s*#\d+)', full_text)

    parsed = []
    for block in raw_blocks:
        content = block.strip()
        if not content:
            continue

        # 匹配题号（例如 问题 #21 或 问题#21）
        match = re.search(r'问题\s*#\s*(\d+)', content)
        if match:
            q_num = match.group(1)

            # 按行进一步过滤，仅保留中文相关的行（包含中文题干、中文选项以及题号）
            lines = content.splitlines()
            valid_lines = []

            for line in lines:
                l_str = line.strip()
                if not l_str:
                    continue

                # 过滤“Question #22”这类英文题号行
                if re.match(r'^Question\s*#\d+', l_str, re.IGNORECASE):
                    continue

                # 保留“问题 #X”行，或者包含中文字符的行（题目和中文选项）
                if "问题" in l_str or contains_chinese(l_str):
                    # 抹去开头的“主题 X”字样
                    l_str = re.sub(r'^\s*主题\s*\d+\s*', '', l_str)
                    valid_lines.append(l_str)

            final_content = "\n".join(valid_lines).strip()

            # 确保提取出的题目既有题干又有实际内容
            if final_content and len(final_content) > 10:
                parsed.append({
                    "q_num": q_num,
                    "content": final_content
                })

    return parsed