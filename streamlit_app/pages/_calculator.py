import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import plotly.io as pio
import core
from copy import deepcopy
from pdf_reports import build_batch_pdf_report, build_single_pdf_report

logo_col, title_col = st.columns([1, 4])
with logo_col:
    st.image("streamlit_app/assets/logo.png", width=200)
with title_col:
    st.markdown("<h1 style='margin-bottom: 0;'>Calculator</h1>", unsafe_allow_html=True)
    st.subheader("|*See how assessment characteristics affect risk*")


def _to_csv_bytes(df):
    return df.to_csv(index=False).encode("utf-8")


def _show_contract_help():
    st.write(
        "Use Batch mode to score multiple assessments at once from an uploaded table. Start by downloading the template, then replace the example rows with your own assessment details (one row per assessment). Keep the column names unchanged so the calculator can read your file correctly. Accepted values are listed below:"
    )


    required = pd.DataFrame(
        [
            {"Column": "type", "Accepted values": ", ".join(core.TYPE_BATCH_DISPLAY_LABELS)},
            {"Column": "delivery", "Accepted values": ", ".join(core.DELIVERY_MAP.keys())},
            {"Column": "authenticity", "Accepted values": ", ".join(core.AUTHENTICITY_MAP.keys())},
            {"Column": "guidance", "Accepted values": ", ".join(core.GUIDANCE_MAP.keys())},
            {"Column": "weighting", "Accepted values": "Number from 0 to 100"},
        ]
    )
    st.dataframe(required, use_container_width=True, hide_index=True)

    st.caption(
        "💡 *You can include additional columns (for example, subject code or assessment name). These are preserved during scoring and returned in the output CSV.*"
    )
    st.caption(
        "🔒 *Privacy tip: Uploaded files are used only during your active session to generate results and are not stored as long-term records by this app.*"
    )


def _set_selection(store_key, state_key, value):
    selections = st.session_state.setdefault(store_key, {})
    selections[state_key] = value
    st.session_state[store_key] = selections


def _icon_choice(title, options, state_key, store_key):
    selections = st.session_state.setdefault(store_key, {})
    if state_key not in selections:
        selections[state_key] = options[0]["value"]
        st.session_state[store_key] = selections

    st.markdown(f"#### {title}")
    cols = st.columns(len(options), gap="small")
    for idx, option in enumerate(options):
        is_selected = selections[state_key] == option["value"]
        with cols[idx]:
            st.button(
                option["label"],
                key=f"{store_key}_{state_key}_{idx}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
                help=option.get("help"),
                on_click=_set_selection,
                args=(store_key, state_key, option["value"]),
            )

    return selections[state_key]


def _build_high_risk_tips(assessment_type, delivery, authenticity, guidance, weighting, category):
    tips = []

    if guidance == "Policy":
        tips.append("You could move beyond policy-only wording and add task-specific guidelines so students know exactly what AI support is and is not appropriate here.")
        tips.append("A quick in-class AI literacy moment (or short explainer video) can often shift this from policy to education with minimal redesign.")
    elif guidance == "Guideline":
        tips.append("You already have guidelines in place; consider a short education step (examples of acceptable vs unacceptable AI use) to lower risk further.")

    if assessment_type == "Report" and delivery == "Online":
        tips.append("Written reports submitted online are inherently higher risk, so adding a brief viva/check-in can help verify authorship and process.")

    if authenticity == "Nothing":
        tips.append("Consider adding a personalised element (e.g., local data, individual topic, or student-specific reflection) so generic AI outputs are less useful.")
    elif authenticity == "Personalised":
        tips.append("A staged body-of-work approach (proposal, draft checkpoint, final submission) can reduce risk without changing the task type.")

    if delivery == "Online":
        tips.append("If feasible, include one supervised or in-person checkpoint to reduce the risk introduced by fully online delivery.")

    if assessment_type == "Report":
        tips.append("You might split one large report into smaller components (e.g., outline, annotated sources, method note) to increase process visibility.")

    if weighting >= 50:
        tips.append("Because this task carries substantial weighting, consider reducing the percentage or spreading marks across multiple assessments to soften risk impact.")

    if category == "Critical":
        tips.append("For a critical rating, a practical first step is to change just one high-impact lever now (guidance or authenticity) and then recalculate.")

    tips.append("Small changes can make a big difference here—try one adjustment, recalculate, and iterate until the risk level is acceptable for your context.")

    ordered_unique_tips = list(dict.fromkeys(tips))
    return ordered_unique_tips[:7]


def _render_single_calculator():
    st.write("Select options for each dimension and choose an assessment weighting:")

    if "single_calculated" not in st.session_state:
        st.session_state["single_calculated"] = False

    type_options = [
        {
            "label": ":material/description: Extended Written",
            "value": "Report",
            "help": "Extended written responses or data-driven investigations\n(e.g., literature review, lab report, design project).",
        },
        {
            "label": ":material/brush: Creative/Multimedia",
            "value": "Creative",
            "help": "Outputs requiring verbal communication, visual design,\nor creative interpretation\n(e.g., presentation, video, poster, artwork).",
        },
        {
            "label": ":material/quiz: Quiz/Exam",
            "value": "Quiz/Exam",
            "help": "Structured assessments testing recall or application\nunder timed/invigilated conditions\n(e.g., quizzes, exams).",
        },
    ]
    delivery_options = [
        {
            "label": ":material/laptop_mac: Online",
            "value": "Online",
            "help": "Fully online submission or completion\nwith no invigilation.",
        },
        {
            "label": ":material/swap_horiz: Hybrid",
            "value": "Hybrid",
            "help": "Online submission with some monitoring\nor mixed-mode delivery.",
        },
        {
            "label": ":material/groups: In person",
            "value": "In person",
            "help": "On-campus, no digital tools\nand/or invigilated conditions.",
        },
    ]
    authenticity_options = [
        {
            "label": ":material/remove_circle_outline: Nothing",
            "value": "Nothing",
            "help": "Applies to any student\nwith no personalisation.",
        },
        {
            "label": ":material/fingerprint: Personalised",
            "value": "Personalised",
            "help": "Unique aspect for a student\n(e.g., shared dataset, case study,\nlab experiment, placement or fieldwork).",
        },
        {
            "label": ":material/library_books: Body of work",
            "value": "Body of work",
            "help": "Unique progression of student learning\nobserved frequently during creation.",
        },
    ]
    guidance_options = [
        {
            "label": ":material/gavel: Policy",
            "value": "Policy",
            "help": "Institutional AI policy\nin the subject outline.",
        },
        {
            "label": ":material/rule: Guideline",
            "value": "Guideline",
            "help": "Explicit task-level guidance\nprovided with the assessment.",
        },
        {
            "label": ":material/school: Education",
            "value": "Education",
            "help": "In-class discussion, examples, or resources\neducating students about appropriate AI use.",
        },
    ]

    sel_type = _icon_choice("Type", type_options, "type", "single_selections")
    sel_delivery = _icon_choice("Delivery", delivery_options, "delivery", "single_selections")
    sel_auth = _icon_choice("Authenticity", authenticity_options, "authenticity", "single_selections")
    sel_guidance = _icon_choice("Guidance", guidance_options, "guidance", "single_selections")

    weighting = st.slider("Assessment weighting (%)", min_value=0, max_value=100, value=100, key="single_weighting")

    st.text_input(
        "Assessment name (optional)",
        key="single_pdf_label",
        placeholder="e.g., BIOL101 Final Exam",
        help="Enter the assessment name and/or subject code to personalise the PDF title. Fill this in before clicking Calculate.",
    )

    calc_col, download_col = st.columns([1, 1])
    with calc_col:
        if st.button("Calculate", key="single_calculate"):
            st.session_state["single_calculated"] = True

    if st.session_state["single_calculated"]:
        adjusted, category = core.calculate_risk_score(
            assessment_type=sel_type,
            delivery=sel_delivery,
            authenticity=sel_auth,
            guidance=sel_guidance,
            weighting=weighting,
        )
        tips = []

        result_col, score_col = st.columns([4, 1], gap="small", vertical_alignment="center")
        color = core.CATEGORY_PALETTE.get(category, "#000000")
        html = f"""<div style='padding:14px 16px;border-radius:8px;background:{color};border-left:4px solid {color};min-height:74px;display:flex;align-items:center'>
        <span style='font-weight:bold; color:#fff;line-height:1.3'>The risk level of this assessment is: {category}</span>
        </div>"""
        with result_col:
            st.markdown(html, unsafe_allow_html=True)
        with score_col:
            st.metric("Risk Score", f"{adjusted:.2f}")

        st.markdown("---")

        label = st.session_state.get("single_pdf_label", "").strip()
        try:
            single_pdf = build_single_pdf_report(
                assessment_type=sel_type,
                delivery=sel_delivery,
                authenticity=sel_auth,
                guidance=sel_guidance,
                weighting=weighting,
                risk_score=adjusted,
                category=category,
                tips=tips,
                assessment_label=label if label else None,
            )
            file_name = f"gari_{label.replace(' ', '_')[:40]}_report.pdf" if label else "gari_report.pdf"
            with download_col:
                _, right_button_col = st.columns([1, 1])
                with right_button_col:
                    st.download_button(
                        "Download PDF report",
                        data=single_pdf,
                        file_name=file_name,
                        mime="application/pdf",
                        key="single_pdf_download",
                    )
        except Exception as ex:
            st.error(f"PDF export failed: {type(ex).__name__}: {str(ex)}")


        # Tips appear below download button
        if category in ["High", "Critical"]:
            st.subheader("| *Looking for simple ways to lower the risk?*")

            tips = _build_high_risk_tips(
                assessment_type=sel_type,
                delivery=sel_delivery,
                authenticity=sel_auth,
                guidance=sel_guidance,
                weighting=weighting,
                category=category,
            )
            st.markdown("\n".join(f"- {tip}" for tip in tips))

def _render_summary(scored):
    valid = scored[scored["is_valid"]]
    invalid = scored[~scored["is_valid"]]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Rows", len(scored))
    c2.metric("Valid", len(valid))
    c3.metric("Invalid", len(invalid))

    avg_score = valid["risk_score"].mean() if not valid.empty else None
    c4.metric("Avg risk score", f"{avg_score:.2f}" if avg_score is not None else "N/A")

    if not valid.empty:
        counts = (
            valid["risk_category"]
            .value_counts()
            .reindex(core.RISK_CATEGORY_ORDER, fill_value=0)
            .rename_axis("risk_category")
            .reset_index(name="count")
        )
        st.subheader("Risk distribution")
        st.vega_lite_chart(
            counts,
            {
                "mark": {"type": "bar", "cornerRadiusEnd": 4},
                "encoding": {
                    "y": {
                        "field": "risk_category",
                        "type": "nominal",
                        "sort": core.RISK_CATEGORY_ORDER,
                        "title": "Risk category",
                    },
                    "x": {
                        "field": "count",
                        "type": "quantitative",
                        "title": "Assessments",
                        "scale": {"domainMin": 0, "nice": True, "zero": True},
                        "axis": {"format": "d", "tickMinStep": 1},
                    },
                    "color": {
                        "field": "risk_category",
                        "type": "nominal",
                        "scale": {
                            "domain": core.RISK_CATEGORY_ORDER,
                            "range": [core.CATEGORY_PALETTE[c] for c in core.RISK_CATEGORY_ORDER],
                        },
                        "legend": None,
                    },
                    "tooltip": [
                        {"field": "risk_category", "type": "nominal", "title": "Category"},
                        {"field": "count", "type": "quantitative", "title": "Count"},
                    ],
                },
                "height": 220,
            },
            use_container_width=True,
        )

        st.subheader("Dimensional distributions")

        dimension_specs = [
            ("Type", "type", list(core.TYPE_MAP.keys())),
            ("Delivery", "delivery", list(core.DELIVERY_MAP.keys())),
            ("Authenticity", "authenticity", list(core.AUTHENTICITY_MAP.keys())),
            ("Guidance", "guidance", list(core.GUIDANCE_MAP.keys())),
        ]

        chart_cols = st.columns(2)
        for index, (title, column_name, category_order) in enumerate(dimension_specs):
            dim_counts = (
                valid[column_name]
                .astype(str)
                .str.strip()
                .value_counts()
                .reindex(category_order, fill_value=0)
                .rename_axis("category")
                .reset_index(name="count")
            )

            with chart_cols[index % 2]:
                st.markdown(f"**{title}**")
                st.vega_lite_chart(
                    dim_counts,
                    {
                        "mark": {"type": "bar", "cornerRadiusEnd": 3, "color": "#49A8EC"},
                        "encoding": {
                            "y": {
                                "field": "category",
                                "type": "nominal",
                                "sort": category_order,
                                "title": None,
                            },
                            "x": {
                                "field": "count",
                                "type": "quantitative",
                                "title": "Assessments",
                                "scale": {"domainMin": 0, "nice": True, "zero": True},
                                "axis": {"format": "d", "tickMinStep": 1},
                            },
                            "tooltip": [
                                {"field": "category", "type": "nominal", "title": "Category"},
                                {"field": "count", "type": "quantitative", "title": "Count"},
                            ],
                        },
                        "height": 180,
                    },
                    use_container_width=True,
                )


def _detect_subject_column(df):
    candidates = ["subject-code", "subject code", "subject_code", "subject", "subject name"]
    normalized = {str(col).strip().lower().replace("_", " "): col for col in df.columns}
    for candidate in candidates:
        found = normalized.get(candidate)
        if found is not None:
            return found
    # Fallback: accept any column name containing 'subject'.
    for norm_name, original in normalized.items():
        if "subject" in norm_name:
            return original
    return None


def _build_scatter_dataframe(scored):
    valid = scored[scored["is_valid"]].copy()
    if valid.empty:
        return valid, None, None

    resolved, _ = core._resolve_batch_columns(valid)
    type_col = resolved["type"]
    delivery_col = resolved["delivery"]
    weighting_col = resolved["weighting"]

    valid["type_score"] = valid[type_col].map(core.TYPE_MAP)
    valid["delivery_score"] = valid[delivery_col].map(core.DELIVERY_MAP)

    jitter = 0.04
    rng = np.random.default_rng(42)
    valid["_type_j"] = valid["type_score"] + rng.normal(0, jitter, size=len(valid))
    valid["_delivery_j"] = valid["delivery_score"] + rng.normal(0, jitter, size=len(valid))

    weights = pd.to_numeric(valid[weighting_col], errors="coerce").fillna(0).clip(0, 100)
    valid["_weight_for_size"] = weights
    return valid, resolved, _detect_subject_column(valid)


def _format_weighting_percent(value):
    numeric = pd.to_numeric(pd.Series([value]), errors="coerce").iloc[0]
    if pd.isna(numeric):
        return f"{value}%"
    if float(numeric).is_integer():
        return f"{int(numeric)}%"
    return f"{float(numeric):.2f}%"


def _format_hover_value(value):
    if pd.isna(value):
        return "N/A"
    return str(value)


def _render_interactive_scatter(scored):
    st.markdown("---")
    st.subheader("Data Summary")
    st.caption("Review your uploaded data below, using the Validation column to identify any issues. When you are satisfied that the data is complete, download the final dataset using the 'Download scored data' button below.")

    scatter_df, resolved, subject_col = _build_scatter_dataframe(scored)
    if scatter_df.empty:
        st.info("No valid rows are currently available for plotting. Please review the Validation messages in the table and correct any invalid entries.")
        return

    type_col = resolved["type"]
    delivery_col = resolved["delivery"]
    authenticity_col = resolved["authenticity"]
    guidance_col = resolved["guidance"]
    weighting_col = resolved["weighting"]

    filtered = scatter_df.copy()
    display_df = scored.copy()

    calculated_columns_for_table = ["risk_score", "risk_category", "validation_error"]
    generated_columns = ["risk_score", "risk_category", "validation_error", "is_valid"]
    uploaded_columns = [col for col in scored.columns if col not in generated_columns]
    display_columns = uploaded_columns + [col for col in calculated_columns_for_table if col in scored.columns]

    validation_display_col = "Validation"
    if "validation_error" in display_df.columns:
        display_df[validation_display_col] = display_df["validation_error"].replace("", "OK")

    display_columns_for_table = [
        validation_display_col if col == "validation_error" else col
        for col in display_columns
    ]

    if subject_col is not None:
        subject_values = [s for s in filtered[subject_col].dropna().astype(str).unique().tolist() if s.strip()]
        subject_values = sorted(subject_values)
        options = ["All subjects"] + subject_values
        auto_single_subject = len(subject_values) == 1
        default_subject = subject_values[0] if auto_single_subject else "All subjects"

        current_subject = st.session_state.get("scatter_subject_filter")
        if current_subject not in options:
            st.session_state["scatter_subject_filter"] = default_subject
        elif auto_single_subject and current_subject != default_subject:
            st.session_state["scatter_subject_filter"] = default_subject

        selected_subject = st.selectbox("Subject view", options, key="scatter_subject_filter")
        if selected_subject != "All subjects":
            filtered = filtered[filtered[subject_col].astype(str) == selected_subject]
            display_df = display_df[display_df[subject_col].astype(str) == selected_subject]

        # If only one subject exists, reset the row selector once so all filtered rows start selected.
        if auto_single_subject:
            selector_seed = f"{selected_subject}:{len(display_df)}"
            if st.session_state.get("scatter_row_selector_seed") != selector_seed:
                st.session_state.pop("scatter_row_selector", None)
                st.session_state["scatter_row_selector_seed"] = selector_seed
        else:
            st.session_state.pop("scatter_row_selector_seed", None)
    else:
        selected_subject = "All subjects"
        st.caption("No subject-style column was detected in this upload, so all valid rows will be shown together in a single scatterplot.")

    if display_df.empty:
        st.info("No rows match the current subject selection. Try switching Subject view back to 'All subjects' or choose a different subject.")
        return

    table_df = display_df[display_columns_for_table].copy()
    selectable = table_df.copy()
    selectable.insert(0, "plot", False)

    if selected_subject != "All subjects" and subject_col is not None:
        selectable["plot"] = True

    edited = st.data_editor(
        selectable,
        use_container_width=True,
        hide_index=True,
        column_config={
            "plot": st.column_config.CheckboxColumn("Select", help="Tick rows to include in the scatterplot."),
            validation_display_col: st.column_config.TextColumn("Validation"),
        },
        key="scatter_row_selector",
    )

    st.download_button(
        "Download scored CSV",
        data=_to_csv_bytes(scored),
        file_name="gari_batch_scored.csv",
        mime="text/csv",
        use_container_width=False,
        key="batch_scored_download",
    )

    st.subheader("Visualisation")
    if subject_col is not None:
        st.caption("To get a quick snapshot of a few assessments, select the rows you want to include using the 'Select' column in the table above. Optionally, use the 'Subject view' dropdown to focus on a single subject.")
    else:
        st.caption("This file does not include a subject-style column, so the scatterplot uses a single combined view. Tick rows in Data Summary above to add them to the visualisation.")

    selected_indices = edited.index[edited["plot"]]
    selected = None
    png_bytes = None
    if len(selected_indices) == 0:
        st.info("To generate the scatterplot, select one or more rows in Data Summary using the Select checkboxes.")
    else:
        selected = filtered.loc[filtered.index.intersection(selected_indices)]
        if selected.empty:
            st.warning("The selected rows are not valid for plotting. Please choose rows where Validation is marked as OK.")
        else:
            required_dimension_columns = {type_col, delivery_col, authenticity_col, guidance_col, weighting_col}
            extra_columns = [
                c for c in uploaded_columns
                if c in selected.columns and c not in required_dimension_columns
            ]

            hover_lines = []
            for _, row in selected.iterrows():
                lines = []
                for col in extra_columns:
                    lines.append(f"{col}: {_format_hover_value(row[col])}")

                lines.append(f"Type: {_format_hover_value(row[type_col])}")
                lines.append(f"Delivery: {_format_hover_value(row[delivery_col])}")
                lines.append(f"Authenticity: {_format_hover_value(row[authenticity_col])}")
                lines.append(f"Guidance: {_format_hover_value(row[guidance_col])}")
                lines.append(f"Weighting: {_format_weighting_percent(row[weighting_col])}")
                hover_lines.append("<br>".join(lines))

            selected = selected.copy()
            selected["_hover_text"] = hover_lines

            fig = px.scatter(
                selected,
                x="_type_j",
                y="_delivery_j",
                color="risk_category",
                size="_weight_for_size",
                size_max=52,
                color_discrete_map=core.CATEGORY_PALETTE,
                category_orders={"risk_category": core.RISK_CATEGORY_ORDER},
                custom_data=["_hover_text"],
                title=f"Assessment Risk Scatter ({selected_subject})",
            )

            x_vals = list(core.TYPE_MAP.values())
            x_labels = list(core.TYPE_MAP.keys())
            y_vals = list(core.DELIVERY_MAP.values())
            y_labels = list(core.DELIVERY_MAP.keys())

            fig.update_layout(
                template="plotly_white",
                legend_title_text="Risk category",
                hoverlabel={"namelength": -1},
                margin={"l": 10, "r": 10, "t": 60, "b": 10},
                title_font_size=16,
                font=dict(size=11),
                legend=dict(font=dict(size=10), title_font_size=11),
            )
            fig.update_traces(
                marker={"line": {"width": 0.7, "color": "#2D3748"}, "opacity": 0.9},
                hovertemplate="%{customdata[0]}<extra></extra>",
            )
            fig.update_xaxes(
                title="Assessment type",
                title_font_size=13,
                tickfont_size=10,
                tickmode="array",
                tickvals=x_vals,
                ticktext=x_labels,
                range=[min(x_vals) - 0.2, max(x_vals) + 0.2],
                zeroline=False,
            )
            fig.update_yaxes(
                title="Delivery mode",
                title_font_size=13,
                tickfont_size=10,
                tickmode="array",
                tickvals=y_vals,
                ticktext=y_labels,
                range=[min(y_vals) - 0.2, max(y_vals) + 0.2],
                zeroline=False,
            )

            st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False, "toImageButtonOptions": {"format": "png", "filename": "gari_subject_scatter"}})

            st.markdown("---")
            st.subheader(f"{selected_subject} Summary")
            selected_valid = selected[selected["is_valid"]]
            s_avg = selected_valid["risk_score"].mean() if not selected_valid.empty else None
            
            if selected_valid.empty:
                st.warning("No valid assessments in this selection.")
            else:
                s_avg = selected_valid["risk_score"].mean()
                s_category = core.score_to_category(s_avg)
                s_color = core.CATEGORY_PALETTE.get(s_category, "#000000")
                
                s_result_col, s_score_col = st.columns([4, 1], gap="small", vertical_alignment="center")
                s_html = f"""<div style='padding:14px 16px;border-radius:8px;background:{s_color};border-left:4px solid {s_color};min-height:74px;display:flex;align-items:center'>
                <span style='font-weight:bold; color:#fff;line-height:1.3'>Subject risk level: {s_category}</span>
                </div>"""
                with s_result_col:
                    st.markdown(s_html, unsafe_allow_html=True)
                with s_score_col:
                    st.metric("Avg risk score", f"{s_avg:.2f}")
                

            st.markdown("---")

            try:
                pdf_fig = deepcopy(fig)
                pdf_fig.update_layout(
                    title_font_size=32,
                    font=dict(size=20),
                    legend=dict(font=dict(size=18), title_font_size=18),
                )
                pdf_fig.update_xaxes(title_font_size=24, tickfont_size=18)
                pdf_fig.update_yaxes(title_font_size=24, tickfont_size=18)
                png_bytes = pio.to_image(pdf_fig, format="png", width=1400, height=900, scale=2)
            except Exception:
                st.caption("💡 Use the camera icon in the plot toolbar to save a PNG snapshot.")

    try:
        visual_pdf = build_batch_pdf_report(
            scored=scored,
            selected_rows=selected,
            selected_subject=selected_subject,
            scatter_png_bytes=png_bytes,
        )
        export_col_left, export_col_right = st.columns([1, 1])
        with export_col_left:
            if png_bytes is not None:
                st.download_button(
                    "Download scatterplot PNG",
                    data=png_bytes,
                    file_name="gari_subject_scatter.png",
                    mime="image/png",
                    use_container_width=False,
                    key="scatter_png_download",
                )
        with export_col_right:
            _, pdf_button_col = st.columns([1, 1])
            with pdf_button_col:
                pdf_file_name = "gari_batch_selected_report.pdf" if png_bytes is not None else "gari_batch_report.pdf"
                st.download_button(
                    "Download PDF report",
                    data=visual_pdf,
                    file_name=pdf_file_name,
                    mime="application/pdf",
                    use_container_width=False,
                    key="batch_selected_pdf_download",
                )
    except Exception as ex:
        st.error(f"PDF export failed: {type(ex).__name__}: {str(ex)}")


def _render_batch_calculator():
    template_df = core.get_batch_template_df()
    left_col, right_col = st.columns([3.8, 1.2])
    with left_col:
        with st.expander("Instructions", expanded=False):
            _show_contract_help()
    with right_col:
        st.download_button(
            "Download template",
            data=_to_csv_bytes(template_df),
            file_name="gari_batch_template.csv",
            mime="text/csv",
            use_container_width=False,
            key="batch_template_download",
        )

    uploaded = st.file_uploader("Upload assessment CSV", type=["csv"], key="batch_upload")
    if uploaded is None:
        return

    try:
        input_df = pd.read_csv(uploaded)
    except Exception:
        st.error("We could not read this file as a CSV. Please upload a valid UTF-8 encoded CSV and try again.")
        return

    if input_df.empty:
        st.warning("The uploaded CSV is empty. Please add at least one assessment row and upload again.")
        return

    try:
        scored = core.score_batch_dataframe(input_df)
    except Exception as ex:
        st.error(f"Validation failed: {ex}")
        return

    st.markdown("---")
    _render_summary(scored)

    invalid_rows = scored[~scored["is_valid"]]
    if not invalid_rows.empty:
        st.warning(
            "Some rows are invalid and were not scored. Please check the Validation column in Data Summary for row-level details, or review the validation_error field in the downloaded CSV."
        )

    _render_interactive_scatter(scored)


single_tab, batch_tab = st.tabs(["Single", "Batch"])

with single_tab:
    _render_single_calculator()

with batch_tab:
    _render_batch_calculator()
