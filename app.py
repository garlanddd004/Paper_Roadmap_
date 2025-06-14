import streamlit as st
from pdf_utils import extract_text_from_pdf
from agent_extract import extract_steps_from_text
from mermaid_generator import steps_to_mermaid
from svg_renderer import render_mermaid_to_svg
import re
import os

st.title("🎯 科研技术路线图 Agent Demo")

uploaded_file = st.file_uploader("📄 上传你的论文 PDF", type="pdf")

if uploaded_file:
    # 保存上传的 PDF
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())

    # 1. 提取全文
    st.info("📃 正在解析论文内容...")
    text = extract_text_from_pdf("temp.pdf")
    st.success("✅ 提取完成！")

    # 2. 摘要预览
    def extract_abstract(text):
        match = re.search(r"(摘要|Abstract)[\s:：]*(.*?)(\n\s*\n|\Z)",
                          text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(2).strip()
        return ""

    st.subheader("📑 论文摘要预览")
    abstract = extract_abstract(text)
    if abstract:
        preview_length = 500
        st.code(abstract[:preview_length] + ("..." if len(abstract) > preview_length else ""),
                language="markdown")
    else:
        st.warning("⚠️ 未识别到摘要段落，展示正文前 500 字供参考：")
        st.code(text[:500] + "...", language="markdown")

    # 质量检查
    if len(text.strip()) < 100:
        st.error("❌ 提取的文本内容过少，PDF 可能为扫描件或图片格式。请上传文本型PDF。")
        st.stop()

    # 3. 调用 LLM 提取双轨结构
    st.info("🧠 调用 LLM 提取科研步骤中...")
    roadmap = extract_steps_from_text(text)
    content_steps = roadmap.get("content_steps", [])
    process_steps = roadmap.get("process_steps", [])

    # 4. 检查是否真正提取到内容
    if not content_steps or not process_steps:
        st.error("❌ 未能提取出完整的技术路线图结构，请检查论文内容或提取配置。")
        st.stop()

    st.success(f"✅ 结构抽取完成！科研内容 {len(content_steps)} 步，研究过程 {len(process_steps)} 步。")

    # 5. 生成 Mermaid DSL
    mermaid_code = steps_to_mermaid(content_steps, process_steps)
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/diagram.mmd", "w", encoding="utf-8") as f:
        f.write(mermaid_code)

    st.subheader("📜 Mermaid 代码")
    st.code(mermaid_code, language="markdown")

    # 6. 渲染并展示 SVG
    st.info("🎨 正在生成 SVG 图...")
    render_mermaid_to_svg(mermaid_code, "outputs")
    st.image("outputs/diagram.svg", use_container_width=True)

    st.success("✅ 完成！你可以下载 SVG 图。")
