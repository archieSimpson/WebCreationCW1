import { useEffect, useMemo, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMap
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

const API = "https://webcreationcw1.onrender.com";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png"
});

function FitBounds({ points }) {
  const map = useMap();

  useEffect(() => {
    if (!points.length) return;
    const bounds = L.latLngBounds(points.map((p) => [p.lat, p.lng]));
    map.fitBounds(bounds, { padding: [40, 40] });
  }, [points, map]);

  return null;
}

function tempColor(temp) {
  if (temp === null || temp === undefined) return "#888888";

  const min = -5;
  const max = 35;
  const ratio = Math.max(0, Math.min(1, (temp - min) / (max - min)));

  const r = Math.floor(255 * ratio);
  const g = Math.floor(255 * (1 - Math.abs(ratio - 0.5) * 2));
  const b = Math.floor(255 * (1 - ratio));

  return `rgb(${r},${g},${b})`;
}

function formatNumber(value, digits = 1, suffix = "") {
  if (value === null || value === undefined || Number.isNaN(value)) return "—";
  return `${Number(value).toFixed(digits)}${suffix}`;
}

function formatRatio(current, total, digits = 1, suffix = "") {
  const currentText =
    current === null || current === undefined || Number.isNaN(current)
      ? "—"
      : Number(current).toFixed(digits);

  const totalText =
    total === null || total === undefined || Number.isNaN(total)
      ? "—"
      : Number(total).toFixed(digits);

  return `${currentText} / ${totalText}${suffix}`;
}

function formatCountRatio(current, total) {
  const currentText =
    current === null || current === undefined || Number.isNaN(current)
      ? "—"
      : String(current);

  const totalText =
    total === null || total === undefined || Number.isNaN(total)
      ? "—"
      : String(total);

  return `${currentText} / ${totalText}`;
}

function SummaryCard({ label, value }) {
  return (
    <div
      style={{
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: 12,
        padding: 14,
        minWidth: 170,
        boxShadow: "0 1px 3px rgba(0,0,0,0.08)"
      }}
    >
      <div style={{ fontSize: 13, color: "#6b7280", marginBottom: 6 }}>
        {label}
      </div>
      <div style={{ fontSize: 20, fontWeight: 700 }}>{value}</div>
    </div>
  );
}

function haversineKm(lat1, lon1, lat2, lon2) {
  const R = 6371;
  const toRad = (deg) => (deg * Math.PI) / 180;

  const dLat = toRad(lat2 - lat1);
  const dLon = toRad(lon2 - lon1);

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(lat1)) *
      Math.cos(toRad(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

function buildSummary(routePoints) {
  if (!routePoints.length) {
    return {
      totalTrackpoints: 0,
      totalDistanceKm: 0,
      durationHours: 0,
      averageStepDistanceKm: 0,
      averageTemperatureC: null,
      averagePrecipitationMm: null
    };
  }

  let totalDistanceKm = 0;

  for (let i = 1; i < routePoints.length; i += 1) {
    const prev = routePoints[i - 1];
    const curr = routePoints[i];

    totalDistanceKm += haversineKm(prev.lat, prev.lng, curr.lat, curr.lng);
  }

  const firstTime = new Date(routePoints[0].time).getTime();
  const lastTime = new Date(routePoints[routePoints.length - 1].time).getTime();
  const durationHours = Math.max(0, (lastTime - firstTime) / (1000 * 60 * 60));

  const temps = routePoints
    .map((p) => p.temp)
    .filter((v) => v !== null && v !== undefined);

  const precips = routePoints
    .map((p) => p.precipitation_mm)
    .filter((v) => v !== null && v !== undefined);

  const averageTemperatureC =
    temps.length > 0
      ? temps.reduce((sum, v) => sum + v, 0) / temps.length
      : null;

  const averagePrecipitationMm =
    precips.length > 0
      ? precips.reduce((sum, v) => sum + v, 0) / precips.length
      : null;

  const stepCount = Math.max(routePoints.length - 1, 0);
  const averageStepDistanceKm =
    stepCount > 0 ? totalDistanceKm / stepCount : 0;

  return {
    totalTrackpoints: routePoints.length,
    totalDistanceKm,
    durationHours,
    averageStepDistanceKm,
    averageTemperatureC,
    averagePrecipitationMm
  };
}

export default function GullMapUI() {
  const [gulls, setGulls] = useState([]);
  const [gullId, setGullId] = useState("");
  const [points, setPoints] = useState([]);

  const [sliderIndex, setSliderIndex] = useState(0);
  const [playing, setPlaying] = useState(false);

  const [loadingGulls, setLoadingGulls] = useState(false);
  const [loadingRoute, setLoadingRoute] = useState(false);
  const [error, setError] = useState("");

  async function loadGulls() {
    setLoadingGulls(true);
    setError("");

    try {
      const res = await fetch(`${API}/api/v1/gulls/`);
      if (!res.ok) {
        throw new Error("Failed to load gull list.");
      }

      const data = await res.json();
      setGulls(data);

      if (data.length > 0) {
        setGullId(String(data[0].id));
      }
    } catch (err) {
      setError(err.message || "Failed to load gull list.");
    } finally {
      setLoadingGulls(false);
    }
  }

  async function loadRoute(id) {
    if (!id) return;

    setLoadingRoute(true);
    setError("");
    setPlaying(false);

    try {
      const res = await fetch(`${API}/api/v1/gulls/${id}/route-with-weather`);
      if (!res.ok) {
        throw new Error("Failed to load route.");
      }

      const data = await res.json();

      const enriched = data.map((tp) => ({
        id: tp.id,
        lat: tp.latitude,
        lng: tp.longitude,
        time: tp.recorded_at,
        temp: tp.temperature_c ?? null,
        precipitation_mm: tp.precipitation_mm ?? null,
        wind_u: tp.wind_u ?? null,
        wind_v: tp.wind_v ?? null,
        surface_pressure: tp.surface_pressure ?? null
      }));

      setPoints(enriched);
      setSliderIndex(0);
    } catch (err) {
      setPoints([]);
      setSliderIndex(0);
      setError(err.message || "Failed to load route.");
    } finally {
      setLoadingRoute(false);
    }
  }

  useEffect(() => {
    loadGulls();
  }, []);

  useEffect(() => {
    if (gullId) {
      loadRoute(gullId);
    }
  }, [gullId]);

  useEffect(() => {
    if (!playing || points.length === 0) return;

    const interval = setInterval(() => {
      setSliderIndex((current) => {
        const next = Math.min(current + 3, points.length - 1);
        if (next >= points.length - 1) {
          setPlaying(false);
        }
        return next;
      });
    }, 80);

    return () => clearInterval(interval);
  }, [playing, points]);

  const visiblePoints =
    points.length > 0 ? points.slice(0, sliderIndex + 1) : [];

  const shownSummary = useMemo(() => buildSummary(visiblePoints), [visiblePoints]);
  const fullSummary = useMemo(() => buildSummary(points), [points]);

  const center = useMemo(() => {
    if (!points.length) return [20, 0];

    const avgLat = points.reduce((sum, p) => sum + p.lat, 0) / points.length;
    const avgLng = points.reduce((sum, p) => sum + p.lng, 0) / points.length;

    return [avgLat, avgLng];
  }, [points]);

  const selectedPoint = points[sliderIndex] || null;
  const start = points[0] || null;
  const end = points[points.length - 1] || null;

  const selectedGull = gulls.find((g) => String(g.id) === String(gullId));

  return (
    <div
      style={{
        padding: 20,
        background: "#f8fafc",
        minHeight: "100vh",
        fontFamily: "Arial, sans-serif"
      }}
    >
      <h2 style={{ marginBottom: 8 }}>Gull Migration Analytics Dashboard</h2>

      <div style={{ color: "#4b5563", marginBottom: 18 }}>
        Visualise tracked movement, playback migration paths, and inspect
        weather-linked route conditions.
      </div>

      <div
        style={{
          display: "flex",
          gap: 12,
          alignItems: "center",
          flexWrap: "wrap",
          marginBottom: 18
        }}
      >
        <label style={{ fontWeight: 600 }}>Select Gull:</label>

        <select
          value={gullId}
          onChange={(e) => setGullId(e.target.value)}
          disabled={loadingGulls || loadingRoute}
          style={{
            padding: "10px 12px",
            borderRadius: 8,
            border: "1px solid #cbd5e1",
            minWidth: 320,
            background: "white"
          }}
        >
          {gulls.map((gull) => (
            <option key={gull.id} value={gull.id}>
              {gull.tag_id} | {gull.species}
              {gull.common_name ? ` | ${gull.common_name}` : ""}
            </option>
          ))}
        </select>

        <button
          onClick={() => loadRoute(gullId)}
          disabled={!gullId || loadingRoute}
          style={{
            padding: "10px 14px",
            borderRadius: 8,
            border: "none",
            background: "#2563eb",
            color: "white",
            cursor: "pointer"
          }}
        >
          {loadingRoute ? "Loading..." : "Reload Route"}
        </button>
      </div>

      {error && (
        <div
          style={{
            marginBottom: 16,
            background: "#fee2e2",
            color: "#991b1b",
            padding: 12,
            borderRadius: 8,
            border: "1px solid #fecaca"
          }}
        >
          {error}
        </div>
      )}

      {selectedGull && (
        <div style={{ marginBottom: 16, color: "#374151" }}>
          <strong>Selected:</strong> {selectedGull.tag_id} — {selectedGull.species}
          {selectedGull.study_name ? ` (${selectedGull.study_name})` : ""}
        </div>
      )}

      <div
        style={{
          display: "flex",
          gap: 12,
          flexWrap: "wrap",
          marginBottom: 20
        }}
      >
        <SummaryCard
          label="Trackpoints"
          value={formatCountRatio(
            shownSummary.totalTrackpoints,
            fullSummary.totalTrackpoints
          )}
        />
        <SummaryCard
          label="Total Distance"
          value={formatRatio(
            shownSummary.totalDistanceKm,
            fullSummary.totalDistanceKm,
            1,
            " km"
          )}
        />
        <SummaryCard
          label="Duration"
          value={formatRatio(
            shownSummary.durationHours,
            fullSummary.durationHours,
            1,
            " hrs"
          )}
        />
        <SummaryCard
          label="Average Step Distance"
          value={formatNumber(shownSummary.averageStepDistanceKm, 2, " km")}
        />
        <SummaryCard
          label="Avg Temp"
          value={formatNumber(shownSummary.averageTemperatureC, 1, " °C")}
        />
        <SummaryCard
          label="Avg Precipitation"
          value={formatNumber(shownSummary.averagePrecipitationMm, 2, " mm")}
        />
      </div>

      <div
        style={{
          background: "white",
          border: "1px solid #e5e7eb",
          borderRadius: 12,
          padding: 16,
          marginBottom: 16,
          boxShadow: "0 1px 3px rgba(0,0,0,0.08)"
        }}
      >
        <div
          style={{
            display: "flex",
            gap: 12,
            alignItems: "center",
            flexWrap: "wrap"
          }}
        >
          <button
            onClick={() => setPlaying((prev) => !prev)}
            disabled={!points.length}
            style={{
              padding: "10px 14px",
              borderRadius: 8,
              border: "none",
              background: playing ? "#dc2626" : "#16a34a",
              color: "white",
              cursor: "pointer"
            }}
          >
            {playing ? "Pause" : "Play"}
          </button>

          <button
            onClick={() => {
              setPlaying(false);
              setSliderIndex(0);
            }}
            disabled={!points.length}
            style={{
              padding: "10px 14px",
              borderRadius: 8,
              border: "1px solid #cbd5e1",
              background: "white",
              cursor: "pointer"
            }}
          >
            Reset
          </button>

          <input
            type="range"
            min="0"
            max={Math.max(points.length - 1, 0)}
            value={Math.min(sliderIndex, Math.max(points.length - 1, 0))}
            onChange={(e) => {
              setPlaying(false);
              setSliderIndex(Number(e.target.value));
            }}
            style={{ width: 420 }}
          />

          <div style={{ color: "#374151" }}>
            {selectedPoint
              ? new Date(selectedPoint.time).toLocaleString()
              : "No trackpoint selected"}
          </div>
        </div>

        {selectedPoint && (
          <div
            style={{
              marginTop: 14,
              display: "flex",
              gap: 20,
              flexWrap: "wrap",
              color: "#374151",
              fontSize: 14
            }}
          >
            <span>
              <strong>Lat:</strong> {selectedPoint.lat.toFixed(4)}
            </span>
            <span>
              <strong>Lng:</strong> {selectedPoint.lng.toFixed(4)}
            </span>
            <span>
              <strong>Temp:</strong>{" "}
              {selectedPoint.temp !== null ? `${selectedPoint.temp} °C` : "—"}
            </span>
            <span>
              <strong>Precip:</strong>{" "}
              {selectedPoint.precipitation_mm !== null
                ? `${selectedPoint.precipitation_mm} mm`
                : "—"}
            </span>
            <span>
              <strong>Wind U:</strong>{" "}
              {selectedPoint.wind_u !== null ? selectedPoint.wind_u : "—"}
            </span>
            <span>
              <strong>Wind V:</strong>{" "}
              {selectedPoint.wind_v !== null ? selectedPoint.wind_v : "—"}
            </span>
          </div>
        )}
      </div>

      <div
        style={{
          position: "relative",
          height: "72vh",
          background: "white",
          borderRadius: 12,
          overflow: "hidden",
          border: "1px solid #e5e7eb",
          boxShadow: "0 1px 3px rgba(0,0,0,0.08)"
        }}
      >
        <MapContainer center={center} zoom={2} style={{ height: "100%", width: "100%" }}>
          <TileLayer
            attribution="OpenStreetMap"
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <FitBounds points={points} />

          {visiblePoints.slice(1).map((point, i) => (
            <Polyline
              key={`${visiblePoints[i].id}-${point.id}`}
              positions={[
                [visiblePoints[i].lat, visiblePoints[i].lng],
                [point.lat, point.lng]
              ]}
              pathOptions={{
                color: tempColor(point.temp),
                weight: 4,
                opacity: 0.9
              }}
            />
          ))}

          {start && (
            <Marker position={[start.lat, start.lng]}>
              <Popup>
                <strong>Start</strong>
                <br />
                {new Date(start.time).toLocaleString()}
              </Popup>
            </Marker>
          )}

          {end && (
            <Marker position={[end.lat, end.lng]}>
              <Popup>
                <strong>End</strong>
                <br />
                {new Date(end.time).toLocaleString()}
              </Popup>
            </Marker>
          )}

          {selectedPoint && (
            <Marker position={[selectedPoint.lat, selectedPoint.lng]}>
              <Popup>
                <strong>Current Playback Point</strong>
                <br />
                {new Date(selectedPoint.time).toLocaleString()}
                <br />
                Temp:{" "}
                {selectedPoint.temp !== null ? `${selectedPoint.temp} °C` : "—"}
                <br />
                Wind U: {selectedPoint.wind_u ?? "—"}
                <br />
                Wind V: {selectedPoint.wind_v ?? "—"}
              </Popup>
            </Marker>
          )}
        </MapContainer>

        <div
          style={{
            position: "absolute",
            right: 16,
            bottom: 16,
            background: "rgba(255,255,255,0.95)",
            padding: 12,
            borderRadius: 10,
            border: "1px solid #e5e7eb",
            minWidth: 180,
            zIndex: 1000,
            pointerEvents: "none"
          }}
        >
          <div style={{ fontWeight: 700, marginBottom: 8 }}>Temperature °C</div>

          <div
            style={{
              width: 160,
              height: 12,
              borderRadius: 999,
              background:
                "linear-gradient(to right, blue, cyan, green, yellow, orange, red)"
            }}
          />

          <div
            style={{
              marginTop: 6,
              display: "flex",
              justifyContent: "space-between",
              fontSize: 12,
              color: "#4b5563"
            }}
          >
            <span>-5</span>
            <span>35+</span>
          </div>
        </div>
      </div>
    </div>
  );
}