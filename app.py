"""Streamlit application for human evaluation of PDF documents.

Run with:
    streamlit run app.py
"""

import streamlit as st

from src.config_loader import load_criteria
from src.pdf_reader import list_pdfs, extract_text
from src.prompt_builder import format_criterion_for_display
from src.score_store import save_scores, get_scores


# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Human Judge", page_icon="", layout="wide")
st.title("Human Judge — Document Evaluation")

# ---------------------------------------------------------------------------
# Load criteria (cached so YAML is only read once per session)
# ---------------------------------------------------------------------------
@st.cache_data
def _load_criteria():
    return load_criteria()

criteria_cfg = _load_criteria()

# ---------------------------------------------------------------------------
# Sidebar — user identity & document picker
# ---------------------------------------------------------------------------
st.sidebar.header("Settings")

user_id = st.sidebar.text_input(
    "Your User ID",
    value="",
    help="Enter your name or identifier. This will be stored alongside your scores.",
)

pdfs = list_pdfs()
if not pdfs:
    st.warning("No PDF files found in the `input/` folder. Add PDFs there and reload.")
    st.stop()

selected_pdf = st.sidebar.selectbox(
    "Select a document",
    options=pdfs,
    format_func=lambda p: p.name,
)

# ---------------------------------------------------------------------------
# Tabs: Evaluate | Review Scores
# ---------------------------------------------------------------------------
tab_evaluate, tab_scores = st.tabs(["Evaluate", "Review Scores"])

# ========================== EVALUATE TAB ==================================
with tab_evaluate:
    if not user_id.strip():
        st.info("Please enter your User ID in the sidebar to begin evaluating.")
        st.stop()

    # Show document text
    with st.expander("Document text", expanded=False):
        try:
            text = extract_text(selected_pdf)
            st.text_area(
                "Extracted text",
                value=text,
                height=400,
                disabled=True,
                label_visibility="collapsed",
            )
        except Exception as e:
            st.error(f"Could not extract text: {e}")
            st.stop()

    st.markdown("---")
    st.subheader("Score each criterion")

    # Build form dynamically from criteria config
    with st.form("evaluation_form"):
        scores: dict[str, int] = {}
        justifications: dict[str, str] = {}

        for criterion in criteria_cfg.criteria:
            st.markdown(format_criterion_for_display(criterion))
            col_score, col_comment = st.columns([1, 3])

            with col_score:
                scores[criterion.id] = st.slider(
                    f"Score — {criterion.name}",
                    min_value=criterion.scale_min,
                    max_value=criterion.scale_max,
                    value=criterion.scale_min,
                    step=1,
                    key=f"score_{criterion.id}",
                    label_visibility="collapsed",
                )

            with col_comment:
                justifications[criterion.id] = st.text_input(
                    f"Comment (optional) — {criterion.name}",
                    key=f"comment_{criterion.id}",
                    label_visibility="collapsed",
                    placeholder="Optional comment...",
                )

            st.markdown("---")

        submitted = st.form_submit_button("Submit evaluation", type="primary")

    if submitted:
        evaluations = [
            {
                "criterion_id": cid,
                "score": score,
                "justification": justifications.get(cid, ""),
            }
            for cid, score in scores.items()
        ]
        save_scores(
            judge_type="human",
            user_id=user_id.strip(),
            document=selected_pdf.name,
            evaluations=evaluations,
        )
        st.success("Scores saved successfully!")

# ========================== REVIEW SCORES TAB ==============================
with tab_scores:
    st.subheader("Previously recorded scores")

    col_filter_doc, col_filter_type = st.columns(2)
    with col_filter_doc:
        filter_doc = st.selectbox(
            "Filter by document",
            options=["All"] + [p.name for p in pdfs],
            key="filter_doc",
        )
    with col_filter_type:
        filter_type = st.selectbox(
            "Filter by judge type",
            options=["All", "human", "llm"],
            key="filter_type",
        )

    doc_filter = None if filter_doc == "All" else filter_doc
    type_filter = None if filter_type == "All" else filter_type
    rows = get_scores(document=doc_filter, judge_type=type_filter)

    if not rows:
        st.info("No scores recorded yet.")
    else:
        st.dataframe(
            rows,
            use_container_width=True,
            column_order=[
                "id",
                "judge_type",
                "user_id",
                "document",
                "criterion_id",
                "score",
                "justification",
                "created_at",
            ],
        )
