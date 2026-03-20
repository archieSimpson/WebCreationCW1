# Gull Migration Analytics API & Dashboard

A full-stack application for analysing gull migration using tracking data enriched with historical weather. Includes a FastAPI backend, PostgreSQL (Render), and a React + Leaflet dashboard.

---

## 🚀 Live

* Backend (Render): [https://your-render-service.onrender.com](https://your-render-service.onrender.com)
* Frontend: Loccally run [http://localhost:5173](http://localhost:5173)

---

## ⚡ Quick Start

```bash
git clone https://github.com/your-username/WebCreationCW1.git
cd gull-tracker-api
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill DATABASE_URL and SECRET_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:

```bash
cd gull-ui
npm install
npm run dev
```

---

## 🏗️ Stack

* **Backend:** FastAPI
* **DB:** PostgreSQL (Render managed)
* **Frontend:** React + Leaflet

---

## 🗄️ Database (Render)

Use environment variables (never commit secrets):

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:PORT/DB_NAME?sslmode=require
SECRET_KEY=your_secret_key
```

**Notes**

* Use **Internal Database URL** on Render (deployed backend)
* Use **External Database URL** locally

---

## 📡 API

**Gulls**

* `GET /api/v1/gulls/`
* `POST /api/v1/gulls/`
* `GET /api/v1/gulls/{id}`
* `PUT /api/v1/gulls/{id}`
* `DELETE /api/v1/gulls/{id}`

**Trackpoints**

* `GET /api/v1/trackpoints`
* `POST /api/v1/trackpoints`
* `PUT /api/v1/trackpoints/{id}`
* `DELETE /api/v1/trackpoints/{id}`

**Weather**

* `GET /api/v1/weather`
* `POST /api/v1/weather`
* `PUT /api/v1/weather/{id}`
* `DELETE /api/v1/weather/{id}`

**Analytics**

* `GET /api/v1/gulls/{id}/movement-summary`
* `GET /api/v1/gulls/{id}/route-with-weather`
* `GET /api/v1/trackpoints/{id}/weather`

---

## 📊 Features

* Interactive map with playback
* Temperature-coloured routes
* Start/end markers
* Movement analytics (distance, duration, averages)
* CRUD data manager UI

---

## ⚡ Performance

Current implementation performs **live weather matching** during route queries.

* ✅ High analytical accuracy
* ❌ Slower for large routes

*Future work:* precompute weather and store enriched trackpoints to eliminate runtime matching.

---

## 🧪 Testing

```bash
pytest -v
```

---

## 🔐 Security

* Do not commit `.env`
* Use environment variables locally and in Render
* Never expose `DATABASE_URL`

---

## 📂 Structure

```
backend/
  app/
  tests/
  alembic/
frontend/
  src/
```

---

## 📚 Data

* Wikelski et al. (2015) gull migration dataset
* Open-Meteo archive API

---

## 👤 Author

Archie Simpson — University of Leeds (COMP3011)
