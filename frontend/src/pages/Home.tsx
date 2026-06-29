import { Satellite, Wind, Flame, AlertTriangle, TrendingDown, Activity } from "lucide-react";
import { aqiColor, aqiCategory, INDIA_CITIES_MOCK } from "../lib/api";

const STATS = [
  { label: "Cities Monitored", value: "30+",   icon: Activity,     color: "#3b82f6" },
  { label: "Avg National AQI",  value: "162",   icon: AlertTriangle, color: "#f59e0b" },
  { label: "HCHO Hotspots",     value: "47",    icon: Wind,          color: "#8b5cf6" },
  { label: "Active Fires",      value: "1,204", icon: Flame,         color: "#ef4444" },
];

export default function Home() {
  const worst = [...INDIA_CITIES_MOCK].sort((a, b) => b.aqi - a.aqi).slice(0, 5);
  const best  = [...INDIA_CITIES_MOCK].sort((a, b) => a.aqi - b.aqi).slice(0, 5);

  return (
    <div className="animate-fadeIn">
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
          <div style={{ width: 42, height: 42, borderRadius: 12, background: "linear-gradient(135deg,#3b82f6,#8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <Satellite size={22} color="#fff" />
          </div>
          <div>
            <h1 style={{ fontSize: 26, fontWeight: 700 }} className="gradient-text">BharatAQI-X</h1>
            <p style={{ fontSize: 12, color: "var(--text-muted)" }}>Bharatiya Antariksh Hackathon 2026 · ISRO</p>
          </div>
        </div>
        <p style={{ color: "var(--text-muted)", fontSize: 14, maxWidth: 600 }}>
          Explainable Satellite-to-Surface Air Quality Digital Twin for India.
          Powered by Sentinel-5P, XGBoost/LightGBM, SHAP, and Agentic AI.
        </p>
      </div>

      {/* Stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 16, marginBottom: 28 }}>
        {STATS.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="stat-card" style={{ padding: 20 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
              <span style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 500 }}>{label}</span>
              <div style={{ width: 32, height: 32, borderRadius: 8, background: `${color}20`, display: "flex", alignItems: "center", justifyContent: "center" }}>
                <Icon size={16} color={color} />
              </div>
            </div>
            <div style={{ fontSize: 28, fontWeight: 700, color }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Two column */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>
        {/* Worst cities */}
        <div className="glass-card" style={{ padding: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
            <AlertTriangle size={15} color="#ef4444" /> Most Polluted Cities
          </h3>
          {worst.map((city, i) => (
            <div key={city.name} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 0", borderBottom: i < 4 ? "1px solid var(--border)" : "none" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontSize: 11, color: "var(--text-muted)", width: 16 }}>#{i+1}</span>
                <span style={{ fontSize: 13, fontWeight: 500 }}>{city.name}</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 12, fontWeight: 700, color: aqiColor(city.aqi) }}>{city.aqi}</span>
                <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 20, background: `${aqiColor(city.aqi)}20`, color: aqiColor(city.aqi) }}>
                  {aqiCategory(city.aqi)}
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Best cities */}
        <div className="glass-card" style={{ padding: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16, display: "flex", alignItems: "center", gap: 8 }}>
            <TrendingDown size={15} color="#10b981" /> Cleanest Cities
          </h3>
          {best.map((city, i) => (
            <div key={city.name} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "8px 0", borderBottom: i < 4 ? "1px solid var(--border)" : "none" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                <span style={{ fontSize: 11, color: "var(--text-muted)", width: 16 }}>#{i+1}</span>
                <span style={{ fontSize: 13, fontWeight: 500 }}>{city.name}</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <span style={{ fontSize: 12, fontWeight: 700, color: aqiColor(city.aqi) }}>{city.aqi}</span>
                <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 20, background: `${aqiColor(city.aqi)}20`, color: aqiColor(city.aqi) }}>
                  {aqiCategory(city.aqi)}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Technology Stack Banner */}
      <div className="glass-card" style={{ padding: 20 }}>
        <h3 style={{ fontSize: 13, fontWeight: 600, color: "var(--text-muted)", marginBottom: 14 }}>TECHNOLOGY STACK</h3>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {["Sentinel-5P","OpenAQ","NASA FIRMS","ERA5","XGBoost","LightGBM","SHAP","LangChain","Qwen3","FastAPI","React","Leaflet","DBSCAN","Isolation Forest"].map(t => (
            <span key={t} style={{ fontSize: 11, padding: "4px 12px", borderRadius: 20, background: "rgba(59,130,246,0.1)", color: "var(--accent-blue)", border: "1px solid rgba(59,130,246,0.2)", fontWeight: 500 }}>{t}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
