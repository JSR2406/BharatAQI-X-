import Plot from "react-plotly.js";
import { Brain } from "lucide-react";

const GLOBAL_FI = [
  { feature: "pm25",          mean_abs_shap: 45.2 },
  { feature: "aqi_lag1",      mean_abs_shap: 38.7 },
  { feature: "no2",           mean_abs_shap: 22.1 },
  { feature: "HCHO",          mean_abs_shap: 18.5 },
  { feature: "fire_count",    mean_abs_shap: 12.3 },
  { feature: "humidity",      mean_abs_shap: 9.8  },
  { feature: "wind_speed",    mean_abs_shap: 8.4  },
  { feature: "temperature",   mean_abs_shap: 6.7  },
  { feature: "pm25_roll7",    mean_abs_shap: 5.9  },
  { feature: "no2_wind",      mean_abs_shap: 4.2  },
  { feature: "season_enc",    mean_abs_shap: 3.8  },
  { feature: "month_sin",     mean_abs_shap: 3.1  },
];

const WATERFALL = [
  { label: "Base value",     value: 125.0, cumulative: 125.0 },
  { label: "+ pm25",         value: 48.2,  cumulative: 173.2 },
  { label: "+ aqi_lag1",     value: 35.6,  cumulative: 208.8 },
  { label: "+ no2",          value: 22.4,  cumulative: 231.2 },
  { label: "− wind_speed",   value: -18.3, cumulative: 212.9 },
  { label: "− humidity",     value: -12.1, cumulative: 200.8 },
  { label: "+ fire_count",   value: 10.5,  cumulative: 211.3 },
  { label: "Prediction",     value: 0,     cumulative: 211.3 },
];

export default function Explainability() {
  return (
    <div className="animate-fadeIn">
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, display: "flex", alignItems: "center", gap: 10 }}>
          <Brain size={22} color="#8b5cf6" /> Explainable AI — SHAP Analysis
        </h1>
        <p style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>
          SHAP (SHapley Additive exPlanations) global and local model explanations
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, marginBottom: 20 }}>
        {/* Global Feature Importance */}
        <div className="glass-card" style={{ padding: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14 }}>Global Feature Importance (Mean |SHAP|)</h3>
          <Plot
            data={[{
              type: "bar", orientation: "h",
              x: GLOBAL_FI.map(f => f.mean_abs_shap).reverse(),
              y: GLOBAL_FI.map(f => f.feature).reverse(),
              marker: { color: GLOBAL_FI.map((_, i) => `hsl(${220 + i*12}, 80%, ${65 - i*3}%)`).reverse() },
            }]}
            layout={{
              paper_bgcolor: "transparent", plot_bgcolor: "transparent",
              font: { color: "#94a3b8", family: "Inter", size: 11 },
              xaxis: { gridcolor: "#1e2d40", title: "Mean |SHAP value|" },
              yaxis: { gridcolor: "#1e2d40" },
              margin: { t: 5, b: 40, l: 120, r: 10 },
              height: 300,
            }}
            style={{ width: "100%" }}
            config={{ displayModeBar: false }}
          />
        </div>

        {/* Waterfall */}
        <div className="glass-card" style={{ padding: 20 }}>
          <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14 }}>Local Explanation — Sample Prediction</h3>
          <Plot
            data={[{
              type: "waterfall", orientation: "v",
              x: WATERFALL.map(w => w.label),
              y: WATERFALL.map((w,i) => i===0 || i===WATERFALL.length-1 ? w.cumulative : w.value),
              measure: WATERFALL.map((_, i) => i===0 || i===WATERFALL.length-1 ? "absolute" : "relative"),
              connector: { line: { color: "#1e2d40" } },
              increasing: { marker: { color: "#ef4444" } },
              decreasing: { marker: { color: "#10b981" } },
              totals: { marker: { color: "#3b82f6" } },
              textposition: "outside",
              text: WATERFALL.map(w => w.value !== 0 ? `${w.value > 0 ? "+" : ""}${w.value}` : `${w.cumulative}`),
            }]}
            layout={{
              paper_bgcolor: "transparent", plot_bgcolor: "transparent",
              font: { color: "#94a3b8", family: "Inter", size: 10 },
              yaxis: { gridcolor: "#1e2d40", title: "AQI contribution" },
              xaxis: { tickangle: -30 },
              margin: { t: 20, b: 80, l: 50, r: 10 },
              height: 300,
            }}
            style={{ width: "100%" }}
            config={{ displayModeBar: false }}
          />
        </div>
      </div>

      {/* SHAP Explanation Cards */}
      <div className="glass-card" style={{ padding: 20 }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 16 }}>Feature Contribution Summary</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10 }}>
          {GLOBAL_FI.slice(0,6).map(f => (
            <div key={f.feature} className="stat-card" style={{ padding: "12px 14px" }}>
              <div style={{ fontSize: 11, fontFamily: "monospace", color: "var(--accent-blue)", marginBottom: 6 }}>{f.feature}</div>
              <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                <div style={{ flex: 1, height: 4, borderRadius: 2, background: "var(--border)" }}>
                  <div style={{ width: `${(f.mean_abs_shap / 45.2) * 100}%`, height: "100%", borderRadius: 2, background: "linear-gradient(90deg,#3b82f6,#8b5cf6)" }} />
                </div>
                <span style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)" }}>{f.mean_abs_shap}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
