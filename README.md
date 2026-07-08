# 🎓 Freshman Success Intelligence Platform

> A full-stack BI dashboard and REST API for identifying at-risk college freshmen and prioritizing advisor outreach — built with FastAPI + Python + interactive JavaScript charts.

---

## 📌 What This Project Does

Every semester, colleges enroll hundreds of new freshmen — and a significant portion quietly struggle before anyone notices. This platform ingests weekly behavioral, academic, and wellbeing data for an entire freshman cohort and surfaces:

- **Who needs help right now** — a ranked contact list sorted by urgency
- **Why they're at risk** — low GPA, high stress, poor attendance, low belonging
- **How the cohort is trending** — week-by-week FSI, GPA, and stress indicators
- **What actions to take** — tailored intervention recommendations per student

---

## 🖥️ Live Demo

>  🚀 [Live Demo](https://freshman-success-platform.onrender.com)

---

## ✨ Features

| Feature | Details |
|---|---|
| 📊 Executive Dashboard | KPI strip, FSI distribution histogram, risk donut chart |
| 📋 Priority Contact List | Sortable, filterable table — click any student for a full profile |
| 📈 Trend Analysis | 8-week FSI, GPA, stress & belonging trends for the full cohort |
| 🔬 Deep Analytics | Scatter plots, GPA vs retention, attendance vs retention, LMS usage |
| 👤 Student Profiles | Per-student panel with 8-week sparkline, percentile ranks, and recommended actions |
| ⚡ REST API | Full FastAPI backend with 9 documented endpoints + Swagger UI |

---

## 🛠️ Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — modern async Python API framework
- [Pandas](https://pandas.pydata.org/) — data processing and aggregation
- [Uvicorn](https://www.uvicorn.org/) — ASGI server

**Frontend**
- Vanilla HTML/CSS/JavaScript — no build step needed
- [Chart.js](https://www.chartjs.org/) — interactive charts (histogram, scatter, donut, line, bar)
- Dark-mode UI with a custom design system

**Data**
- Synthetic dataset: 200 students × 8 weeks × 24 metrics
- Excel source file processed entirely in Python

---

## 📁 Project Structure

```
freshman-success-platform/
│
├── backend/
│   ├── __init__.py
│   ├── main.py          ← FastAPI app + all API routes
│   ├── analytics.py     ← Data engine (risk scoring, trends, profiles)
│   └── data/
│       └── students.xlsx
│
├── frontend/
│   └── index.html       ← Full dashboard (self-contained)
│
├── requirements.txt
├── .gitignore
├── run.py               ← One-click launcher
└── README.md
```

---

## 🚀 Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/freshman-success-platform.git
cd freshman-success-platform
```

**2. Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Start the server**
```bash
python run.py
```

The app opens automatically at **http://localhost:8000**

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Serves the dashboard |
| GET | `/api/summary` | Cohort KPIs |
| GET | `/api/weekly-trends` | Week-by-week averages |
| GET | `/api/students` | Full student list (filterable, sortable) |
| GET | `/api/students/{id}` | Single student profile + recommendations |
| GET | `/api/contact-list` | Priority outreach list |
| GET | `/api/analytics/gpa-retention` | GPA bucket → retention rate |
| GET | `/api/analytics/attendance-retention` | Attendance bucket → retention rate |
| GET | `/api/analytics/risk-group-averages` | Averages by risk category |
| GET | `/api/health` | Server health check |

📖 **Interactive API docs:** `http://localhost:8000/api/docs`

---

## 📊 Key Findings from the Data

- **Midterm GPA** is the strongest dropout predictor (r = 0.71)
- Students with GPA below 1.5 have an **82% dropout rate**
- High-risk students average **stress score 6.6** vs 3.8 for low-risk
- Students with **0 tutoring visits** drop out at significantly higher rates
- **67 of 200** students (33.5%) require immediate outreach this semester

---

## 🗺️ Roadmap

- [ ] Add authentication (JWT) for advisor login
- [ ] Email / SMS outreach trigger directly from the dashboard
- [ ] Upload new semester data via UI (no code needed)
- [ ] Predictive ML model for dropout probability
- [ ] Export contact list to CSV / PDF

---

## 👤 Author

Built by Bhagwant Negi · [LinkedIn][(https://www.linkedin.com/in/bhagwant-negi/) · 

---

## 📄 License

MIT — free to use, modify, and share.
