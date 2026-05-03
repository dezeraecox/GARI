import streamlit as st

logo_col, title_col = st.columns([1, 4])
with logo_col:
    st.image("streamlit_app/assets/logo.png", width=200)
with title_col:
    st.markdown("<h1 style='margin-bottom: 0;'>Frequently Asked Questions</h1>", unsafe_allow_html=True)
    st.subheader("|*Find answers to the most common questions about GARI*")



with st.expander("What is GARI used for?"):
    st.write(
        "GARI is a practical planning tool to help educators estimate assessment vulnerability to inappropriate or unintended generative AI use. "
        "It supports reflection and redesign conversations rather than replacing professional judgement."
    )

with st.expander("How are risk scores calculated?"):
    st.write(
        "Each assessment is scored across Type, Delivery, Authenticity, and Guidance, then adjusted by assessment weighting. "
        "The resulting score maps to one of five descriptors: Insignificant, Minor, Moderate, High, or Critical."
    )

with st.expander("What do the risk categories mean?"):
    st.write(
        "Categories indicate relative risk bands, not certainty. Higher categories suggest the assessment may benefit from stronger authenticity design, clearer AI guidance, or other integrity-supporting adjustments."
    )
    st.markdown(
        """
- **Insignificant**
- **Minor**
- **Moderate**
- **High**
- **Critical**
"""
    )
    st.caption("Exact score cut-points are determined by the current calculator threshold settings.")

with st.expander("Should GARI be used for high-stakes decisions?"):
    st.write(
        "No. GARI should be used as decision support alongside educator expertise, institutional policy, and local context. "
        "It is not intended as a standalone compliance or disciplinary tool."
    )

with st.expander("What is the difference between Single and Batch modes?"):
    st.write(
        "Use Single mode to test one assessment quickly. Use Batch mode to upload a CSV and score many assessments at once, with downloadable results and summary charts."
    )

with st.expander("What columns are required for Batch mode?"):
    st.write(
        "Your CSV must include: type, delivery, authenticity, guidance, and weighting. "
        "Weighting must be numeric from 0 to 100."
    )

with st.expander("Are uploaded batch files stored?"):
    st.write(
        "Uploaded CSV files are used only to calculate results during your active session. "
        "They are not stored as long-term records by this app."
    )

with st.expander("Can I include extra columns in my batch CSV?"):
    st.write(
        "Yes. Additional columns are preserved in the output file so you can keep subject names, assessment IDs, or other metadata."
    )

with st.expander("Why were some batch rows marked invalid?"):
    st.write(
        "Rows are marked invalid when one or more required values are missing or outside accepted options (for example, unsupported category labels or weighting outside 0 to 100). "
        "Check the validation_error column in the output."
    )

with st.expander("How can I reduce an assessment's risk score?"):
    st.write(
        "Common approaches include increasing authenticity features, improving explicit student guidance on acceptable AI use, revising delivery conditions, and reviewing weighting in overall subject design."
    )

with st.expander("Who should I contact for support or feedback?"):
    st.write(
        "Open the Contact page (in the sidebar) to send questions or feedback directly to the GARI project team."
    )

st.markdown("---")
st.info("Still have questions? Use the Contact form to get in touch with the GARI team.")
