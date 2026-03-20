# Gull Migration Analytics API

A full-stack platform for analysing bird migration patterns using GPS tracking data enhanced with historical weather data.

This project provides a production-style REST API alongside an interactive geospatial dashboard, enabling users to explore migration routes, environmental conditions, and derived movement analytics.

---

## Live System

* **API Base URL**
  https://webcreationcw1.onrender.com

* **API Documentation (Swagger UI)**
  https://webcreationcw1.onrender.com/docs

---

## Project Overview

This system models migration behaviour by combining:

* **Tracking data** – latitude, longitude, timestamps
* **Weather observations** – temperature, precipitation, wind, pressure
* **Derived analytics** – distance travelled, duration, environmental conditions

---

## Key Features

### REST API

A fully featured RESTful API with versioned endpoints:

* `Gulls` – species and metadata
* `Trackpoints` – movement observations
* `Weather` – environmental data

Includes:

* Full CRUD operations
* Filtering and querying
* Structured JSON responses
* Auto-generated OpenAPI documentation

---

### Architecture

The backend follows a clean, modular structure:

```
app/
├── api/           # HTTP endpoints
├── models/        # Database models
├── schemas/       # Data validation
├── services/      # Core business logic
├── utils/         # Utility functions
├── db/            # Database configuration
└── core/          # Application settings
```

---

### Data Model

* **Gull → Trackpoints** (one-to-many relationship)
* Weather stored independently for flexibility and scalability

Indexes are used to optimise:

* Time-based queries
* Spatial matching operations

---

### Geospatial & Analytical Logic

* Haversine formula used for accurate distance calculations
* Weather matching algorithm:

  * Filters by time window (±3 hours)
  * Applies spatial bounding box
  * Selects nearest candidate

---

### Testing

The project includes a comprehensive automated test suite covering:

* API endpoints
* Data validation
* Analytical computations
* Error handling

Run locally:

```bash
pytest -v
```

---
<img width="220" height="111" alt="image" src="https://github.com/user-attachments/assets/f0eeba14-c49b-4e46-9825-f5f6d745a46a" />
<img width="276" height="90" alt="image" src="https://github.com/user-attachments/assets/b9d755cf-1191-4ac2-a4ac-f938b7ca5ba7" />
<img width="256" height="142" alt="image" src="https://github.com/user-attachments/assets/91682d98-9b9d-40c7-8dc4-d40b5c8d01f9" />



## Frontend Dashboard

A React + Leaflet interface for exploring migration data visually.

Features:

* Interactive map visualisation
* Playback of migration routes (time slider)
* Temperature-based route colouring
* Live summary statistics
* Full CRUD data manager

---

### Run Frontend Locally

```bash
cd gull-ui
npm install
npm run dev
```

Open:

```
http://localhost:5173
```

---

## Backend Setup

### Clone Repository

```bash
git clone https://github.com/archieSimpson/WebCreationCW1.git
cd WebCreationCW1/backend
```

---

### Install Dependencies

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### Configure Environment

Create `.env`:

```env
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/gull_tracker
API_V1_STR=/api/v1
PROJECT_NAME=Gull Tracker API
```

---

### Run Migrations

```bash
alembic upgrade head
```

---

### Start Server

```bash
uvicorn app.main:app --reload
```

Access docs:

```
http://127.0.0.1:8000/docs
```

---

## Deployment

* **Backend:** Render
* **Database:** PostgreSQL
* **API Docs:** Swagger (FastAPI)

---

## Data Sources

* https://www.movebank.org/cms/movebank-main
* [Historical weather observations aligned to tracking points](https://open-meteo.com)

---


## Author

Archie Simpson

---
