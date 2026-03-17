import { useState } from "react";
import GullMapUI from "./GullMapUI";
import DataManagerUI from "./DataManagerUI";

export default function App() {
  const [page, setPage] = useState("analytics");

  const navButtonStyle = (active) => ({
    padding: "10px 16px",
    borderRadius: 10,
    border: active ? "1px solid #2563eb" : "1px solid #cbd5e1",
    background: active ? "#2563eb" : "#ffffff",
    color: active ? "#ffffff" : "#111827",
    fontWeight: 600,
    cursor: "pointer"
  });

  return (
    <div style={{ minHeight: "100vh", background: "#f8fafc" }}>
      <div
        style={{
          position: "sticky",
          top: 0,
          zIndex: 2000,
          background: "#ffffff",
          borderBottom: "1px solid #e5e7eb",
          padding: "14px 20px",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          gap: 12,
          flexWrap: "wrap"
        }}
      >
        <div>
          <div style={{ fontSize: 20, fontWeight: 800, color: "#111827" }}>
            Gull Tracker API Frontend
          </div>
          <div style={{ fontSize: 13, color: "#6b7280", marginTop: 4 }}>
            Analytics dashboard + CRUD data manager
          </div>
        </div>

        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button
            type="button"
            onClick={() => setPage("analytics")}
            style={navButtonStyle(page === "analytics")}
          >
            Analytics Dashboard
          </button>
          <button
            type="button"
            onClick={() => setPage("manager")}
            style={navButtonStyle(page === "manager")}
          >
            Data Manager
          </button>
        </div>
      </div>

      {page === "analytics" ? <GullMapUI /> : <DataManagerUI />}
    </div>
  );
}