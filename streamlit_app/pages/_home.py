import streamlit as st
import core
from pathlib import Path
import base64
import html
from functools import lru_cache


APP_DIR = Path(__file__).resolve().parents[1]
ASSETS_DIR = APP_DIR / "assets"


st.markdown(
    """
<style>
/* Keep slide-like rows: icon block at left, text at right */
.dimension-row {
    display: grid;
    grid-template-columns: 152px 1fr;
    gap: 0.9rem;
    align-items: start;
    margin-bottom: 0.9rem;
}

.dimension-row:last-child {
    margin-bottom: 0;
}

.dimension-icon {
    width: 100%;
    max-width: 152px;
    height: auto;
    display: block;
}

.dimension-title {
    font-weight: 700;
    margin: 0 0 0.25rem 0;
}

.dimension-description {
    margin: 0;
    line-height: 1.45;
}

.dimension-pair-spacer {
    height: 0.95rem;
}

/* Stack the two major columns on narrower windows */
@media (max-width: 1150px) {
    .st-key-riskgrid [data-testid="stHorizontalBlock"],
    .st-key-mitigationgrid [data-testid="stHorizontalBlock"] {
        flex-direction: column;
    }

    .dimension-row {
        grid-template-columns: 132px 1fr;
    }

    .dimension-icon {
        max-width: 132px;
    }
}

@media (max-width: 640px) {
    .dimension-row {
        grid-template-columns: 92px 1fr;
        gap: 0.75rem;
    }

    .dimension-icon {
        max-width: 92px;
    }
}
</style>
    """,
    unsafe_allow_html=True,
)


def _image_to_base64(path):
    with open(path, "rb") as file_obj:
        return base64.b64encode(file_obj.read()).decode("utf-8")


@lru_cache(maxsize=32)
def _get_icon_base64(prefix, idx):
    return _image_to_base64(ASSETS_DIR / f"{prefix}{idx}.png")


def _render_dimension_item(prefix, idx, item):
    img_b64 = _get_icon_base64(prefix, idx)
    title_html = html.escape(item["title"])
    desc_html = item["description_html"]
    st.markdown(
        f"""
<div class="dimension-row">
    <div>
        <img class="dimension-icon" src="data:image/png;base64,{img_b64}" alt="{title_html} icon" />
    </div>
    <div>
        <p class="dimension-title">{title_html}</p>
        <p class="dimension-description">{desc_html}</p>
    </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def _render_paired_dimension_section(left_title, left_prefix, left_items, right_title, right_prefix, right_items):
    header_left, header_right = st.columns(2, gap="large")
    with header_left:
        st.markdown(f"##### {left_title}")
    with header_right:
        st.markdown(f"##### {right_title}")

    total_rows = min(len(left_items), len(right_items))
    for idx, (left_item, right_item) in enumerate(zip(left_items, right_items), start=1):
        row_left, row_right = st.columns(2, gap="large")
        with row_left:
            _render_dimension_item(left_prefix, idx, left_item)
        with row_right:
            _render_dimension_item(right_prefix, idx, right_item)
        if idx < total_rows:
            st.markdown('<div class="dimension-pair-spacer"></div>', unsafe_allow_html=True)

logo_col, title_col = st.columns([1, 4])

with logo_col:
    st.image(str(APP_DIR / "assets/logo.png"), width=200)

with title_col:
    st.markdown("<h1 style='margin-bottom: 0;'>Meet the GenAI Risk Index</h1>", unsafe_allow_html=True)
    st.subheader("|*Assess risk in assessment design in the age of AI*")

st.markdown("---")

st.write(
    "GARI was designed to help educators quickly estimate the likelihood that an assessment could be vulnerable "
    "to unintentional or inappropriate use of generative AI. It is designed as a practical planning tool "
    "to support reflection, discussion, and improvement."
)


risk_descriptors_html = ", ".join(
    f"<span style='color:{core.CATEGORY_PALETTE[category]};font-weight:600'>{category}</span>"
    for category in core.RISK_CATEGORY_ORDER
)

st.markdown(
    "GARI evaluates four dimensions of assessment design that are relevant to generative AI risk: "
    "**Type**, **Delivery**, **Authenticity**, and **Guidance**. Each dimension is scored based on "
    "the presence of design features that may increase or decrease vulnerability to inappropriate AI use. "
    f"Finally, the resulting risk score maps to a category ({risk_descriptors_html}) to help educators "
    "identify where design adjustments may reduce risk.",
    unsafe_allow_html=True,
)

st.markdown("---")

st.subheader("The guts of GARI: dimensions and modifiers")

st.markdown("#### Risk dimensions")
with st.container(key="riskgrid"):
    _render_paired_dimension_section(
        "Type",
        "T",
        [
            {
                "title": "Extended Written",
                "description_html": "Extended written responses or data-driven investigations where students synthesise sources or produce original analysis. <em>Examples: literature review, lab report, design project.</em>",
            },
            {
                "title": "Creative/Multimedia",
                "description_html": "Outputs requiring verbal communication, visual design, or creative interpretation. <em>Examples: oral presentation, video submission, poster, artwork.</em>",
            },
            {
                "title": "Quiz/Exam",
                "description_html": "Structured assessments testing recall, problem-solving, or application under timed or invigilated conditions. <em>Examples: final or midsession quizzes.</em>",
            },
        ],
        "Delivery",
        "D",
        [
            {
                "title": "Online",
                "description_html": "Fully online submission or completion with no invigilation, enabling unrestricted access to generative AI tools.",
            },
            {
                "title": "Hybrid",
                "description_html": "Online submission or digital exam with some monitoring, or assessment with a mixed mode of submission.",
            },
            {
                "title": "In person",
                "description_html": "Conducted on campus without digital tools and/or under invigilated conditions, limiting AI use.",
            },
        ],
    )

st.markdown("#### Mitigation dimensions")
with st.container(key="mitigationgrid"):
    _render_paired_dimension_section(
        "Authenticity",
        "A",
        [
            {
                "title": "Nothing",
                "description_html": "Applies to any student, with no personalisation.",
            },
            {
                "title": "Personalised",
                "description_html": "Includes unique elements that are not easily generated by AI. <em>Examples: shared dataset or case study, lab experiment, personalised dataset, placement, fieldwork.</em>",
            },
            {
                "title": "Body of work",
                "description_html": "Uses observable progression of student learning across stages of creation.",
            },
        ],
        "Guidance",
        "G",
        [
            {
                "title": "Policy",
                "description_html": "Institutional AI policy.",
            },
            {
                "title": "Guideline",
                "description_html": "Explicit task-level guidance on appropriate AI use for the assessment.",
            },
            {
                "title": "Education",
                "description_html": "Explicit discussion, examples, or resources that educate students about appropriate AI use.",
            },
        ],
    )

st.markdown("### *Modifiers*")

st.markdown("Assessment weighting modifies the base risk score according to the percentage contribution of an individual assessment to the subject grade (ranging from 0-100).")

st.markdown("---")
st.subheader("Ready to give GARI a go?")

st.markdown(
    """
1. Open Risk Calculator from the sidebar.
2. Choose the *Single* tab for one assessment or *Batch* tab for multiple assessments.
3. Review the resulting score, risk category, and optional tips to reduce High or Critical risk outcomes.
"""
)


st.markdown("---")
st.info(
    """
    ### About the team
    GARI was developed by a dedicated team from the University of Wollongong School of Science: an interdisciplinary group focused on practical, evidence-informed approaches to assessment design in the context of generative AI. The team works with educators to make risk assessment understandable, transparent, and actionable.
    """
)
