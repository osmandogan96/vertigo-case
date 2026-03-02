# Vertigo Games — Data Engineer Case Study

This repository contains the solution for the Vertigo Games Data Engineer case study, consisting of two parts: a Clan Management API and a dbt-based analytics pipeline with visualization.

---

## Part 1 — Clan API

A REST API for managing game clans, built with **FastAPI** and **PostgreSQL**, deployed on **Google Cloud Run** with **Cloud SQL**.

**Live API:** [https://clan-api-904232302569.europe-west1.run.app/](https://clan-api-904232302569.europe-west1.run.app/)  
**Swagger Docs:** [https://clan-api-904232302569.europe-west1.run.app/docs](https://clan-api-904232302569.europe-west1.run.app/docs)

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/clans/` | Create a clan (name + region) |
| `GET` | `/clans/` | List all clans |
| `GET` | `/clans/search?name=xxx` | Search by name (min 3 chars, contains) |
| `GET` | `/clans/{id}` | Get clan by UUID |
| `DELETE` | `/clans/{id}` | Delete clan by UUID |

**Tech stack:** FastAPI, SQLAlchemy, Pydantic v2, PostgreSQL 16, Docker, Google Cloud Run, Cloud SQL, Artifact Registry

→ See [`clan-api/README.md`](clan-api/README.md) for setup, deployment steps, and design decisions.

---

## Part 2 — DBT Model & Visualization

An analytics pipeline that transforms raw user-level daily metrics into an aggregated `daily_metrics` model using **dbt** on **BigQuery**, visualized with **Looker Studio**.

**Dashboard:** [Looker Studio — Daily Metrics Dashboard](https://lookerstudio.google.com/reporting/e5aed70b-1049-438c-9b89-bdface300fcf/page/oylqF?s=gl_doVbdUBY)

**Pipeline flow:**

```
csv.gz files → BigQuery (raw_data) → stg_user_daily_metrics (view) → daily_metrics (table) → Looker Studio
```

**Aggregated metrics** (by event_date, country, platform): DAU, total IAP & ad revenue, ARPDAU, matches started, match per DAU, win/defeat ratio, server errors per DAU.

**Tech stack:** dbt-core, dbt-bigquery, BigQuery, Looker Studio, Python (pandas for data quality checks)

→ See [`dbt-analyse/README.md`](dbt-analyse/README.md) for model details, assumptions, key findings, and how to run.

---

## Key Findings

### DAU Trend
Weekly pattern with peaks mid-week (~300K) and dips on weekends (~200K).

![DAU Trend](dbt-analyse/visualization/dau_trend.png)

### Revenue Breakdown
IAP revenue dominates; ad revenue remains stable. Total daily revenue ranges between ~$30K–$50K.

![Revenue](dbt-analyse/visualization/revenue_trend.png)

### Server Errors per DAU
Error rate peaked in mid-February (~0.08/user) and has since improved to ~0.03, indicating infrastructure stabilization.

![Server Errors](dbt-analyse/visualization/server_errors_per_dau.png)

### Platform & Geography
Android holds 65.4% of DAU. Türkiye is the top country, followed by Brazil, Russia, and the United States.

| | |
|---|---|
| ![Platform](dbt-analyse/visualization/dau_by_platform.png) | ![Countries](dbt-analyse/visualization/top_countries_dau.png) |

---

## Repository Structure

```
vertigo-case/
├── README.md                    # This file
├── clan-api/                    # Part 1 — REST API
│   ├── configs/                 # Environment & settings
│   ├── db/                      # SQLAlchemy models & session
│   ├── routes/                  # API endpoints
│   ├── schemas/                 # Pydantic schemas
│   ├── main.py                  # FastAPI entry point
│   ├── Dockerfile               # Container image
│   ├── docker-compose.yml       # Local dev (API + PostgreSQL)
│   ├── requirements.txt
│   └── README.md
└── dbt-analyse/                 # Part 2 — dbt + Visualization
    ├── configs/                 # GCP project config
    ├── models/
    │   ├── staging/             # stg_user_daily_metrics (cleaning)
    │   └── marts/               # daily_metrics (aggregation)
    ├── visualization/           # Dashboard screenshots
    ├── data_quality_check.py    # Pre-modeling data inspection
    ├── upload_to_bq.py          # CSV → BigQuery loader
    ├── dbt_project.yml
    ├── profiles.yml
    ├── requirements.txt
    └── README.md
```

---

## Quick Start

### Part 1 — Run the API locally

```bash
cd clan-api
docker-compose up --build -d
# API → http://localhost:8080
# Docs → http://localhost:8080/docs
```

### Part 2 — Run the dbt pipeline

```bash
cd dbt-analyse
pip install -r requirements.txt

# Authenticate with GCP
gcloud auth login
gcloud auth application-default login
export GCP_PROJECT_ID=<YOUR_PROJECT_ID>

# Upload raw data & run models
python upload_to_bq.py
dbt run
dbt test
```

---

## Author

Osman Doğan  
Case study completed for the Vertigo Games Data Engineer position.
