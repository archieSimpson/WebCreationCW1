# Gull Migration Analytics API & Dashboard

A full-stack web application for analysing animal migration patterns using real-world gull tracking data enriched with historical weather conditions. The system provides a RESTful API, interactive map visualisation, and data management interface.

---

# 🚀 Live Deployment

* **Backend (Render):**
  `https://your-render-service.onrender.com`

* **Frontend (Local or deployed separately):**
  `http://localhost:5173`

---

# 📊 Features

## Backend (FastAPI)

* RESTful API for:

  * Gulls
  * Trackpoints (movement data)
  * Weather observations
* Analytical endpoints:

  * Movement summary (distance, duration, averages)
  * Route with weather enrichment
* PostgreSQL database hosted on **Render**
* Fully tested with `pytest` (CRUD + analytics coverage)

## Frontend (React + Leaflet)

* Interactive migration map
* Time slider playback
* Temperature-coloured routes
* Start / end markers
* Live analytics dashboard
* Data management UI (CRUD interface)

## Data

* Real gull migration dataset (Wikelski et al. 2015)
* Weather data matched using Open-Meteo archive API
* Preprocessed CSV import pipeline

---

# 🏗️ Architecture

```
Frontend (React + Leaflet)
        ↓
FastAPI Backend (Render)
        ↓
PostgreSQL Database (Render)
```

---

# 🗄️ Database (Render PostgreSQL)

This project uses a **managed PostgreSQL database hosted on Render**.

## Environment Variables

Your `.env` file should contain:

```
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME?sslmode=require
SECRET_KEY=your_secret_key
```

### Important

* Always use **`sslmode=require`** for Render databases
* Do NOT include `export DATABASE_URL=...` inside the value
* The value must be a clean connection string

---

## Render Setup

### 1. Create PostgreSQL Database

* Go to Render Dashboard
* Click **New → PostgreSQL**
* Copy the **Internal Database URL**

### 2. Create Web Service

* New → Web Service
* Connect your GitHub repo
* Set:

  * Build command:

    ```
    pip install -r requirements.txt
    ```
  * Start command:

    ```
    uvicorn app.main:app --host 0.0.0.0 --port 10000
    ```

### 3. Add Environment Variables

In Render → Environment:

```
DATABASE_URL=<Internal Database URL>
SECRET_KEY=your_secret_key
```

### 4. Deploy

* Click **Deploy**
* Wait for build to complete

---

# 🧪 Local Development Setup

## 1. Clone Repository

```
git clone https://github.com/your-username/gull-tracker-api.git
cd gull-tracker-api
```

## 2. Create Virtual Environment

```
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```
pip install -r requirements.txt
```

## 4. Configure Environment

Create `.env`:

```
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME?sslmode=require
SECRET_KEY=your_secret_key
```

## 5. Run Migrations

```
alembic upgrade head
```

## 6. Run Backend

```
uvicorn app.main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

---

# 🌐 Frontend Setup

```
cd gull-ui
npm install
npm run dev
```

Make sure API URL is set:

```js
const API = "http://127.0.0.1:8000";
```

If using deployed backend:

```js
const API = "https://your-render-service.onrender.com";
```

---

# 📡 API Endpoints

## Gulls

* `GET /api/v1/gulls/`
* `POST /api/v1/gulls/`
* `GET /api/v1/gulls/{id}`
* `PUT /api/v1/gulls/{id}`
* `DELETE /api/v1/gulls/{id}`

## Trackpoints

* `GET /api/v1/trackpoints`
* `POST /api/v1/trackpoints`
* `PUT /api/v1/trackpoints/{id}`
* `DELETE /api/v1/trackpoints/{id}`

## Weather

* `GET /api/v1/weather`
* `POST /api/v1/weather`
* `PUT /api/v1/weather/{id}`
* `DELETE /api/v1/weather/{id}`

## Analytics

* `GET /api/v1/gulls/{id}/movement-summary`
* `GET /api/v1/gulls/{id}/route-with-weather`
* `GET /api/v1/trackpoints/{id}/weather`

---

# 📈 Analytical Capabilities

* Total migration distance (Haversine formula)
* Duration of migration
* Average step distance
* Average temperature along route
* Average precipitation
* Weather-linked movement insights

---

# ⚡ Performance Considerations

The system currently performs **live weather matching** when retrieving routes.

### Trade-off:

* ✅ High analytical accuracy
* ❌ Slower response time for large datasets

### Future Improvement:

* Precompute weather during data import
* Store enriched trackpoints in database
* Replace dynamic matching with direct joins

---

# 🧪 Testing

Run all tests:

```
pytest -v
```

Includes:

* CRUD tests
* API validation tests
* Analytics tests

---

# 📂 Project Structure

```
backend/
│
├── app/
│   ├── api/
│   ├── models/
│   ├── schemas/
│   ├── core/
│   └── main.py
│
├── tests/
├── alembic/
├── requirements.txt
└── .env

frontend/
│
├── src/
│   ├── GullMapUI.jsx
│   ├── DataManagerUI.jsx
│   └── main.jsx
```

---

# 📊 Data Pipeline

1. Load gull migration CSV
2. Call Open-Meteo API per trackpoint
3. Save enriched dataset:

   ```
   output_gulls_with_weather.csv
   ```
4. Import into PostgreSQL

---

# 🧠 Design Decisions

* FastAPI for performance and automatic documentation
* PostgreSQL for relational queries and scalability
* React + Leaflet for geospatial visualisation
* Separation of:

  * data storage
  * analytics
  * visualisation

---

# 🧾 Coursework Alignment

This project demonstrates:

* RESTful API design
* Database modelling
* External API integration
* Data enrichment pipelines
* Analytical computation
* Frontend-backend integration
* Performance trade-off awareness

---

# 🔮 Future Enhancements

* Precomputed weather joins (performance boost)
* Route clustering and simplification
* Wind vector visualisation
* Migration prediction models
* Deployment of frontend on Render/Netlify

---

# 📚 References

* Open-Meteo API
* Wikelski et al. (2015) Gull migration dataset
* FastAPI documentation
* Leaflet.js documentation

---

# 👤 Author

Archie Simpson
University of Leeds – Computer Science
COMP3011 Web Services Coursework

---
