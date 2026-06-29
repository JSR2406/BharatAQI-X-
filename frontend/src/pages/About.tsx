import { Info, Satellite, Zap } from "lucide-react";

export default function About() {
  return (
    <div className="animate-fadeIn" style={{ maxWidth: 800 }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontSize: 24, fontWeight: 700, display: "flex", alignItems: "center", gap: 10 }}>
          <Info size={22} color="#3b82f6" /> About BharatAQI-X
        </h1>
        <p style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 6, lineHeight: 1.8 }}>
          An Explainable Satellite-to-Surface Air Quality Digital Twin for India
          built for <strong style={{ color: "var(--accent-blue)" }}>Bharatiya Antariksh Hackathon 2026</strong>.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 20 }}>
        {[
          { icon: Satellite, title: "Data Sources", color: "#3b82f6", items: ["Sentinel-5P (ESA/ISRO)","OpenAQ / CPCB Ground Stations","NASA FIRMS Fire Data","ERA5 Reanalysis Weather"] },
          { icon: Zap, title: "ML Pipeline", color: "#8b5cf6", items: ["XGBoost + LightGBM Ensemble","SHAP Explainability","DBSCAN Hotspot Clustering","Isolation Forest Anomaly Detection"] },
        ].map(({ icon: Icon, title, color, items }) => (
          <div key={title} className="glass-card" style={{ padding: 20 }}>
            <h3 style={{ fontSize: 13, fontWeight: 600, display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
              <Icon size={15} color={color} /> {title}
            </h3>
            {items.map(item => (
              <div key={item} style={{ fontSize: 12, color: "var(--text-muted)", padding: "5px 0", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ width: 6, height: 6, borderRadius: "50%", background: color, flexShrink: 0 }} />
                {item}
              </div>
            ))}
          </div>
        ))}
      </div>

      <div className="glass-card" style={{ padding: 20, marginBottom: 16 }}>
        <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 14 }}>Problem Statement</h3>
        <p style={{ fontSize: 13, color: "var(--text-muted)", lineHeight: 1.8 }}>
          Development of Surface AQI & Identification of HCHO Hotspots over India using Satellite Data.
          This project addresses India's critical air quality crisis by combining satellite atmospheric data
          (Sentinel-5P), ground observations (CPCB/OpenAQ), fire data (NASA FIRMS), and weather data (ERA5)
          to build a production-grade, explainable AI platform for AQI prediction and HCHO hotspot detection.
        </p>
      </div>

      <div className="glass-card" style={{ padding: 20 }}>
        <h3 style={{ fontSize: 13, fontWeight: 600, marginBottom: 14 }}>API Endpoints</h3>
        {[
          { method: "GET",  path: "/predict",   desc: "Predict surface AQI from pollutant inputs" },
          { method: "GET",  path: "/forecast",  desc: "7–30 day AQI forecast for a city" },
          { method: "GET",  path: "/hotspots",  desc: "HCHO hotspot clusters (DBSCAN/ISO)" },
          { method: "GET",  path: "/explain",   desc: "SHAP global/local feature importance" },
          { method: "POST", path: "/analyze",   desc: "AI agent environmental analysis" },
          { method: "GET",  path: "/map-data",  desc: "Geospatial data for dashboard maps" },
        ].map(({ method, path, desc }) => (
          <div key={path} style={{ display: "flex", alignItems: "center", gap: 12, padding: "8px 0", borderBottom: "1px solid var(--border)" }}>
            <span style={{ fontSize: 10, fontWeight: 700, padding: "2px 8px", borderRadius: 4, background: method === "POST" ? "rgba(139,92,246,0.2)" : "rgba(59,130,246,0.15)", color: method === "POST" ? "#8b5cf6" : "#3b82f6", minWidth: 38, textAlign: "center" }}>{method}</span>
            <code style={{ fontSize: 12, color: "#10b981" }}>{path}</code>
            <span style={{ fontSize: 12, color: "var(--text-muted)" }}>{desc}</span>
          </div>
        ))}
        <div style={{ marginTop: 12, fontSize: 12, color: "var(--text-muted)" }}>
          Full docs: <a href="http://localhost:8000/docs" target="_blank" style={{ color: "var(--accent-blue)" }}>http://localhost:8000/docs</a>
        </div>
      </div>
    </div>
  );
}
