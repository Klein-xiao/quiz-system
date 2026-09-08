import re
from io import BytesIO
import pandas as pd
from pypdf import PdfReader

# 文件路径配置
pdf_file_path = ""
csv_output_path = ""


def extract_pmp_answers_pypdf(pdf_path, output_csv):
    print(f"⏳ 开始读取 PDF 文件: {pdf_path}")

    # 1. 使用 BytesIO 读取文件入内存，再传递给 PdfReader
    try:
        with open(pdf_path, "rb") as f:
            pdf_bytes = BytesIO(f.read())
        reader = PdfReader(pdf_bytes)
    except Exception as e:
        print(f"❌ 打开文件失败，请检查文件路径: {e}")
        return

    results = []
    # 正则规则匹配题号（如 Question #1 或 Question 1）
    q_pattern = re.compile(r'Question\s*#?\s*(\d+)', re.IGNORECASE)
    # 正则规则匹配正确答案（如 Correct Answer: D 或 Correct Answer: ABD）
    a_pattern = re.compile(r'Correct\s*Answer:\s*([A-Za-f]+)', re.IGNORECASE)

    current_q_num = None

    # 2. 逐页提取纯文本
    for page_idx, page in enumerate(reader.pages):
        text = page.extract_text()
        if not text:
            continue

        for line in text.splitlines():
            line_str = line.strip()

            # 匹配题号
            q_match = q_pattern.search(line_str)
            if q_match:
                current_q_num = q_match.group(1)

            # 匹配答案
            a_match = a_pattern.search(line_str)
            if a_match and current_q_num is not None:
                correct_ans = a_match.group(1).upper()
                results.append({
                    "q_num": int(current_q_num),
                    "real_answer": correct_ans
                })
                current_q_num = None  # 重置状态

    # 3. 去重、排序并导出 CSV
    df = pd.DataFrame(results)
    if not df.empty:
        df = df.drop_duplicates(subset=['q_num']).sort_values(by='q_num')
        df.to_csv(output_csv, index=False, encoding='utf-8-sig')
        print(f"🎉 解析成功！共提取 {len(df)} 道题目的答案。")
        print(f"📁 已保存至 CSV 文件: {output_csv}")
    else:
        print("⚠️ 未在 PDF 中匹配到有效题号及答案。")


if __name__ == "__main__":
    extract_pmp_answers_pypdf(pdf_file_path, csv_output_path)