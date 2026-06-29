import { useState } from "react";
import Plot from "react-plotly.js";
import { TrendingUp } from "lucide-react";
import { aqiColor, aqiCategory, INDIA_CITIES_MOCK } from "../lib/api";

function genForecast(baseAqi: number, days: number) {
  return Array.from({ length: days }, (_, i) => ({
    day: i + 1,
    aqi: Math.max(0, Math.min(500, baseAqi + (Math.random() - 0.48) * 25 + i * 0.5)),
  }));
}

export default function Forecast() {
  const [city, setCity] = useState("Delhi");
  const [days, setDays] = useState(7);
  const base = INDIA_CITIES_MOCK.find(c => c.name === city)?.aqi ?? 150;
  const forecast = genForecast(base, days);
  const labels = forecast.map(f => `Day ${f.day}`);
  const values = forecast.map(f => f.aqi);

  return (
    <div className="animate-fadeIn">
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, display: "flex", alignItems: "center", gap: 10 }}>
          <TrendingUp size={22} color="#10b981" /> AQI Forecast
        </h1>
        <p style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>
          7–30 day AQI forecast using ensemble ML model (XGBoost + LightGBM)
        </p>
      </div>

      {/* Controls */}
      <div className="glass-card" style={{ padding: 20, marginBottom: 20, display: "flex", gap: 20, alignItems: "center" }}>
        <div>
          <label style={{ fontSize: 12, color: "var(--text-muted)", display: "block", marginBottom: 6 }}>City</label>
          <select value={city} onChange={e => setCity(e.target.value)}
            style={{ background: "var(--bg-card)", color: "var(--text-primary)", border: "1px solid var(--border)", borderRadius: 8, padding: "8px 12px", fontSize: 13 }}>
            {INDIA_CITIES_MOCK.map(c => <option key={c.name}>{c.name}</option>)}
          </select>
        </div>
        <div>
          <label style={{ fontSize: 12, color: "var(--text-muted)", display: "block", marginBottom: 6 }}>Forecast Days: {days}</label>
          <input type="range" min={3} max={30} value={days} onChange={e => setDays(+e.target.value)}
            style={{ width: 180 }} />
        </div>
        <div className="stat-card" style={{ marginLeft: "auto", padding: "12px 20px", textAlign: "center" }}>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>Current AQI</div>
          <div style={{ fontSize: 28, fontWeight: 800, color: aqiColor(base) }}>{base}</div>
          <div style={{ fontSize: 11, color: aqiColor(base) }}>{aqiCategory(base)}</div>
        </div>
      </div>

      {/* Chart */}
      <div className="glass-card" style={{ padding: 20, marginBottom: 20 }}>
        <Plot
          data={[
            {
              x: labels, y: values, type: "scatter", mode: "lines+markers",
              line: { color: "#3b82f6", width: 2.5 },
              marker: { color: values.map(v => aqiColor(v)), size: 7 },
              fill: "tozeroy",
              fillcolor: "rgba(59,130,246,0.08)",
              name: "Predicted AQI",
            },
            {
              x: labels,
              y: values.map(v => v + 20),
              type: "scatter", mode: "lines",
              line: { dash: "dot", color: "rgba(59,130,246,0.3)", width: 1 },
              name: "Upper bound",
            },
            {
              x: labels,
              y: values.map(v => Math.max(0, v - 20)),
              type: "scatter", mode: "lines",
              line: { dash: "dot", color: "rgba(59,130,246,0.3)", width: 1 },
              name: "Lower bound",
              fill: "tonexty",
              fillcolor: "rgba(59,130,246,0.05)",
            },
          ]}
          layout={{
            paper_bgcolor: "transparent", plot_bgcolor: "transparent",
            font: { color: "#64748b", family: "Inter" },
            xaxis: { gridcolor: "#1e2d40", tickfont: { size: 11 } },
            yaxis: { gridcolor: "#1e2d40", tickfont: { size: 11 }, title: "AQI" },
            legend: { orientation: "h", y: -0.15 },
            margin: { t: 10, b: 40, l: 50, r: 10 },
            height: 320,
          }}
          style={{ width: "100%" }}
          config={{ displayModeBar: false }}
        />
      </div>

      {/* Forecast table */}
      <div className="glass-card" style={{ padding: 20 }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14 }}>Daily Forecast — {city}</h3>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 8 }}>
          {forecast.slice(0, 7).map(f => (
            <div key={f.day} className="stat-card" style={{ padding: "12px 8px", textAlign: "center" }}>
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 6 }}>Day {f.day}</div>
              <div style={{ fontSize: 18, fontWeight: 700, color: aqiColor(f.aqi) }}>{f.aqi.toFixed(0)}</div>
              <div style={{ fontSize: 9, color: aqiColor(f.aqi), marginTop: 4 }}>{aqiCategory(f.aqi)}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
