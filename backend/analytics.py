"""
analytics.py
------------
Core data engine for the Freshman Success Intelligence Platform.
Loads the Excel dataset, computes risk scores, trends, and
generates the priority contact list used by the API.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from functools import lru_cache

DATA_PATH = Path(__file__).parent / "data" / "students.xlsx"


# ─────────────────────────────────────────────
# 1. DATA LOADING
# ─────────────────────────────────────────────

@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    """Load and return the master student log (cached after first call)."""
    df = pd.read_excel(DATA_PATH, sheet_name="All Student Master Logs")
    df.columns = df.columns.str.strip()
    return df


def get_week8() -> pd.DataFrame:
    """Return only Week 8 records — one row per student."""
    df = load_data()
    return df[df["week"] == 8].copy()


# ─────────────────────────────────────────────
# 2. COHORT SUMMARY  (Overview KPIs)
# ─────────────────────────────────────────────

def cohort_summary() -> dict:
    df = get_week8()
    total = len(df)
    risk_counts = df["risk_category"].value_counts().to_dict()

    return {
        "total_students": total,
        "high_risk_count": int(risk_counts.get("High Risk", 0)),
        "medium_risk_count": int(risk_counts.get("Medium Risk", 0)),
        "low_risk_count": int(risk_counts.get("Low Risk", 0)),
        "retention_rate": round(df["retained_next_semester"].mean() * 100, 1),
        "avg_fsi": round(df["freshman_success_index"].mean(), 2),
        "avg_midterm_gpa": round(df["midterm_gpa"].mean(), 2),
        "avg_attendance": round(df["attendance_pct"].mean() * 100, 1),
        "avg_stress": round(df["stress_score"].mean(), 2),
        "avg_belonging": round(df["belonging_score"].mean(), 2),
        "students_zero_tutoring": int((df["tutoring_visits"] == 0).sum()),
        "students_low_attendance": int((df["attendance_pct"] < 0.65).sum()),
    }


# ─────────────────────────────────────────────
# 3. WEEKLY TRENDS
# ─────────────────────────────────────────────

def weekly_trends() -> list[dict]:
    df = load_data()
    grouped = (
        df.groupby("week")
        .agg(
            avg_fsi=("freshman_success_index", "mean"),
            avg_gpa=("midterm_gpa", "mean"),
            avg_attendance=("attendance_pct", "mean"),
            avg_stress=("stress_score", "mean"),
            avg_belonging=("belonging_score", "mean"),
            high_risk_count=("risk_category", lambda x: (x == "High Risk").sum()),
        )
        .reset_index()
        .round(3)
    )
    return grouped.to_dict("records")


# ─────────────────────────────────────────────
# 4. STUDENT LIST  (filterable / sortable)
# ─────────────────────────────────────────────

def student_list(
    risk_filter: list[str] | None = None,
    sort_by: str = "freshman_success_index",
    sort_dir: str = "asc",
    search_id: int | None = None,
) -> list[dict]:
    df = get_week8()

    # Optional filter by risk category
    if risk_filter:
        df = df[df["risk_category"].isin(risk_filter)]

    # Optional filter by student ID
    if search_id is not None:
        df = df[df["student_id"] == search_id]

    # Sort
    ascending = sort_dir.lower() != "desc"
    if sort_by in df.columns:
        df = df.sort_values(sort_by, ascending=ascending)

    cols = [
        "student_id", "risk_category", "freshman_success_index",
        "midterm_gpa", "attendance_pct", "assignments_completed_pct",
        "stress_score", "belonging_score", "study_hours",
        "tutoring_visits", "office_hour_visits", "lms_logins",
        "retained_next_semester",
    ]
    return _clean(df[cols])


# ─────────────────────────────────────────────
# 5. SINGLE STUDENT PROFILE
# ─────────────────────────────────────────────

def student_profile(student_id: int) -> dict | None:
    df8 = get_week8()
    row = df8[df8["student_id"] == student_id]
    if row.empty:
        return None

    s = row.iloc[0].to_dict()

    # 8-week FSI trend for sparkline
    all_df = load_data()
    trend_df = (
        all_df[all_df["student_id"] == student_id]
        .sort_values("week")[["week", "freshman_success_index"]]
    )
    s["fsi_trend"] = trend_df["freshman_success_index"].round(2).tolist()

    # Percentile ranks (vs whole cohort at week 8)
    s["fsi_percentile"] = _percentile(df8["freshman_success_index"], s["freshman_success_index"])
    s["gpa_percentile"] = _percentile(df8["midterm_gpa"], s["midterm_gpa"])
    s["attendance_percentile"] = _percentile(df8["attendance_pct"], s["attendance_pct"])

    # Recommended actions
    s["recommended_actions"] = _recommend(s)

    # Clean numpy types
    return {k: _to_python(v) for k, v in s.items()}


# ─────────────────────────────────────────────
# 6. CONTACT PRIORITY LIST
# ─────────────────────────────────────────────

def contact_list(top_n: int = 67) -> list[dict]:
    """
    Returns the priority outreach list sorted by urgency:
    High Risk first, then by FSI ascending (lowest FSI = most urgent).
    """
    df = get_week8()

    risk_order = {"High Risk": 0, "Medium Risk": 1, "Low Risk": 2}
    df["risk_rank"] = df["risk_category"].map(risk_order)
    df = df.sort_values(["risk_rank", "freshman_success_index"], ascending=[True, True])

    # FSI drop: week 1 → week 8
    all_df = load_data()
    w1 = all_df[all_df["week"] == 1].set_index("student_id")["freshman_success_index"]
    w8 = all_df[all_df["week"] == 8].set_index("student_id")["freshman_success_index"]
    fsi_drop = (w1 - w8).rename("fsi_drop_w1_w8")

    df = df.join(fsi_drop, on="student_id")

    cols = [
        "student_id", "risk_category", "freshman_success_index",
        "midterm_gpa", "attendance_pct", "stress_score",
        "belonging_score", "tutoring_visits", "fsi_drop_w1_w8",
    ]
    return _clean(df[cols].head(top_n))


# ─────────────────────────────────────────────
# 7. ANALYTICS — GPA BUCKETS & RETENTION
# ─────────────────────────────────────────────

def gpa_retention_breakdown() -> list[dict]:
    df = get_week8()
    bins = [0, 1.0, 1.5, 2.0, 2.5, 3.0, 4.1]
    labels = ["<1.0", "1.0–1.5", "1.5–2.0", "2.0–2.5", "2.5–3.0", "3.0+"]
    df["gpa_bucket"] = pd.cut(df["midterm_gpa"], bins=bins, labels=labels, right=False)
    result = (
        df.groupby("gpa_bucket", observed=True)
        .agg(count=("student_id", "count"), retained=("retained_next_semester", "sum"))
        .reset_index()
    )
    result["retention_rate"] = (result["retained"] / result["count"] * 100).round(1)
    return result.to_dict("records")


def attendance_retention_breakdown() -> list[dict]:
    df = get_week8()
    bins = [0, 0.6, 0.7, 0.8, 0.9, 1.01]
    labels = ["<60%", "60–70%", "70–80%", "80–90%", "90–100%"]
    df["att_bucket"] = pd.cut(df["attendance_pct"], bins=bins, labels=labels, right=False)
    result = (
        df.groupby("att_bucket", observed=True)
        .agg(count=("student_id", "count"), retained=("retained_next_semester", "sum"))
        .reset_index()
    )
    result["retention_rate"] = (result["retained"] / result["count"] * 100).round(1)
    return result.to_dict("records")


def risk_group_averages() -> list[dict]:
    df = get_week8()
    metrics = [
        "freshman_success_index", "midterm_gpa", "attendance_pct",
        "stress_score", "belonging_score", "study_hours",
        "tutoring_visits", "office_hour_visits", "lms_logins",
    ]
    result = df.groupby("risk_category")[metrics].mean().round(3).reset_index()
    return result.to_dict("records")


# ─────────────────────────────────────────────
# 8. STUDENT FSI TRENDS (all 200 students)
# ─────────────────────────────────────────────

def all_student_trends() -> dict[str, list[float]]:
    """Returns {student_id: [fsi_wk1, ..., fsi_wk8]} for every student."""
    df = load_data()
    trends = {}
    for sid, grp in df.groupby("student_id"):
        trends[str(sid)] = grp.sort_values("week")["freshman_success_index"].round(2).tolist()
    return trends


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def _percentile(series: pd.Series, value: float) -> int:
    return int(round((series <= value).mean() * 100))


def _to_python(v):
    if isinstance(v, (np.integer,)): return int(v)
    if isinstance(v, (np.floating,)): return float(v)
    if isinstance(v, float) and np.isnan(v): return None
    return v


def _clean(df: pd.DataFrame) -> list[dict]:
    return [{k: _to_python(v) for k, v in row.items()} for row in df.to_dict("records")]


def _recommend(s: dict) -> list[str]:
    actions = []
    if s.get("risk_category") == "High Risk":
        actions.append("Schedule immediate outreach call with advisor")
    if s.get("stress_score", 0) >= 7:
        actions.append("Refer to counseling / mental health services")
    if s.get("tutoring_visits", 1) == 0:
        actions.append("Enroll in peer tutoring program")
    if s.get("belonging_score", 10) <= 3:
        actions.append("Connect with student clubs or community groups")
    if s.get("attendance_pct", 1.0) < 0.70:
        actions.append("Trigger attendance intervention protocol")
    if s.get("midterm_gpa", 4.0) < 1.5:
        actions.append("Academic probation warning — meet with department chair")
    if not actions:
        actions.append("Continue regular check-ins — student on track")
    return actions
