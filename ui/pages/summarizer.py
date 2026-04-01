"""
Summarizer page with configurable detail and output structure.
"""
import time

import httpx
import streamlit as st

from app.config import API_HOST, API_PORT

API_BASE = f"http://{API_HOST}:{API_PORT}"


def render_summarizer_page():
    st.markdown(
        """
    <h1 style="font-size:2rem; margin-bottom:0.2rem;">Note Summarizer</h1>
    <p style="color:#94a3b8; margin-bottom:1.5rem;">
        Upload any PDF, DOCX, or TXT file and get a local AI summary with flexible depth and structure.
    </p>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class="card" style="padding:0.8rem 1.2rem; margin-bottom:1.5rem;">
        <span class="privacy-badge">Your file never leaves this device</span>
        &nbsp; Text is processed by a local LLM running on your machine.
    </div>
    """,
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Drop your file here or click to browse",
        type=["pdf", "docx", "txt"],
        help="Supports PDF, Word documents, and plain text files",
    )

    option_col1, option_col2 = st.columns(2)
    with option_col1:
        detail_level = st.selectbox(
            "Detail level",
            options=["concise", "standard", "detailed"],
            index=1,
            help="Choose how deep the summary should go.",
        )
    with option_col2:
        format_type = st.selectbox(
            "Summary format",
            options=["structured", "study_guide", "plain"],
            index=0,
            help="Structured modes produce topic and subtopic breakdowns.",
        )

    st.caption(
        "For topic-wise and subtopic-wise output, use `detailed` with `structured` or `study_guide`."
    )

    col1, col2 = st.columns([2, 1])

    if uploaded_file is not None:
        file_size_kb = round(len(uploaded_file.getvalue()) / 1024, 1)
        file_ext = uploaded_file.name.split(".")[-1].upper()
        ext_colors = {"PDF": "#ef4444", "DOCX": "#3b82f6", "TXT": "#10b981"}
        color = ext_colors.get(file_ext, "#6366f1")

        with col1:
            st.markdown(
                f"""
            <div class="card" style="padding:1.2rem;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <div style="background:{color}22; border:1px solid {color}44;
                         border-radius:8px; padding:8px 14px; color:{color}; font-weight:700; font-size:0.9rem;">
                        {file_ext}
                    </div>
                    <div>
                        <div style="font-weight:600; color:#e2e8f0;">{uploaded_file.name}</div>
                        <div style="font-size:0.8rem; color:#94a3b8;">{file_size_kb} KB</div>
                    </div>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            summarize_btn = st.button(
                "Generate Summary",
                use_container_width=True,
                type="primary",
            )

        if summarize_btn:
            _run_summarization(uploaded_file, detail_level, format_type)


def _run_summarization(uploaded_file, detail_level: str, format_type: str):
    progress_placeholder = st.empty()

    with progress_placeholder.container():
        progress_bar = st.progress(0, text="Uploading file to local backend...")
        time.sleep(0.3)
        progress_bar.progress(20, text="Extracting text from document...")
        time.sleep(0.3)

    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        data = {
            "detail_level": detail_level,
            "format_type": format_type,
        }
        progress_placeholder.empty()

        with st.spinner("Local model is summarizing... this can take a while on CPU"):
            start = time.time()
            resp = httpx.post(
                f"{API_BASE}/summarize",
                files=files,
                data=data,
                timeout=300,
            )
            elapsed = round(time.time() - start, 1)

        if resp.status_code == 200:
            payload = resp.json()
            summary = payload.get("summary", "No summary generated.")
            chunk_count = payload.get("chunk_count", "N/A")

            st.success(f"Summary generated in {elapsed}s")

            st.markdown(
                """
            <div class="card">
                <h3 style="color:#818cf8; margin-top:0;">Summary</h3>
            """,
                unsafe_allow_html=True,
            )
            st.markdown(summary)
            st.markdown("</div>", unsafe_allow_html=True)

            word_count = len(summary.split())

            col1, col2, col3 = st.columns(3)
            col1.metric("Time", f"{elapsed}s")
            col2.metric("Summary Words", word_count)
            col3.metric("Chunks", chunk_count)

            col4, col5 = st.columns(2)
            col4.metric("Detail", detail_level.title())
            col5.metric("Format", format_type.replace("_", " ").title())

            st.download_button(
                "Download Summary",
                data=summary,
                file_name=f"summary_{uploaded_file.name.rsplit('.', 1)[0]}.txt",
                mime="text/plain",
            )
        else:
            st.error(f"Error: {resp.text}")

    except httpx.ConnectError:
        st.error("Backend not running. Start it with: `uvicorn app.main:app --port 8000`")
    except Exception as exc:
        st.error(f"Unexpected error: {str(exc)}")
