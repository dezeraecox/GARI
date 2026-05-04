import pandas as pd


TYPE_MAP = {"Quiz/Exam": 0, "Creative": 0.5, "Report": 1}
DELIVERY_MAP = {"In person": 0, "Hybrid": 0.5, "Online": 1}
AUTHENTICITY_MAP = {"Nothing": 0, "Personalised": 0.5, "Body of work": 1}
GUIDANCE_MAP = {"Policy": 0, "Guideline": 0.5, "Education": 1}

# Batch uploads can use either canonical values or single-calculator labels.
TYPE_BATCH_DISPLAY_LABELS = ["Quiz/Exam", "Creative/Multimedia", "Extended Written"]

# Map internal type values to user-facing display labels
TYPE_DISPLAY_LABELS = {
    "Quiz/Exam": "Quiz/Exam",
    "Creative": "Creative/Multimedia",
    "Report": "Extended Written",
}
TYPE_INPUT_ALIASES = {
    "quiz/exam": "Quiz/Exam",
    "creative": "Creative",
    "creative/multimedia": "Creative",
    "report": "Report",
    "extended written": "Report",
}

CATEGORY_PALETTE = {
    "Insignificant": "#6B7280",
    "Minor": "#14B8A6",
    "Moderate": "#F59E0B",
    "High": "#DC2626",
    "Critical": "#4C1D95",
}


RISK_CATEGORY_ORDER = ["Insignificant", "Minor", "Moderate", "High", "Critical"]

BATCH_COLUMN_ALIASES = {
    "type": ["type", "assessment_type", "assessment type"],
    "delivery": ["delivery", "delivery_mode", "delivery mode", "mode"],
    "authenticity": ["authenticity", "authenticity_level", "authenticity level"],
    "guidance": ["guidance", "guidance_level", "guidance level"],
    "weighting": [
        "weighting",
        "weighting_%",
        "weighting (%)",
        "assessment weighting",
        "assessment weighting (%)",
        "assessment_weighting",
    ],
}


def score_to_category(score):
    baseline = max(AUTHENTICITY_MAP.values()) + max(GUIDANCE_MAP.values())
    if score < 1 * baseline:
        return "Insignificant"
    if score < 1.5 * baseline:
        return "Minor"
    if score < 2 * baseline:
        return "Moderate"
    if score < 2.5 * baseline:
        return "High"
    return "Critical"


def calculate_risk_score(assessment_type, delivery, authenticity, guidance, weighting):
    t_score = TYPE_MAP.get(assessment_type)
    d_score = DELIVERY_MAP.get(delivery)
    a_score = AUTHENTICITY_MAP.get(authenticity)
    g_score = GUIDANCE_MAP.get(guidance)

    if t_score is None or d_score is None or a_score is None or g_score is None:
        raise ValueError("Invalid category value provided.")

    weighting_value = float(weighting)
    if weighting_value < 0 or weighting_value > 100:
        raise ValueError("Weighting must be between 0 and 100.")
    
    baseline = max(AUTHENTICITY_MAP.values()) + max(GUIDANCE_MAP.values())

    base_risk = baseline + (t_score + d_score) - (a_score + g_score)
    weighting_multiplier = 1.0 + (weighting_value / 100.0)
    adjusted_risk = round(base_risk * weighting_multiplier, 2)
    return adjusted_risk, score_to_category(adjusted_risk)


def _norm_text(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def _norm_colname(name):
    return str(name).strip().lower().replace("_", " ")


def get_batch_template_df():
    return pd.DataFrame(
        [
            {
                "type": "Quiz/Exam",
                "delivery": "In person",
                "authenticity": "Nothing",
                "guidance": "Policy",
                "weighting": 40,
            },
            {
                "type": "Extended Written",
                "delivery": "Online",
                "authenticity": "Body of work",
                "guidance": "Education",
                "weighting": 60,
            },
        ]
    )


def _resolve_batch_columns(df):
    normalized = {_norm_colname(col): col for col in df.columns}
    resolved = {}
    missing = []
    for canonical, aliases in BATCH_COLUMN_ALIASES.items():
        actual = None
        for alias in aliases:
            match = normalized.get(_norm_colname(alias))
            if match is not None:
                actual = match
                break
        if actual is None:
            missing.append(canonical)
        else:
            resolved[canonical] = actual
    return resolved, missing


def score_batch_dataframe(df):
    output = df.copy()
    resolved, missing = _resolve_batch_columns(output)

    if missing:
        missing_txt = ", ".join(missing)
        raise ValueError(f"Missing required columns: {missing_txt}")

    type_lookup = {_norm_text(key): key for key in TYPE_MAP}
    type_lookup.update(TYPE_INPUT_ALIASES)
    delivery_lookup = {_norm_text(key): key for key in DELIVERY_MAP}
    authenticity_lookup = {_norm_text(key): key for key in AUTHENTICITY_MAP}
    guidance_lookup = {_norm_text(key): key for key in GUIDANCE_MAP}

    risk_scores = []
    risk_categories = []
    validation_errors = []

    for idx, row in output.iterrows():
        t_raw = row[resolved["type"]]
        d_raw = row[resolved["delivery"]]
        a_raw = row[resolved["authenticity"]]
        g_raw = row[resolved["guidance"]]
        w_raw = row[resolved["weighting"]]

        t_value = type_lookup.get(_norm_text(t_raw))
        d_value = delivery_lookup.get(_norm_text(d_raw))
        a_value = authenticity_lookup.get(_norm_text(a_raw))
        g_value = guidance_lookup.get(_norm_text(g_raw))

        issues = []
        if t_value is None:
            issues.append("invalid type")
        if d_value is None:
            issues.append("invalid delivery")
        if a_value is None:
            issues.append("invalid authenticity")
        if g_value is None:
            issues.append("invalid guidance")

        try:
            w_value = float(w_raw)
            if w_value < 0 or w_value > 100:
                issues.append("weighting out of range (0-100)")
        except Exception:
            w_value = None
            issues.append("invalid weighting")

        if issues:
            risk_scores.append(None)
            risk_categories.append(None)
            validation_errors.append("; ".join(issues))
            continue

        # Persist normalized labels so downstream summaries/charts remain consistent.
        output.at[idx, resolved["type"]] = t_value
        output.at[idx, resolved["delivery"]] = d_value
        output.at[idx, resolved["authenticity"]] = a_value
        output.at[idx, resolved["guidance"]] = g_value

        score, category = calculate_risk_score(
            assessment_type=t_value,
            delivery=d_value,
            authenticity=a_value,
            guidance=g_value,
            weighting=w_value,
        )
        risk_scores.append(score)
        risk_categories.append(category)
        validation_errors.append("")

    output["risk_score"] = risk_scores
    output["risk_category"] = risk_categories
    output["validation_error"] = validation_errors
    output["is_valid"] = output["validation_error"].eq("")
    return output

