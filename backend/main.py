"""
main.py
-------
FastAPI application for the Freshman Success Intelligence Platform.

Run locally:
    uvicorn backend.main:app --reload

Then open: http://localhost:8000
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from typing import Optional
import backend.analytics as analytics

# ─────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────

app = FastAPI(
    title="Freshman Success Intelligence API",
    description="Backend API for the student success & retention BI dashboard.",
    version="1.0.0",
    docs_url="/api/docs",        # Swagger UI at /api/docs
    redoc_url="/api/redoc",
)

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"


# ─────────────────────────────────────────────
# SERVE FRONTEND
# ─────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def serve_dashboard():
    """Serve the main HTML dashboard."""
    index = FRONTEND_DIR / "index.html"
    if not index.exists():
        raise HTTPException(status_code=404, detail="Frontend not found")
    return FileResponse(index)


# ─────────────────────────────────────────────
# API ROUTES
# ─────────────────────────────────────────────

@app.get("/api/summary", tags=["Overview"])
def get_summary():
    """
    Returns high-level cohort KPIs:
    - total students, risk counts, retention rate, avg GPA/FSI/attendance, etc.
    """
    return analytics.cohort_summary()


@app.get("/api/weekly-trends", tags=["Trends"])
def get_weekly_trends():
    """
    Returns week-by-week averages (weeks 1–8) for:
    FSI, GPA, attendance, stress, belonging, and high-risk count.
    """
    return analytics.weekly_trends()


@app.get("/api/students", tags=["Students"])
def get_students(
    risk: Optional[str] = Query(
        default=None,
        description="Comma-separated risk filters. E.g. 'High Risk,Medium Risk'"
    ),
    sort_by: str = Query(default="freshman_success_index", description="Column to sort by"),
    sort_dir: str = Query(default="asc", description="'asc' or 'desc'"),
    search_id: Optional[int] = Query(default=None, description="Filter by exact student_id"),
):
    """
    Returns the full student list for Week 8.
    Supports filtering by risk category, sorting, and searching by ID.
    """
    risk_filter = [r.strip() for r in risk.split(",")] if risk else None
    return analytics.student_list(
        risk_filter=risk_filter,
        sort_by=sort_by,
        sort_dir=sort_dir,
        search_id=search_id,
    )


@app.get("/api/students/{student_id}", tags=["Students"])
def get_student_profile(student_id: int):
    """
    Returns detailed profile for a single student, including:
    - All Week 8 metrics
    - 8-week FSI trend (sparkline data)
    - Percentile rankings vs cohort
    - Recommended intervention actions
    """
    profile = analytics.student_profile(student_id)
    if profile is None:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    return profile


@app.get("/api/contact-list", tags=["Outreach"])
def get_contact_list(
    top_n: int = Query(default=67, ge=1, le=200, description="How many students to return")
):
    """
    Returns the priority outreach list — students sorted by urgency
    (High Risk first, then by lowest FSI score).
    Use this to decide who to call first.
    """
    return analytics.contact_list(top_n=top_n)


@app.get("/api/analytics/gpa-retention", tags=["Analytics"])
def get_gpa_retention():
    """
    Returns GPA bucket breakdown with retention rates.
    Useful for the GPA vs Retention bar chart.
    """
    return analytics.gpa_retention_breakdown()


@app.get("/api/analytics/attendance-retention", tags=["Analytics"])
def get_attendance_retention():
    """
    Returns attendance bucket breakdown with retention rates.
    """
    return analytics.attendance_retention_breakdown()


@app.get("/api/analytics/risk-group-averages", tags=["Analytics"])
def get_risk_group_averages():
    """
    Returns average metrics (GPA, stress, study hours, etc.)
    broken down by risk category (High / Medium / Low).
    """
    return analytics.risk_group_averages()


@app.get("/api/analytics/student-trends", tags=["Analytics"])
def get_all_student_trends():
    """
    Returns 8-week FSI trend for every student.
    Format: { "1": [77.7, 67.9, ...], "2": [...], ... }
    Used for the scatter chart and sparklines.
    """
    return analytics.all_student_trends()


# ─────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────

@app.get("/api/health", tags=["System"])
def health_check():
    """Simple health check — useful for deployment monitoring."""
    return {"status": "ok", "message": "Freshman Success API is running"}
