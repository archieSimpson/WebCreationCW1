import { useEffect, useMemo, useState } from "react";

const API = "http://127.0.0.1:8000";
const PAGE_SIZE = 50;

function buildUrl(path) {
  return `${API}${path.startsWith("/") ? path : `/${path}`}`;
}

async function fetchJson(path, options = {}) {
  const res = await fetch(buildUrl(path), {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {})
    },
    ...options
  });

  if (res.status === 204) {
    return null;
  }

  const contentType = res.headers.get("content-type") || "";
  const contentLength = res.headers.get("content-length");

  let data = null;

  if (contentLength === "0") {
    data = null;
  } else if (contentType.includes("application/json")) {
    const text = await res.text();
    data = text ? JSON.parse(text) : null;
  } else {
    const text = await res.text();
    data = text || null;
  }

  if (!res.ok) {
    let message = "Request failed.";

    if (data?.detail) {
      if (typeof data.detail === "string") {
        message = data.detail;
      } else if (Array.isArray(data.detail)) {
        message = data.detail
          .map((item) => item?.msg || JSON.stringify(item))
          .join(", ");
      }
    } else if (typeof data === "string" && data.trim()) {
      message = data;
    }

    throw new Error(message);
  }

  return data;
}

function SectionCard({ title, subtitle, children, rightContent }) {
  return (
    <div
      style={{
        background: "#ffffff",
        border: "1px solid #e5e7eb",
        borderRadius: 14,
        padding: 18,
        boxShadow: "0 1px 3px rgba(0,0,0,0.08)"
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 12,
          alignItems: "flex-start",
          marginBottom: 16,
          flexWrap: "wrap"
        }}
      >
        <div>
          <div style={{ fontSize: 18, fontWeight: 800, color: "#111827" }}>
            {title}
          </div>
          {subtitle ? (
            <div style={{ fontSize: 13, color: "#6b7280", marginTop: 4 }}>
              {subtitle}
            </div>
          ) : null}
        </div>
        {rightContent}
      </div>
      {children}
    </div>
  );
}

function StatusBanner({ type, text, onClose }) {
  if (!text) return null;

  const isError = type === "error";

  return (
    <div
      style={{
        marginBottom: 16,
        padding: 12,
        borderRadius: 10,
        border: `1px solid ${isError ? "#fecaca" : "#bbf7d0"}`,
        background: isError ? "#fee2e2" : "#dcfce7",
        color: isError ? "#991b1b" : "#166534",
        display: "flex",
        justifyContent: "space-between",
        gap: 12,
        alignItems: "center"
      }}
    >
      <span>{text}</span>
      <button
        type="button"
        onClick={onClose}
        style={{
          border: "none",
          background: "transparent",
          cursor: "pointer",
          color: "inherit",
          fontWeight: 700
        }}
      >
        ×
      </button>
    </div>
  );
}

function ToolbarButton({
  children,
  onClick,
  disabled,
  primary = false,
  danger = false,
  type = "button"
}) {
  let background = "#ffffff";
  let color = "#111827";
  let border = "1px solid #cbd5e1";

  if (primary) {
    background = "#2563eb";
    color = "#ffffff";
    border = "1px solid #2563eb";
  }

  if (danger) {
    background = "#dc2626";
    color = "#ffffff";
    border = "1px solid #dc2626";
  }

  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      style={{
        padding: "10px 14px",
        borderRadius: 10,
        border,
        background,
        color,
        fontWeight: 600,
        cursor: disabled ? "not-allowed" : "pointer",
        opacity: disabled ? 0.6 : 1
      }}
    >
      {children}
    </button>
  );
}

function TextInput({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
  required = false,
  step,
  min,
  max
}) {
  return (
    <label style={{ display: "block" }}>
      <div
        style={{
          fontSize: 13,
          fontWeight: 600,
          color: "#374151",
          marginBottom: 6
        }}
      >
        {label} {required ? "*" : ""}
      </div>
      <input
        type={type}
        value={value}
        step={step}
        min={min}
        max={max}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          width: "100%",
          padding: "10px 12px",
          borderRadius: 10,
          border: "1px solid #cbd5e1",
          background: "#ffffff",
          boxSizing: "border-box"
        }}
      />
    </label>
  );
}

function SelectInput({ label, value, onChange, options }) {
  return (
    <label style={{ display: "block" }}>
      <div
        style={{
          fontSize: 13,
          fontWeight: 600,
          color: "#374151",
          marginBottom: 6
        }}
      >
        {label}
      </div>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        style={{
          width: "100%",
          padding: "10px 12px",
          borderRadius: 10,
          border: "1px solid #cbd5e1",
          background: "#ffffff",
          boxSizing: "border-box"
        }}
      >
        {options.map((opt) => (
          <option key={String(opt.value)} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function DataTable({ columns, rows, emptyText }) {
  return (
    <div
      style={{
        overflowX: "auto",
        border: "1px solid #e5e7eb",
        borderRadius: 12
      }}
    >
      <table
        style={{
          width: "100%",
          borderCollapse: "collapse",
          minWidth: 900,
          background: "#ffffff"
        }}
      >
        <thead>
          <tr style={{ background: "#f8fafc" }}>
            {columns.map((col) => (
              <th
                key={col.key}
                style={{
                  textAlign: "left",
                  padding: "12px 14px",
                  borderBottom: "1px solid #e5e7eb",
                  fontSize: 13,
                  color: "#374151"
                }}
              >
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td
                colSpan={columns.length}
                style={{
                  padding: 20,
                  textAlign: "center",
                  color: "#6b7280"
                }}
              >
                {emptyText}
              </td>
            </tr>
          ) : (
            rows.map((row, idx) => (
              <tr
                key={row.id ?? idx}
                style={{
                  borderBottom: idx === rows.length - 1 ? "none" : "1px solid #f1f5f9"
                }}
              >
                {columns.map((col) => (
                  <td
                    key={col.key}
                    style={{
                      padding: "12px 14px",
                      verticalAlign: "top",
                      fontSize: 14,
                      color: "#111827"
                    }}
                  >
                    {col.render ? col.render(row) : row[col.key] ?? "—"}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

function PaginationControls({
  page,
  setPage,
  totalItems,
  pageSize = PAGE_SIZE
}) {
  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));
  const start = totalItems === 0 ? 0 : (page - 1) * pageSize + 1;
  const end = Math.min(page * pageSize, totalItems);

  return (
    <div
      style={{
        marginTop: 12,
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        gap: 12,
        flexWrap: "wrap"
      }}
    >
      <div style={{ fontSize: 13, color: "#6b7280" }}>
        Showing {start}-{end} of {totalItems}
      </div>

      <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
        <ToolbarButton
          onClick={() => setPage((p) => Math.max(1, p - 1))}
          disabled={page <= 1}
        >
          Previous
        </ToolbarButton>
        <div style={{ fontWeight: 600, color: "#374151" }}>
          Page {page} / {totalPages}
        </div>
        <ToolbarButton
          onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
          disabled={page >= totalPages}
        >
          Next
        </ToolbarButton>
      </div>
    </div>
  );
}

function formatDateTimeLocal(iso) {
  if (!iso) return "";
  const date = new Date(iso);
  if (Number.isNaN(date.getTime())) return "";
  const pad = (n) => String(n).padStart(2, "0");
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(
    date.getDate()
  )}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
}

function toIsoOrNull(value) {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toISOString();
}

function formatShortDate(value) {
  if (!value) return "—";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return value;
  return d.toLocaleString();
}

function slicePage(items, page, pageSize = PAGE_SIZE) {
  const start = (page - 1) * pageSize;
  return items.slice(start, start + pageSize);
}

export default function DataManagerUI() {
  const [tab, setTab] = useState("gulls");
  const [message, setMessage] = useState({ type: "success", text: "" });

  const [gulls, setGulls] = useState([]);
  const [trackpoints, setTrackpoints] = useState([]);
  const [weather, setWeather] = useState([]);

  const [loading, setLoading] = useState({
    gulls: false,
    trackpoints: false,
    weather: false
  });

  const [loadedTabs, setLoadedTabs] = useState({
    gulls: false,
    trackpoints: false,
    weather: false
  });

  const [gullForm, setGullForm] = useState({
    id: "",
    tag_id: "",
    species: "",
    common_name: "",
    study_name: ""
  });

  const [trackpointForm, setTrackpointForm] = useState({
    id: "",
    gull_id: "",
    recorded_at: "",
    latitude: "",
    longitude: "",
    event_id: "",
    sensor_type: "",
    visible: ""
  });

  const [weatherForm, setWeatherForm] = useState({
    id: "",
    observed_at: "",
    latitude: "",
    longitude: "",
    year: "",
    temperature_c: "",
    precipitation_mm: "",
    wind_u: "",
    wind_v: "",
    surface_pressure: "",
    source: "",
    dataset_name: ""
  });

  const [trackpointFilterGullId, setTrackpointFilterGullId] = useState("");
  const [appliedTrackpointFilterGullId, setAppliedTrackpointFilterGullId] =
    useState("");
  const [gullSearch, setGullSearch] = useState("");
  const [weatherSearch, setWeatherSearch] = useState("");

  const [gullPage, setGullPage] = useState(1);
  const [trackpointPage, setTrackpointPage] = useState(1);
  const [weatherPage, setWeatherPage] = useState(1);

  function showSuccess(text) {
    setMessage({ type: "success", text });
  }

  function handleError(error) {
    setMessage({
      type: "error",
      text: error?.message || "Something went wrong."
    });
  }

  function resetGullForm() {
    setGullForm({
      id: "",
      tag_id: "",
      species: "",
      common_name: "",
      study_name: ""
    });
  }

  function resetTrackpointForm() {
    setTrackpointForm({
      id: "",
      gull_id: "",
      recorded_at: "",
      latitude: "",
      longitude: "",
      event_id: "",
      sensor_type: "",
      visible: ""
    });
  }

  function resetWeatherForm() {
    setWeatherForm({
      id: "",
      observed_at: "",
      latitude: "",
      longitude: "",
      year: "",
      temperature_c: "",
      precipitation_mm: "",
      wind_u: "",
      wind_v: "",
      surface_pressure: "",
      source: "",
      dataset_name: ""
    });
  }

  async function loadGulls() {
    setLoading((prev) => ({ ...prev, gulls: true }));
    try {
      const data = await fetchJson("/api/v1/gulls/");
      setGulls(Array.isArray(data) ? data : []);
      setLoadedTabs((prev) => ({ ...prev, gulls: true }));
    } catch (error) {
      handleError(error);
    } finally {
      setLoading((prev) => ({ ...prev, gulls: false }));
    }
  }

  async function loadTrackpoints(gullId = "") {
    setLoading((prev) => ({ ...prev, trackpoints: true }));
    try {
      const path = gullId
        ? `/api/v1/trackpoints?gull_id=${encodeURIComponent(gullId)}`
        : "/api/v1/trackpoints";
      const data = await fetchJson(path);
      setTrackpoints(Array.isArray(data) ? data : []);
      setLoadedTabs((prev) => ({ ...prev, trackpoints: true }));
    } catch (error) {
      handleError(error);
    } finally {
      setLoading((prev) => ({ ...prev, trackpoints: false }));
    }
  }

  async function loadWeather() {
    setLoading((prev) => ({ ...prev, weather: true }));
    try {
      const data = await fetchJson("/api/v1/weather");
      setWeather(Array.isArray(data) ? data : []);
      setLoadedTabs((prev) => ({ ...prev, weather: true }));
    } catch (error) {
      handleError(error);
    } finally {
      setLoading((prev) => ({ ...prev, weather: false }));
    }
  }

  useEffect(() => {
    if (tab === "gulls" && !loadedTabs.gulls) {
      loadGulls();
    }

    if (tab === "trackpoints") {
      if (!loadedTabs.gulls) {
        loadGulls();
      }
      if (!loadedTabs.trackpoints) {
        loadTrackpoints(appliedTrackpointFilterGullId);
      }
    }

    if (tab === "weather" && !loadedTabs.weather) {
      loadWeather();
    }
  }, [tab, loadedTabs.gulls, loadedTabs.trackpoints, loadedTabs.weather]);

  useEffect(() => {
    setGullPage(1);
  }, [gullSearch]);

  useEffect(() => {
    setTrackpointPage(1);
  }, [trackpoints]);

  useEffect(() => {
    setWeatherPage(1);
  }, [weatherSearch, weather]);

  const filteredGulls = useMemo(() => {
    const q = gullSearch.trim().toLowerCase();
    if (!q) return gulls;

    return gulls.filter((g) =>
      [g.id, g.tag_id, g.species, g.common_name, g.study_name]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(q)
    );
  }, [gulls, gullSearch]);

  const filteredWeather = useMemo(() => {
    const q = weatherSearch.trim().toLowerCase();
    if (!q) return weather;

    return weather.filter((w) =>
      [
        w.id,
        w.observed_at,
        w.latitude,
        w.longitude,
        w.year,
        w.temperature_c,
        w.precipitation_mm,
        w.source,
        w.dataset_name
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase()
        .includes(q)
    );
  }, [weather, weatherSearch]);

  const pagedGulls = useMemo(
    () => slicePage(filteredGulls, gullPage),
    [filteredGulls, gullPage]
  );

  const pagedTrackpoints = useMemo(
    () => slicePage(trackpoints, trackpointPage),
    [trackpoints, trackpointPage]
  );

  const pagedWeather = useMemo(
    () => slicePage(filteredWeather, weatherPage),
    [filteredWeather, weatherPage]
  );

  async function submitGull(e) {
    e.preventDefault();

    try {
      const payload = {
        tag_id: gullForm.tag_id,
        species: gullForm.species,
        common_name: gullForm.common_name || null,
        study_name: gullForm.study_name || null
      };

      if (!payload.tag_id || !payload.species) {
        throw new Error("Tag ID and species are required.");
      }

      if (gullForm.id) {
        const updated = await fetchJson(`/api/v1/gulls/${gullForm.id}`, {
          method: "PUT",
          body: JSON.stringify(payload)
        });

        setGulls((prev) =>
          prev.map((item) =>
            String(item.id) === String(gullForm.id) ? updated : item
          )
        );
        showSuccess("Gull updated.");
      } else {
        const created = await fetchJson("/api/v1/gulls/", {
          method: "POST",
          body: JSON.stringify(payload)
        });

        setGulls((prev) => [created, ...prev]);
        showSuccess("Gull created.");
      }

      resetGullForm();
      setLoadedTabs((prev) => ({ ...prev, gulls: true }));
      setGullPage(1);
    } catch (error) {
      handleError(error);
    }
  }

  async function submitTrackpoint(e) {
    e.preventDefault();

    try {
      const lat = Number(trackpointForm.latitude);
      const lng = Number(trackpointForm.longitude);

      if (!trackpointForm.gull_id) {
        throw new Error("Gull ID is required.");
      }
      if (!trackpointForm.recorded_at) {
        throw new Error("Recorded at is required.");
      }
      if (Number.isNaN(lat) || lat < -90 || lat > 90) {
        throw new Error("Latitude must be between -90 and 90.");
      }
      if (Number.isNaN(lng) || lng < -180 || lng > 180) {
        throw new Error("Longitude must be between -180 and 180.");
      }

      const payload = {
        gull_id: Number(trackpointForm.gull_id),
        recorded_at: toIsoOrNull(trackpointForm.recorded_at),
        latitude: lat,
        longitude: lng,
        event_id: trackpointForm.event_id || null,
        sensor_type: trackpointForm.sensor_type || null,
        visible: trackpointForm.visible || null
      };

      if (!payload.recorded_at) {
        throw new Error("Recorded at is not a valid date/time.");
      }

      if (trackpointForm.id) {
        const updated = await fetchJson(`/api/v1/trackpoints/${trackpointForm.id}`, {
          method: "PUT",
          body: JSON.stringify(payload)
        });

        setTrackpoints((prev) =>
          prev.map((item) =>
            String(item.id) === String(trackpointForm.id) ? updated : item
          )
        );
        showSuccess("Trackpoint updated.");
      } else {
        const created = await fetchJson("/api/v1/trackpoints", {
          method: "POST",
          body: JSON.stringify(payload)
        });

        const shouldShow =
          !appliedTrackpointFilterGullId ||
          String(created.gull_id) === String(appliedTrackpointFilterGullId);

        if (shouldShow) {
          setTrackpoints((prev) => [created, ...prev]);
        }

        showSuccess("Trackpoint created.");
      }

      resetTrackpointForm();
      setLoadedTabs((prev) => ({ ...prev, trackpoints: true }));
      setTrackpointPage(1);
    } catch (error) {
      handleError(error);
    }
  }
  async function submitWeather(e) {
    e.preventDefault();
  
    try {
      const observedAtIso = toIsoOrNull(weatherForm.observed_at);
  
      if (!observedAtIso) {
        throw new Error("Observed at is required and must be valid.");
      }
  
      const lat = Number(weatherForm.latitude);
      const lng = Number(weatherForm.longitude);
  
      if (Number.isNaN(lat) || lat < -90 || lat > 90) {
        throw new Error("Latitude must be between -90 and 90.");
      }
  
      if (Number.isNaN(lng) || lng < -180 || lng > 180) {
        throw new Error("Longitude must be between -180 and 180.");
      }
  
      const derivedYear = new Date(observedAtIso).getUTCFullYear();
  
      const payload = {
        observed_at: observedAtIso,
        latitude: lat,
        longitude: lng,
        year: weatherForm.year === "" ? derivedYear : Number(weatherForm.year),
        temperature_c:
          weatherForm.temperature_c === "" ? null : Number(weatherForm.temperature_c),
        precipitation_mm:
          weatherForm.precipitation_mm === ""
            ? null
            : Number(weatherForm.precipitation_mm),
        wind_u: weatherForm.wind_u === "" ? null : Number(weatherForm.wind_u),
        wind_v: weatherForm.wind_v === "" ? null : Number(weatherForm.wind_v),
        surface_pressure:
          weatherForm.surface_pressure === ""
            ? null
            : Number(weatherForm.surface_pressure),
        source: weatherForm.source?.trim() || null,
        dataset_name: weatherForm.dataset_name?.trim() || null
      };
  
      if (Number.isNaN(payload.year)) {
        throw new Error("Year must be a valid number.");
      }
  
      if (weatherForm.id) {
        const updated = await fetchJson(`/api/v1/weather/${weatherForm.id}`, {
          method: "PUT",
          body: JSON.stringify(payload)
        });
  
        setWeather((prev) =>
          prev.map((item) =>
            String(item.id) === String(weatherForm.id) ? updated : item
          )
        );
        showSuccess("Weather row updated.");
      } else {
        const created = await fetchJson("/api/v1/weather", {
          method: "POST",
          body: JSON.stringify(payload)
        });
  
        setWeather((prev) => [created, ...prev]);
        showSuccess("Weather row created.");
      }
  
      resetWeatherForm();
      setLoadedTabs((prev) => ({ ...prev, weather: true }));
      setWeatherPage(1);
    } catch (error) {
      handleError(error);
    }
  }
  
  async function deleteGull(id) {
    if (!window.confirm(`Delete gull ${id}? This may affect linked trackpoints.`)) {
      return;
    }

    const previous = gulls;
    setGulls((prev) => prev.filter((item) => String(item.id) !== String(id)));

    try {
      await fetchJson(`/api/v1/gulls/${id}`, { method: "DELETE" });
      showSuccess("Gull deleted.");

      if (String(gullForm.id) === String(id)) {
        resetGullForm();
      }
    } catch (error) {
      setGulls(previous);
      handleError(error);
    }
  }
  async function deleteWeather(id) {
    if (!window.confirm(`Delete weather row ${id}?`)) {
      return;
    }
  
    const previous = weather;
    setWeather((prev) =>
      prev.filter((item) => String(item.id) !== String(id))
    );
  
    try {
      await fetchJson(`/api/v1/weather/${id}`, { method: "DELETE" });
      showSuccess("Weather row deleted.");
  
      if (String(weatherForm.id) === String(id)) {
        resetWeatherForm();
      }
    } catch (error) {
      setWeather(previous);
      handleError(error);
    }
  }

  async function deleteTrackpoint(id) {
    if (!window.confirm(`Delete trackpoint ${id}?`)) {
      return;
    }

    const previous = trackpoints;
    setTrackpoints((prev) =>
      prev.filter((item) => String(item.id) !== String(id))
    );

    try {
      await fetchJson(`/api/v1/trackpoints/${id}`, { method: "DELETE" });
      showSuccess("Trackpoint deleted.");

      if (String(trackpointForm.id) === String(id)) {
        resetTrackpointForm();
      }
    } catch (error) {
      setTrackpoints(previous);
      handleError(error);
    }
  }

  
  async function applyTrackpointFilter() {
    setAppliedTrackpointFilterGullId(trackpointFilterGullId);
    setTrackpointPage(1);
    await loadTrackpoints(trackpointFilterGullId);
  }

  function tabButtonStyle(active) {
    return {
      padding: "10px 14px",
      borderRadius: 10,
      border: active ? "1px solid #2563eb" : "1px solid #cbd5e1",
      background: active ? "#2563eb" : "#ffffff",
      color: active ? "#ffffff" : "#111827",
      fontWeight: 700,
      cursor: "pointer"
    };
  }

  const gullColumns = [
    { key: "id", label: "ID" },
    { key: "tag_id", label: "Tag ID" },
    { key: "species", label: "Species" },
    { key: "common_name", label: "Common Name" },
    { key: "study_name", label: "Study Name" },
    {
      key: "actions",
      label: "Actions",
      render: (row) => (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <ToolbarButton
            onClick={() =>
              setGullForm({
                id: row.id ?? "",
                tag_id: row.tag_id ?? "",
                species: row.species ?? "",
                common_name: row.common_name ?? "",
                study_name: row.study_name ?? ""
              })
            }
          >
            Edit
          </ToolbarButton>
          <ToolbarButton danger onClick={() => deleteGull(row.id)}>
            Delete
          </ToolbarButton>
        </div>
      )
    }
  ];

  const trackpointColumns = [
    { key: "id", label: "ID" },
    { key: "gull_id", label: "Gull ID" },
    {
      key: "recorded_at",
      label: "Recorded At",
      render: (row) => formatShortDate(row.recorded_at)
    },
    {
      key: "latitude",
      label: "Latitude",
      render: (row) => row.latitude?.toFixed?.(5) ?? row.latitude ?? "—"
    },
    {
      key: "longitude",
      label: "Longitude",
      render: (row) => row.longitude?.toFixed?.(5) ?? row.longitude ?? "—"
    },
    { key: "event_id", label: "Event ID" },
    { key: "sensor_type", label: "Sensor Type" },
    { key: "visible", label: "Visible" },
    {
      key: "actions",
      label: "Actions",
      render: (row) => (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <ToolbarButton
            onClick={() =>
              setTrackpointForm({
                id: row.id ?? "",
                gull_id: row.gull_id ?? "",
                recorded_at: formatDateTimeLocal(row.recorded_at),
                latitude: row.latitude ?? "",
                longitude: row.longitude ?? "",
                event_id: row.event_id ?? "",
                sensor_type: row.sensor_type ?? "",
                visible: row.visible ?? ""
              })
            }
          >
            Edit
          </ToolbarButton>
          <ToolbarButton danger onClick={() => deleteTrackpoint(row.id)}>
            Delete
          </ToolbarButton>
        </div>
      )
    }
  ];

  const weatherColumns = [
    { key: "id", label: "ID" },
    {
      key: "observed_at",
      label: "Observed At",
      render: (row) => formatShortDate(row.observed_at)
    },
    {
      key: "latitude",
      label: "Latitude",
      render: (row) => row.latitude?.toFixed?.(4) ?? row.latitude ?? "—"
    },
    {
      key: "longitude",
      label: "Longitude",
      render: (row) => row.longitude?.toFixed?.(4) ?? row.longitude ?? "—"
    },
    { key: "year", label: "Year" },
    { key: "temperature_c", label: "Temp °C" },
    { key: "precipitation_mm", label: "Precip mm" },
    { key: "wind_u", label: "Wind U" },
    { key: "wind_v", label: "Wind V" },
    { key: "surface_pressure", label: "Pressure" },
    { key: "source", label: "Source" },
    { key: "dataset_name", label: "Dataset" },
    {
      key: "actions",
      label: "Actions",
      render: (row) => (
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          <ToolbarButton
            onClick={() =>
              setWeatherForm({
                id: row.id ?? "",
                observed_at: formatDateTimeLocal(row.observed_at),
                latitude: row.latitude ?? "",
                longitude: row.longitude ?? "",
                year: row.year ?? "",
                temperature_c: row.temperature_c ?? "",
                precipitation_mm: row.precipitation_mm ?? "",
                wind_u: row.wind_u ?? "",
                wind_v: row.wind_v ?? "",
                surface_pressure: row.surface_pressure ?? "",
                source: row.source ?? "",
                dataset_name: row.dataset_name ?? ""
              })
            }
          >
            Edit
          </ToolbarButton>
          <ToolbarButton danger onClick={() => deleteWeather(row.id)}>
            Delete
          </ToolbarButton>
        </div>
      )
    }
  ];

  return (
    <div
      style={{
        padding: 20,
        background: "#f8fafc",
        minHeight: "100vh",
        fontFamily: "Arial, sans-serif"
      }}
    >
      <h2 style={{ marginBottom: 8 }}>Gull Data Manager</h2>
      <div style={{ color: "#4b5563", marginBottom: 18 }}>
        Create, update, and remove gulls, trackpoints, and weather records.
      </div>

      <StatusBanner
        type={message.type}
        text={message.text}
        onClose={() => setMessage((prev) => ({ ...prev, text: "" }))}
      />

      <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 18 }}>
        <button type="button" onClick={() => setTab("gulls")} style={tabButtonStyle(tab === "gulls")}>
          Gulls
        </button>
        <button
          type="button"
          onClick={() => setTab("trackpoints")}
          style={tabButtonStyle(tab === "trackpoints")}
        >
          Trackpoints
        </button>
        <button
          type="button"
          onClick={() => setTab("weather")}
          style={tabButtonStyle(tab === "weather")}
        >
          Weather
        </button>
      </div>

      {tab === "gulls" && (
        <div style={{ display: "grid", gridTemplateColumns: "1.1fr 1.8fr", gap: 18 }}>
          <SectionCard
            title={gullForm.id ? "Edit Gull" : "Create Gull"}
            subtitle="Manage species-level and study metadata."
          >
            <form onSubmit={submitGull}>
              <div style={{ display: "grid", gap: 14 }}>
                <TextInput
                  label="Tag ID"
                  value={gullForm.tag_id}
                  onChange={(v) => setGullForm((p) => ({ ...p, tag_id: v }))}
                  required
                />
                <TextInput
                  label="Species"
                  value={gullForm.species}
                  onChange={(v) => setGullForm((p) => ({ ...p, species: v }))}
                  required
                />
                <TextInput
                  label="Common Name"
                  value={gullForm.common_name}
                  onChange={(v) => setGullForm((p) => ({ ...p, common_name: v }))}
                />
                <TextInput
                  label="Study Name"
                  value={gullForm.study_name}
                  onChange={(v) => setGullForm((p) => ({ ...p, study_name: v }))}
                />

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  <ToolbarButton primary type="submit">
                    {gullForm.id ? "Update Gull" : "Create Gull"}
                  </ToolbarButton>
                  <ToolbarButton onClick={resetGullForm}>Clear</ToolbarButton>
                  <ToolbarButton onClick={loadGulls} disabled={loading.gulls}>
                    {loading.gulls ? "Refreshing..." : "Refresh"}
                  </ToolbarButton>
                </div>
              </div>
            </form>
          </SectionCard>

          <SectionCard
            title="Gull Records"
            subtitle="Search and edit registered gulls."
            rightContent={
              <div style={{ minWidth: 260 }}>
                <TextInput
                  label="Search"
                  value={gullSearch}
                  onChange={setGullSearch}
                  placeholder="Search by tag, species, study..."
                />
              </div>
            }
          >
            <DataTable
              columns={gullColumns}
              rows={pagedGulls}
              emptyText={loading.gulls ? "Loading gulls..." : "No gull records found."}
            />
            <PaginationControls
              page={gullPage}
              setPage={setGullPage}
              totalItems={filteredGulls.length}
            />
          </SectionCard>
        </div>
      )}

      {tab === "trackpoints" && (
        <div style={{ display: "grid", gridTemplateColumns: "1.15fr 1.85fr", gap: 18 }}>
          <SectionCard
            title={trackpointForm.id ? "Edit Trackpoint" : "Create Trackpoint"}
            subtitle="Add location/time observations for a gull."
          >
            <form onSubmit={submitTrackpoint}>
              <div style={{ display: "grid", gap: 14 }}>
                <SelectInput
                  label="Gull"
                  value={trackpointForm.gull_id}
                  onChange={(v) => setTrackpointForm((p) => ({ ...p, gull_id: v }))}
                  options={[
                    { value: "", label: "Select gull..." },
                    ...gulls.map((g) => ({
                      value: String(g.id),
                      label: `${g.id} | ${g.tag_id} | ${g.species}`
                    }))
                  ]}
                />

                <TextInput
                  label="Recorded At"
                  type="datetime-local"
                  value={trackpointForm.recorded_at}
                  onChange={(v) => setTrackpointForm((p) => ({ ...p, recorded_at: v }))}
                  required
                />

                <TextInput
                  label="Latitude"
                  type="number"
                  step="any"
                  min="-90"
                  max="90"
                  value={trackpointForm.latitude}
                  onChange={(v) => setTrackpointForm((p) => ({ ...p, latitude: v }))}
                  required
                />

                <TextInput
                  label="Longitude"
                  type="number"
                  step="any"
                  min="-180"
                  max="180"
                  value={trackpointForm.longitude}
                  onChange={(v) => setTrackpointForm((p) => ({ ...p, longitude: v }))}
                  required
                />

                <TextInput
                  label="Event ID"
                  value={trackpointForm.event_id}
                  onChange={(v) => setTrackpointForm((p) => ({ ...p, event_id: v }))}
                />

                <TextInput
                  label="Sensor Type"
                  value={trackpointForm.sensor_type}
                  onChange={(v) => setTrackpointForm((p) => ({ ...p, sensor_type: v }))}
                />

                <TextInput
                  label="Visible"
                  value={trackpointForm.visible}
                  onChange={(v) => setTrackpointForm((p) => ({ ...p, visible: v }))}
                />

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  <ToolbarButton primary type="submit">
                    {trackpointForm.id ? "Update Trackpoint" : "Create Trackpoint"}
                  </ToolbarButton>
                  <ToolbarButton onClick={resetTrackpointForm}>Clear</ToolbarButton>
                  <ToolbarButton
                    onClick={() => loadTrackpoints(appliedTrackpointFilterGullId)}
                    disabled={loading.trackpoints}
                  >
                    {loading.trackpoints ? "Refreshing..." : "Refresh"}
                  </ToolbarButton>
                </div>
              </div>
            </form>
          </SectionCard>

          <SectionCard
            title="Trackpoint Records"
            subtitle="Filter by gull and manage recorded movement points."
            rightContent={
              <div
                style={{
                  display: "flex",
                  gap: 10,
                  flexWrap: "wrap",
                  alignItems: "end"
                }}
              >
                <div style={{ minWidth: 260 }}>
                  <SelectInput
                    label="Filter by Gull"
                    value={trackpointFilterGullId}
                    onChange={setTrackpointFilterGullId}
                    options={[
                      { value: "", label: "All gulls" },
                      ...gulls.map((g) => ({
                        value: String(g.id),
                        label: `${g.id} | ${g.tag_id} | ${g.species}`
                      }))
                    ]}
                  />
                </div>
                <ToolbarButton
                  onClick={applyTrackpointFilter}
                  disabled={loading.trackpoints}
                >
                  {loading.trackpoints ? "Applying..." : "Apply Filter"}
                </ToolbarButton>
              </div>
            }
          >
            <DataTable
              columns={trackpointColumns}
              rows={pagedTrackpoints}
              emptyText={
                loading.trackpoints ? "Loading trackpoints..." : "No trackpoints found."
              }
            />
            <PaginationControls
              page={trackpointPage}
              setPage={setTrackpointPage}
              totalItems={trackpoints.length}
            />
          </SectionCard>
        </div>
      )}

      {tab === "weather" && (
        <div style={{ display: "grid", gridTemplateColumns: "1.15fr 1.85fr", gap: 18 }}>
          <SectionCard
            title={weatherForm.id ? "Edit Weather Record" : "Create Weather Record"}
            subtitle="Manage weather observations linked to migration analysis."
          >
            <form onSubmit={submitWeather}>
              <div style={{ display: "grid", gap: 14 }}>
                <TextInput
                  label="Observed At"
                  type="datetime-local"
                  value={weatherForm.observed_at}
                  onChange={(v) => setWeatherForm((p) => ({ ...p, observed_at: v }))}
                  required
                />

                <TextInput
                  label="Latitude"
                  type="number"
                  step="any"
                  min="-90"
                  max="90"
                  value={weatherForm.latitude}
                  onChange={(v) => setWeatherForm((p) => ({ ...p, latitude: v }))}
                  required
                />

                <TextInput
                  label="Longitude"
                  type="number"
                  step="any"
                  min="-180"
                  max="180"
                  value={weatherForm.longitude}
                  onChange={(v) => setWeatherForm((p) => ({ ...p, longitude: v }))}
                  required
                />

                <TextInput
                  label="Year"
                  type="number"
                  value={weatherForm.year}
                  onChange={(v) => setWeatherForm((p) => ({ ...p, year: v }))}
                />

                <TextInput
                  label="Temperature °C"
                  type="number"
                  step="any"
                  value={weatherForm.temperature_c}
                  onChange={(v) => setWeatherForm((p) => ({ ...p, temperature_c: v }))}
                />

                <TextInput
                  label="Precipitation mm"
                  type="number"
                  step="any"
                  value={weatherForm.precipitation_mm}
                  onChange={(v) => setWeatherForm((p) => ({ ...p, precipitation_mm: v }))}
                />

                <TextInput
                  label="Wind U"
                  type="number"
                  step="any"
                  value={weatherForm.wind_u}
                  onChange={(v) => setWeatherForm((p) => ({ ...p, wind_u: v }))}
                />

                <TextInput
                  label="Wind V"
                  type="number"
                  step="any"
                  value={weatherForm.wind_v}
                  onChange={(v) => setWeatherForm((p) => ({ ...p, wind_v: v }))}
                />

                <TextInput
                  label="Surface Pressure"
                  type="number"
                  step="any"
                  value={weatherForm.surface_pressure}
                  onChange={(v) =>
                    setWeatherForm((p) => ({ ...p, surface_pressure: v }))
                  }
                />

                <TextInput
                  label="Source"
                  value={weatherForm.source}
                  onChange={(v) => setWeatherForm((p) => ({ ...p, source: v }))}
                />

                <TextInput
                  label="Dataset Name"
                  value={weatherForm.dataset_name}
                  onChange={(v) =>
                    setWeatherForm((p) => ({ ...p, dataset_name: v }))
                  }
                />

                <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
                  <ToolbarButton primary type="submit">
                    {weatherForm.id ? "Update Weather" : "Create Weather"}
                  </ToolbarButton>
                  <ToolbarButton onClick={resetWeatherForm}>Clear</ToolbarButton>
                  <ToolbarButton onClick={loadWeather} disabled={loading.weather}>
                    {loading.weather ? "Refreshing..." : "Refresh"}
                  </ToolbarButton>
                </div>
              </div>
            </form>
          </SectionCard>

          <SectionCard
            title="Weather Records"
            subtitle="Search and manage stored observations."
            rightContent={
              <div style={{ minWidth: 260 }}>
                <TextInput
                  label="Search"
                  value={weatherSearch}
                  onChange={setWeatherSearch}
                  placeholder="Search by id, date, temp, coords..."
                />
              </div>
            }
          >
            <DataTable
              columns={weatherColumns}
              rows={pagedWeather}
              emptyText={loading.weather ? "Loading weather..." : "No weather rows found."}
            />
            <PaginationControls
              page={weatherPage}
              setPage={setWeatherPage}
              totalItems={filteredWeather.length}
            />
          </SectionCard>
        </div>
      )}
    </div>
  );
}
