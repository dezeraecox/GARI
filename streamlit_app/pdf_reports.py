import base64
import html
from datetime import datetime

import pandas as pd

import core


def build_single_pdf_report(
    assessment_type,
    delivery,
    authenticity,
    guidance,
    weighting,
    risk_score,
    category,
    tips,
    assessment_label=None,
):
    try:
        from weasyprint import HTML
    except Exception as ex:
        raise RuntimeError(f"PDF export requires weasyprint: {ex}") from ex

    # Convert internal type value to display label
    type_display = core.TYPE_DISPLAY_LABELS.get(assessment_type, assessment_type)

    category_color = core.CATEGORY_PALETTE.get(category, "#000000")
    pdf_title = f"GARI - {assessment_label}" if assessment_label else "GARI"

    tips_html = ""
    if tips:
        tips_list = "".join(f"<li>{tip}</li>" for tip in tips)
        tips_html = f"""
        <div class="section">
            <h2>Risk Reduction Tips</h2>
            <ul class="tips-list">{tips_list}</ul>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                color: #1F2937;
                line-height: 1.5;
                background: white;
                padding: 24px;
            }}
            .header {{
                margin-bottom: 32px;
            }}
            .title {{
                font-size: 32px;
                font-weight: 700;
                margin-bottom: 4px;
                color: #1F2937;
            }}
            .subtitle {{
                font-size: 14px;
                color: #6B7280;
                margin-bottom: 4px;
            }}
            .section {{
                margin-bottom: 28px;
            }}
            .section h2 {{
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 16px;
                color: #1F2937;
            }}
            .inputs-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                margin-bottom: 20px;
            }}
            .input-card {{
                background: #F9FAFB;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 12px;
            }}
            .input-label {{
                font-size: 12px;
                font-weight: 600;
                color: #6B7280;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                margin-bottom: 4px;
            }}
            .input-value {{
                font-size: 16px;
                font-weight: 600;
                color: #1F2937;
            }}
            .result-box {{
                background: {category_color};
                border-radius: 8px;
                padding: 24px;
                color: white;
                display: grid;
                grid-template-columns: 1fr auto;
                gap: 24px;
                align-items: center;
                margin-bottom: 24px;
            }}
            .result-label {{
                font-size: 14px;
                font-weight: 600;
                opacity: 0.95;
                margin-bottom: 8px;
            }}
            .result-category {{
                font-size: 28px;
                font-weight: 700;
            }}
            .result-score {{
                text-align: right;
            }}
            .score-label {{
                font-size: 12px;
                font-weight: 600;
                opacity: 0.95;
                margin-bottom: 4px;
            }}
            .score-value {{
                font-size: 32px;
                font-weight: 700;
            }}
            .tips-list {{
                list-style: none;
                padding: 0;
            }}
            .tips-list li {{
                font-size: 13px;
                color: #374151;
                margin-bottom: 10px;
                padding-left: 20px;
                position: relative;
            }}
            .tips-list li:before {{
                content: "-";
                position: absolute;
                left: 0;
                font-weight: bold;
            }}
            .footer {{
                border-top: 1px solid #E5E7EB;
                padding-top: 16px;
                font-size: 12px;
                color: #9CA3AF;
                margin-top: 32px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="title">{pdf_title}</div>
            <div class="subtitle">Assessment Report - Generated {datetime.now().strftime('%B %d, %Y at %H:%M')}</div>
        </div>

        <div class="section">
            <h2>Assessment Inputs</h2>
            <div class="inputs-grid">
                <div class="input-card">
                    <div class="input-label">Type</div>
                    <div class="input-value">{type_display}</div>
                </div>
                <div class="input-card">
                    <div class="input-label">Delivery</div>
                    <div class="input-value">{delivery}</div>
                </div>
                <div class="input-card">
                    <div class="input-label">Authenticity</div>
                    <div class="input-value">{authenticity}</div>
                </div>
                <div class="input-card">
                    <div class="input-label">Guidance</div>
                    <div class="input-value">{guidance}</div>
                </div>
            </div>
            <div class="input-card">
                <div class="input-label">Assessment Weighting</div>
                <div class="input-value">{weighting}%</div>
            </div>
        </div>

        <div class="result-box">
            <div>
                <div class="result-label">The risk level of this assessment is:</div>
                <div class="result-category">{category}</div>
            </div>
            <div class="result-score">
                <div class="score-label">Risk Score</div>
                <div class="score-value">{risk_score:.2f}</div>
            </div>
        </div>

        {tips_html}

        <div class="footer">
            <p>GARI was designed to help educators quickly assess vulnerability to unintentional or inappropriate generative AI use. Use these insights to guide design adjustments and discussions with colleagues.</p>
        </div>
    </body>
    </html>
    """

    try:
        return HTML(string=html_content).write_pdf()
    except Exception as ex:
        raise RuntimeError(f"PDF generation failed: {str(ex)}") from ex


def build_batch_pdf_report(scored, selected_rows=None, selected_subject="All subjects", scatter_png_bytes=None):
    try:
        from weasyprint import HTML
    except Exception as ex:
        raise RuntimeError(f"PDF export requires weasyprint: {ex}") from ex

    valid = scored[scored["is_valid"]]
    invalid = scored[~scored["is_valid"]]
    avg_score = valid["risk_score"].mean() if not valid.empty else None

    counts = (
        valid["risk_category"]
        .value_counts()
        .reindex(core.RISK_CATEGORY_ORDER, fill_value=0)
        .rename_axis("Risk category")
        .reset_index(name="Count")
    )

    total_valid = int(len(valid))
    max_count = int(counts["Count"].max()) if not counts.empty else 0

    distribution_rows_html = ""
    for _, row in counts.iterrows():
        category = str(row["Risk category"])
        count = int(row["Count"])
        percent = (count / total_valid * 100.0) if total_valid > 0 else 0.0
        width_pct = (count / max_count * 100.0) if max_count > 0 else 0.0
        color = core.CATEGORY_PALETTE.get(category, "#4B5563")
        distribution_rows_html += f"""
        <div class=\"dist-row\">
            <div class=\"dist-label\">{html.escape(category)}</div>
            <div class=\"dist-bar-wrap\">
                <div class=\"dist-bar\" style=\"width:{width_pct:.2f}%; background:{color};\"></div>
            </div>
            <div class=\"dist-count\">{count} ({percent:.1f}%)</div>
        </div>
        """

    dimension_specs = [
        ("Type", "type", list(core.TYPE_MAP.keys())),
        ("Delivery", "delivery", list(core.DELIVERY_MAP.keys())),
        ("Authenticity", "authenticity", list(core.AUTHENTICITY_MAP.keys())),
        ("Guidance", "guidance", list(core.GUIDANCE_MAP.keys())),
    ]
    dimension_cards_html = ""
    for title, col_name, category_order in dimension_specs:
        if col_name not in valid.columns:
            continue

        dim_counts = (
            valid[col_name]
            .astype(str)
            .str.strip()
            .value_counts()
            .reindex(category_order, fill_value=0)
            .rename_axis("category")
            .reset_index(name="count")
        )
        dim_max = int(dim_counts["count"].max()) if not dim_counts.empty else 0

        dim_rows_html = ""
        for _, drow in dim_counts.iterrows():
            dlabel = str(drow["category"])
            # Convert type values to display labels
            if col_name == "type":
                dlabel = core.TYPE_DISPLAY_LABELS.get(dlabel, dlabel)
            dcount = int(drow["count"])
            dwidth = (dcount / dim_max * 100.0) if dim_max > 0 else 0.0
            dim_rows_html += f"""
            <div class=\"dim-row\">
                <div class=\"dim-label\">{html.escape(dlabel)}</div>
                <div class=\"dim-bar-wrap\">
                    <div class=\"dim-bar\" style=\"width:{dwidth:.2f}%;\"></div>
                </div>
                <div class=\"dim-count\">{dcount}</div>
            </div>
            """

        dimension_cards_html += f"""
        <div class=\"dim-card\">
            <h3>{html.escape(title)}</h3>
            {dim_rows_html}
        </div>
        """

    scatter_html = ""
    if scatter_png_bytes:
        scatter_b64 = base64.b64encode(scatter_png_bytes).decode("ascii")
        scatter_html = f"""
        <div class=\"section\">
            <h2>Selected Scatterplot</h2>
            <div class=\"image-wrap\">
                <img src=\"data:image/png;base64,{scatter_b64}\" alt=\"Selected scatterplot\" />
            </div>
        </div>
        """

    selected_rows_html = ""
    if selected_rows is not None and not selected_rows.empty:
        display_cols = ["type", "delivery", "authenticity", "guidance", "weighting", "risk_score"]
        display_cols = [col for col in display_cols if col in selected_rows.columns]
        col_labels = {
            "type": "Type",
            "delivery": "Delivery",
            "authenticity": "Authenticity",
            "guidance": "Guidance",
            "weighting": "Weighting",
            "risk_score": "Risk Score",
        }
        table_rows = ""
        for _, row in selected_rows.iterrows():
            row_html = ""
            for col in display_cols:
                val = str(row[col]) if pd.notna(row[col]) else ""
                # Convert type values to display labels
                if col == "type":
                    val = core.TYPE_DISPLAY_LABELS.get(val, val)
                row_html += f"<td>{html.escape(val)}</td>"
            table_rows += f"<tr>{row_html}</tr>"

        header_row = "".join([f"<th>{html.escape(col_labels[col])}</th>" for col in display_cols])
        selected_rows_html = f"""
        <div class=\"section\">
            <h2>Selected Assessments</h2>
            <table class=\"selected-table\">
                <thead><tr>{header_row}</tr></thead>
                <tbody>{table_rows}</tbody>
            </table>
        </div>
        """

    subject_summary_html = ""
    if selected_rows is not None and not selected_rows.empty:
        selected_valid = selected_rows[selected_rows["is_valid"]]
        if not selected_valid.empty:
            s_avg = selected_valid["risk_score"].mean()
            s_category = core.score_to_category(s_avg)
            s_color = core.CATEGORY_PALETTE.get(s_category, "#000000")
            s_assessments = len(selected_rows)
            s_valid = len(selected_valid)

            subject_summary_html = f"""
        <div style=\"page-break-before: always;\"></div>
        <div class=\"section subject-summary\">
            <h2>{html.escape(str(selected_subject))} Summary</h2>
            <div class=\"subject-result-box\" style=\"background:{s_color}; border-left-color:{s_color};\">
                <div class=\"subject-result-text\">Subject risk level: {html.escape(s_category)}</div>
            </div>
            <div class=\"subject-metrics\">
                <div class=\"subject-metric-card\"><div class=\"subject-metric-label\">Assessments</div><div class=\"subject-metric-value\">{s_assessments}</div></div>
                <div class=\"subject-metric-card\"><div class=\"subject-metric-label\">Valid</div><div class=\"subject-metric-value\">{s_valid}</div></div>
                <div class=\"subject-metric-card\"><div class=\"subject-metric-label\">Avg risk</div><div class=\"subject-metric-value\">{s_avg:.2f}</div></div>
            </div>
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset=\"UTF-8\">
        <style>
            * {{ box-sizing: border-box; }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
                color: #1F2937;
                line-height: 1.4;
                margin: 0;
                padding: 24px;
                background: white;
            }}
            .header {{ margin-bottom: 24px; }}
            .title {{ font-size: 30px; font-weight: 700; margin: 0 0 4px 0; }}
            .subtitle {{ font-size: 13px; color: #6B7280; margin: 0; }}
            .section {{ margin-bottom: 24px; }}
            .section h2 {{ font-size: 18px; margin: 0 0 12px 0; }}
            .summary-grid {{
                display: grid;
                grid-template-columns: repeat(5, 1fr);
                gap: 10px;
            }}
            .summary-card {{
                border: 1px solid #E5E7EB;
                background: #F9FAFB;
                border-radius: 8px;
                padding: 10px 12px;
            }}
            .summary-label {{ font-size: 11px; color: #6B7280; text-transform: uppercase; font-weight: 700; }}
            .summary-value {{ font-size: 18px; font-weight: 700; margin-top: 4px; }}
            .dist-container {{
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                padding: 12px;
                background: #FFFFFF;
            }}
            .dist-row {{
                display: flex;
                align-items: center;
                margin-bottom: 8px;
            }}
            .dist-row:last-child {{ margin-bottom: 0; }}
            .dist-label {{ width: 120px; font-size: 12px; font-weight: 600; }}
            .dist-bar-wrap {{
                flex: 1;
                height: 14px;
                border-radius: 999px;
                background: #E5E7EB;
                overflow: hidden;
                margin: 0 10px;
            }}
            .dist-bar {{ height: 100%; border-radius: 999px; }}
            .dist-count {{ width: 90px; font-size: 12px; color: #374151; text-align: right; }}
            .image-wrap {{
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background: #FFFFFF;
                padding: 8px;
            }}
            .image-wrap img {{ width: 100%; height: auto; display: block; }}
            .dim-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 12px;
            }}
            .dim-card {{
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background: #FFFFFF;
                padding: 12px;
            }}
            .dim-card h3 {{
                margin: 0 0 10px 0;
                font-size: 14px;
            }}
            .dim-row {{
                display: flex;
                align-items: center;
                margin-bottom: 8px;
            }}
            .dim-row:last-child {{ margin-bottom: 0; }}
            .dim-label {{ width: 120px; font-size: 12px; font-weight: 600; }}
            .dim-bar-wrap {{
                flex: 1;
                height: 14px;
                border-radius: 999px;
                background: #E5E7EB;
                overflow: hidden;
                margin: 0 10px;
            }}
            .dim-bar {{
                height: 100%;
                border-radius: 999px;
                background: #49A8EC;
            }}
            .dim-count {{ width: 38px; font-size: 12px; color: #374151; text-align: right; }}
            .selected-table {{
                width: 100%;
                border-collapse: collapse;
                border: 1px solid #E5E7EB;
                border-radius: 8px;
                background: #FFFFFF;
            }}
            .selected-table thead {{
                background: #F3F4F6;
            }}
            .selected-table th {{
                padding: 10px 12px;
                text-align: left;
                font-size: 12px;
                font-weight: 600;
                border-bottom: 1px solid #E5E7EB;
                color: #374151;
            }}
            .selected-table td {{
                padding: 10px 12px;
                font-size: 12px;
                border-bottom: 1px solid #E5E7EB;
                color: #1F2937;
            }}
            .selected-table tbody tr:last-child td {{
                border-bottom: none;
            }}
            .subject-summary {{
                margin-bottom: 20px;
            }}
            .subject-result-box {{
                padding: 14px 16px;
                border-radius: 8px;
                border-left: 4px solid;
                min-height: 60px;
                display: flex;
                align-items: center;
                margin-bottom: 12px;
            }}
            .subject-result-text {{
                font-weight: bold;
                color: #fff;
                line-height: 1.3;
                flex: 1;
            }}
            .subject-metrics {{
                display: grid;
                grid-template-columns: 1fr 1fr 1fr;
                gap: 10px;
            }}
            .subject-metric-card {{
                border: 1px solid #E5E7EB;
                background: #F9FAFB;
                border-radius: 8px;
                padding: 10px 12px;
            }}
            .subject-metric-label {{
                font-size: 11px;
                color: #6B7280;
                text-transform: uppercase;
                font-weight: 700;
            }}
            .subject-metric-value {{
                font-size: 18px;
                font-weight: 700;
                margin-top: 4px;
            }}
            .footer {{
                border-top: 1px solid #E5E7EB;
                margin-top: 24px;
                padding-top: 12px;
                font-size: 11px;
                color: #6B7280;
            }}
        </style>
    </head>
    <body>
        <div class=\"header\">
            <h1 class=\"title\">GARI Batch Risk Report</h1>
            <p class=\"subtitle\">Generated {datetime.now().strftime('%B %d, %Y at %H:%M')} | Subject view: {html.escape(str(selected_subject))}</p>
        </div>

        <div class=\"section\">
            <h2>Batch Summary</h2>
            <div class=\"summary-grid\">
                <div class=\"summary-card\"><div class=\"summary-label\">Rows</div><div class=\"summary-value\">{len(scored)}</div></div>
                <div class=\"summary-card\"><div class=\"summary-label\">Valid</div><div class=\"summary-value\">{len(valid)}</div></div>
                <div class=\"summary-card\"><div class=\"summary-label\">Invalid</div><div class=\"summary-value\">{len(invalid)}</div></div>
                <div class=\"summary-card\"><div class=\"summary-label\">Avg. risk</div><div class=\"summary-value\">{f'{avg_score:.2f}' if avg_score is not None else 'N/A'}</div></div>
                <div class=\"summary-card\"><div class=\"summary-label\">Subject</div><div class=\"summary-value\">{html.escape(str(selected_subject))}</div></div>
            </div>
        </div>

        <div class=\"section\">
            <h2>Risk Distribution</h2>
            <div class=\"dist-container\">
                {distribution_rows_html}
            </div>
        </div>

        <div class=\"section\">
            <h2>Dimensional Distributions</h2>
            <div class=\"dim-grid\">
                {dimension_cards_html}
            </div>
        </div>

        {subject_summary_html}

        {scatter_html}

        {selected_rows_html}

    </body>
    </html>
    """

    try:
        return HTML(string=html_content).write_pdf()
    except Exception as ex:
        raise RuntimeError(f"PDF generation failed: {str(ex)}") from ex
