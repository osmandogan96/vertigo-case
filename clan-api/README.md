# Vertigo Games — Clan Management API

REST API for managing game clans. Built with **FastAPI** + **PostgreSQL**, deployed on **Google Cloud Run** with **Cloud SQL**.

**Live URL:** [https://clan-api-904232302569.europe-west1.run.app/](https://clan-api-904232302569.europe-west1.run.app/)

---

## Project Structure

```
clan-api/
├── configs/
│   ├── .env                 # Environment variables (not committed)
│   └── config.py            # Settings loader (reads from env vars)
├── db/
│   ├── session.py           # SQLAlchemy engine & session factory
│   └── models.py            # Clan ORM model (UUID, timestamps in UTC)
├── routes/
│   └── route.py             # API endpoints (CRUD + search)
├── schemas/
│   └── schemas.py           # Pydantic request/response models
├── main.py                  # FastAPI app entry point with lifespan
├── Dockerfile               # Production container image
├── docker-compose.yml       # Local development setup (API + PostgreSQL)
└── requirements.txt         # Python dependencies
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/clans/` | Create a clan (name + region) |
| `GET` | `/clans/` | List all clans (newest first) |
| `GET` | `/clans/search?name=xxx` | Search by name (min 3 chars, case-insensitive contains) |
| `GET` | `/clans/{id}` | Get a specific clan by UUID |
| `DELETE` | `/clans/{id}` | Delete a specific clan by UUID |

All responses are returned as **JSON**.

### Example Requests

```bash
# Health check
curl https://clan-api-904232302569.europe-west1.run.app/

# Create a clan
curl -X POST https://clan-api-904232302569.europe-west1.run.app/clans/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Dragon Warriors", "region": "TR"}'

# List all clans
curl https://clan-api-904232302569.europe-west1.run.app/clans/

# Search clans by name (min 3 characters)
curl "https://clan-api-904232302569.europe-west1.run.app/clans/search?name=dragon"

# Get a specific clan
curl https://clan-api-904232302569.europe-west1.run.app/clans/{clan_id}

# Delete a clan
curl -X DELETE https://clan-api-904232302569.europe-west1.run.app/clans/{clan_id}
```

## Database Schema

| Column | Type | Description |
|--------|------|-------------|
| `id` | `UUID` | Primary key, auto-generated |
| `name` | `VARCHAR` | Clan name (required, trimmed) |
| `region` | `VARCHAR` | Region code, e.g. "TR", "US" (auto-uppercased) |
| `created_at` | `TIMESTAMP WITH TZ` | Auto-generated in UTC |

## Tech Stack

- **FastAPI** — async-capable Python web framework
- **SQLAlchemy 2.0** — ORM with PostgreSQL dialect
- **Pydantic v2** — request/response validation
- **PostgreSQL 16** — relational database (Cloud SQL in production)
- **Docker** — containerized deployment
- **Google Cloud Run** — serverless container hosting
- **Google Cloud SQL** — managed PostgreSQL instance
- **Artifact Registry** — Docker image storage

---

## Running Locally

```bash
# Start PostgreSQL + API with Docker Compose
docker-compose up --build -d

# Swagger docs available at:
# http://localhost:8080/docs
```

### Environment Variables

| Variable | Description | Default (local) |
|----------|-------------|-----------------|
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | `postgres` |
| `POSTGRES_SERVER` | Database host | `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `POSTGRES_DB` | Database name | `vertigo_clans` |
| `PORT` | API server port | `8080` |

---

## Cloud Deployment (Google Cloud Run + Cloud SQL)

### Prerequisites

- Google Cloud SDK (`gcloud`) installed and authenticated
- A GCP project created
- Billing enabled on the project

### Step 1 — Enable Required Services

```bash
gcloud services enable artifactregistry.googleapis.com \
  --project=<YOUR_PROJECT_ID>
```

### Step 2 — IAM Permissions

Grant the necessary roles to your user account and the Compute Engine default service account:

```bash
# User account permissions
gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
  --member="user:<YOUR_EMAIL>" \
  --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
  --member="user:<YOUR_EMAIL>" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
  --member="user:<YOUR_EMAIL>" \
  --role="roles/owner"

# Service account permissions (for Cloud Build)
gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
  --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
  --role="roles/storage.admin"

gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
  --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding <YOUR_PROJECT_ID> \
  --member="serviceAccount:<PROJECT_NUMBER>-compute@developer.gserviceaccount.com" \
  --role="roles/logging.logWriter"
```

### Step 3 — Create Artifact Registry Repository

```bash
gcloud artifacts repositories create clan-api-repo \
  --repository-format=docker \
  --location=europe-west1 \
  --project=<YOUR_PROJECT_ID>
```

### Step 4 — Build & Push Docker Image

```bash
gcloud builds submit \
  --tag europe-west1-docker.pkg.dev/<YOUR_PROJECT_ID>/clan-api-repo/clan-api
```

### Step 5 — Create Cloud SQL Instance

Create a PostgreSQL instance via the GCP Console or CLI, then note the **instance connection name** (format: `PROJECT_ID:REGION:INSTANCE_NAME`).

### Step 6 — Deploy to Cloud Run

```bash
gcloud run deploy clan-api \
  --image europe-west1-docker.pkg.dev/<YOUR_PROJECT_ID>/clan-api-repo/clan-api \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --add-cloudsql-instances <YOUR_PROJECT_ID>:<SQL_REGION>:<SQL_INSTANCE_NAME> \
  --set-env-vars \
    POSTGRES_USER=<DB_USER>,\
    POSTGRES_PASSWORD=<DB_PASSWORD>,\
    POSTGRES_SERVER=<DB_HOST_OR_SOCKET>,\
    POSTGRES_PORT=<DB_PORT>,\
    POSTGRES_DB=<DB_NAME>
```

After deployment, Cloud Run will provide a public URL where the API is accessible.

---

## Design Decisions

1. **UUID as primary key** — ensures globally unique identifiers, safe for distributed systems.
2. **UTC timestamps** — all `created_at` values are stored in UTC as required by the case specification.
3. **Case-insensitive search** — clan name search uses `LOWER()` + `LIKE` for flexible matching.
4. **Input validation** — Pydantic validators trim whitespace, reject blank names, and auto-uppercase region codes.
5. **Connection pooling** — SQLAlchemy engine configured with `pool_pre_ping`, `pool_size=5`, and `max_overflow=10` for production readiness.
6. **Lifespan event** — database tables are auto-created on application startup using SQLAlchemy's `create_all`.
