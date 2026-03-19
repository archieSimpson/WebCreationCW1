# Gull Tracker API & Analytics Platform

## Overview

This project is a full-stack **data-driven web API system** for analysing gull migration patterns using spatial-temporal data enriched with environmental (weather) observations.

It demonstrates:

* RESTful API design
* database integration
* analytical endpoint development
* full-stack visualisation

The system goes beyond basic CRUD by providing **movement analytics and environmental correlation**, aligning with real-world data systems.

---

## Live Deployment

* Backend (Render): https://YOUR-RENDER-URL.onrender.com
* Frontend (Local): http://localhost:5173

---

## Features

### Core API

* Full CRUD operations for:

  * Gulls
  * Trackpoints
  * Weather observations
* Filtering (e.g. by species, gull_id)
* Proper HTTP status codes:

  * 201 Created
  * 404 Not Found
  * 409 Conflict
  * 204 No Content

---

### Analytical Features (Key Differentiator)

#### Movement Summary

`GET /gulls/{id}/movement-summary`

* Total distance (Haversine)
* Duration
* Average step distance
* Average temperature & precipitation

#### Route with Weather

`GET /gulls/{id}/route-with-weather`

* Combines movement + weather data
* Enables environmental analysis

#### Weather Matching

`GET /trackpoints/{id}/weather`

* Spatial + temporal matching algorithm
* Returns:

  * nearest observation
  * time difference
  * distance

---

## Frontend Application

### Analytics Dashboard

* Interactive Leaflet map
* Route playback animation
* Temperature-coloured paths
* Summary statistics cards
* Start/end markers

### Data Manager

* Full CRUD interface
* Filtering + search
* Pagination
* Input validation

---

## Technology Stack

### Backend

* FastAPI
* SQLAlchemy
* SQLite
* Pydantic
* Pytest

### Frontend

* React (Vite)
* Leaflet / React-Leaflet

---

## Project Structure

```
app/
  api/            # API routes
  models/         # Database models
  schemas/        # Validation schemas
  services/       # Business logic
  utils/          # Geo calculations
  db/             # Database config

frontend/
  App.jsx
  GullMapUI.jsx
  DataManagerUI.jsx

tests/
  test_*.py
```

---

## Setup Instructions

### Backend

```
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

```
npm install
npm run dev
```

---

## Testing

```
pytest
```

Includes:

* endpoint testing
* validation testing
* analytics correctness

---

## Design Highlights

* Clean layered architecture
* Indexed database for performance
* Spatial-temporal analytics
* REST-compliant API design

---

## Future Improvements

* Authentication layer
* Deployment of frontend
* Advanced analytics (speed, clustering)
* Caching strategies

---

## GenAI Declaration

Generative AI tools (ChatGPT) were used for:

* system design planning
* debugging assistance
* improving documentation clarity

All outputs were critically reviewed and adapted.

---

## Repository

GitHub: [INSERT LINK]

---
