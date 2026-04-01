"""
Documents Q&A Page — Upload documents, index them, and ask questions (RAG).
"""
import streamlit as st
import httpx
from app.config import API_HOST, API_PORT

API_BASE = f"http://{API_HOST}:{API_PORT}"


def render_documents_page():
    st.markdown("""
    <h1 style="font-size:2rem; margin-bottom:0.2rem;">🔍 Document Q&A</h1>
    <p style="color:#94a3b8; margin-bottom:1.5rem;">
        Upload your documents, index them once, then ask questions in plain English.
        Powered by RAG — answers come from <em>your</em> documents, not the internet.
    </p>
    """, unsafe_allow_html=True)

    # ── RAG Explainer ─────────────────────────────────────────────────────
    with st.expander("ℹ️ How does this work? (RAG Pipeline)"):
        st.markdown("""
        1. **Upload** your PDF, DOCX, or TXT document
        2. **Index** it — text is split into chunks and converted to vector embeddings (stored in ChromaDB locally)
        3. **Ask** a question — your query is embedded and matched against the most relevant chunks
        4. **Answer** — the matched context is sent to the local LLM (Phi-3 Mini) which generates a grounded answer
        
        ✅ No internet. No cloud. Your documents never leave your machine.
        """)

    tab_upload, tab_qa = st.tabs(["📤 Upload & Index", "❓ Ask Questions"])

    # ── Tab 1: Upload & Index ──────────────────────────────────────────────
    with tab_upload:
        st.markdown("### Upload a Document")

        uploaded = st.file_uploader(
            "Choose a file to index",
            type=["pdf", "docx", "txt"],
            key="doc_uploader",
        )

        if uploaded:
            file_size = round(len(uploaded.getvalue()) / 1024, 1)
            st.markdown(f"**📄 {uploaded.name}** · {file_size} KB")

            if st.button("🔄 Index Document", type="primary", use_container_width=False):
                with st.spinner(f"🧠 Indexing '{uploaded.name}'... Generating embeddings locally..."):
                    try:
                        files = {"file": (uploaded.name, uploaded.getvalue(), uploaded.type)}
                        resp = httpx.post(
                            f"{API_BASE}/documents/upload",
                            files=files,
                            timeout=300,
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            st.success(f"✅ {data.get('message', 'Document indexed!')}")
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {resp.text}")
                    except httpx.ConnectError:
                        st.error("⚠️ Backend not running.")
                    except Exception as e:
                        st.error(str(e))

        # Indexed documents list
        st.markdown("---")
        st.markdown("### 📚 Indexed Documents")
        try:
            resp = httpx.get(f"{API_BASE}/documents/indexed", timeout=10)
            docs = resp.json() if resp.status_code == 200 else []
        except Exception:
            docs = []

        if not docs:
            st.info("📭 No documents indexed yet. Upload one above to get started.")
        else:
            for doc in docs:
                st.markdown(f"""
                <div class="card" style="padding:0.8rem 1.2rem;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-weight:600; color:#818cf8;">📄 {doc.get('filename')}</span><br/>
                            <span style="font-size:0.78rem; color:#94a3b8;">
                                {doc.get('chunk_count', 0)} chunks indexed · {doc.get('indexed_at', '')[:10]}
                            </span>
                        </div>
                        <span style="color:#10b981; font-size:0.8rem;">✅ Ready</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Tab 2: Ask Questions ───────────────────────────────────────────────
    with tab_qa:
        st.markdown("### Ask Questions About Your Documents")

        if "qa_history" not in st.session_state:
            st.session_state.qa_history = []

        # Example questions
        st.markdown("**💡 Example questions:**")
        examples = [
            "What is the main methodology described?",
            "Summarize the key findings",
            "What tools were used in this project?",
        ]
        cols = st.columns(3)
        for i, ex in enumerate(examples):
            if cols[i].button(ex, key=f"qa_ex_{i}", use_container_width=True):
                _ask_question(ex)

        query = st.text_input(
            "Your question",
            placeholder="Ask anything about your indexed documents...",
            key="qa_input",
        )
        if st.button("🔍 Search & Answer", type="primary") and query.strip():
            _ask_question(query)

        # Q&A History
        if st.session_state.qa_history:
            st.divider()
            st.markdown("### 📜 Q&A History")
            for item in reversed(st.session_state.qa_history):
                with st.expander(f"❓ {item['question'][:70]}..."):
                    st.markdown(item["answer"])


def _ask_question(query: str):
    with st.spinner("🔍 Searching documents and generating answer..."):
        try:
            resp = httpx.post(
                f"{API_BASE}/documents/query",
                json={"query": query},
                timeout=120,
            )
            if resp.status_code == 200:
                data = resp.json()
                answer = data.get("answer", "No answer found.")

                st.markdown("**📚 Answer from your documents:**")
                st.markdown(f"""
                <div class="card">
                    {answer}
                </div>
                """, unsafe_allow_html=True)

                st.session_state.qa_history.append({
                    "question": query,
                    "answer": answer,
                })
            else:
                st.error(f"❌ {resp.text}")
        except httpx.ConnectError:
            st.error("⚠️ Backend not running.")
        except Exception as e:
            st.error(str(e))
