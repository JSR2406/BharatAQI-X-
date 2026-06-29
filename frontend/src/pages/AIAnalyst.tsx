import { useState } from "react";
import { Cpu, Loader2, Send } from "lucide-react";
import { aqiColor, aqiCategory } from "../lib/api";

const DEFAULT = { city: "Delhi", aqi: 285, pm25: 120, pm10: 210, no2: 68, so2: 22, co: 2.1, o3: 45, hcho: 6.2e-5, temperature: 18, humidity: 75, wind_speed: 1.2, fire_count: 8 };

function mockAnalysis(d: typeof DEFAULT) {
  return `**ROOT CAUSE ANALYSIS**
AQI ${d.aqi} (${aqiCategory(d.aqi)}) in ${d.city}: vehicular ~45%, industrial ~25%, biomass burning (${d.fire_count} fires) ~15%, secondary aerosols ~15%. Wind ${d.wind_speed} m/s insufficient for dispersion.

**48-HOUR PREDICTION**
${d.wind_speed < 3 ? "Stagnant conditions → pollution persists." : "Improving winds → gradual improvement."} Expected AQI: ${Math.max(0, d.aqi - 30).toFixed(0)}–${(d.aqi + 25).toFixed(0)}.

**HEALTH EFFECTS**
• General: Avoid outdoor exposure
• Children/elderly: Stay indoors
• Asthma/COPD: Use rescue inhaler; no outdoor exertion
• Pregnant: HEPA purifier indoors

**GOVERNMENT ADVICE (GRAP)**
• GRAP Stage ${d.aqi > 300 ? "III–IV" : d.aqi > 200 ? "II" : "I"} activation
• Halt construction >500m²; odd-even vehicles
• Issue advisory via Sameer App / SAFAR

**CITIZEN ADVICE**
• N95/KN95 mask for all outdoor activity
• HEPA purifier indoors; windows closed
• Avoid exercise 6–10 AM

**ENVIRONMENTAL INSIGHT**
HCHO ${(d.hcho as number).toExponential(2)} mol/m² — ${(d.hcho as number) > 5e-5 ? "ELEVATED" : "MODERATE"}.
${d.fire_count} fires ${d.fire_count > 10 ? "significantly" : "marginally"} contributing to PM2.5 via long-range transport.`;
}

export default function AIAnalyst() {
  const [form, setForm] = useState(DEFAULT);
  const [analysis, setAnalysis] = useState("");
  const [loading, setLoading] = useState(false);

  const analyze = async () => {
    setLoading(true);
    await new Promise(r => setTimeout(r, 1200));
    setAnalysis(mockAnalysis(form));
    setLoading(false);
  };

  return (
    <div className="animate-fadeIn">
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, display: "flex", alignItems: "center", gap: 10 }}>
          <Cpu size={22} color="#8b5cf6" /> AI Environmental Analyst
        </h1>
        <p style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>Powered by LangChain + Qwen3 (Ollama) with Gemini fallback</p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "320px 1fr", gap: 20 }}>
        <div className="glass-card" style={{ padding: 20 }}>
          <h3 style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", marginBottom: 16 }}>INPUT PARAMETERS</h3>
          <div style={{ marginBottom: 12 }}>
            <label style={{ fontSize: 11, color: "var(--text-muted)", display: "block", marginBottom: 4 }}>City</label>
            <input value={form.city} onChange={e => setForm({ ...form, city: e.target.value })}
              style={{ width: "100%", background: "var(--bg-card)", color: "var(--text-primary)", border: "1px solid var(--border)", borderRadius: 8, padding: "7px 10px", fontSize: 13 }} />
          </div>
          <div style={{ textAlign: "center", padding: "12px 0 16px", marginBottom: 12, borderTop: "1px solid var(--border)", borderBottom: "1px solid var(--border)" }}>
            <div style={{ fontSize: 40, fontWeight: 800, color: aqiColor(form.aqi) }}>{form.aqi}</div>
            <div style={{ fontSize: 12, color: aqiColor(form.aqi) }}>{aqiCategory(form.aqi)}</div>
          </div>
          {[
            { key: "aqi", label: "AQI", min: 0, max: 500 },
            { key: "pm25", label: "PM2.5", min: 0, max: 300 },
            { key: "no2", label: "NO2", min: 0, max: 200 },
            { key: "temperature", label: "Temp °C", min: -5, max: 50 },
            { key: "humidity", label: "Humidity %", min: 0, max: 100 },
            { key: "wind_speed", label: "Wind m/s", min: 0, max: 20 },
            { key: "fire_count", label: "Active Fires", min: 0, max: 100 },
          ].map(({ key, label, min, max }) => (
            <div key={key} style={{ marginBottom: 10 }}>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                <label style={{ fontSize: 11, color: "var(--text-muted)" }}>{label}</label>
                <span style={{ fontSize: 11, fontWeight: 600 }}>{(form as any)[key]}</span>
              </div>
              <input type="range" min={min} max={max} value={(form as any)[key]}
                onChange={e => setForm({ ...form, [key]: parseFloat(e.target.value) })}
                style={{ width: "100%", accentColor: "#3b82f6" }} />
            </div>
          ))}
          <button className="btn-primary" onClick={analyze} disabled={loading}
            style={{ width: "100%", marginTop: 12, display: "flex", alignItems: "center", justifyContent: "center", gap: 8 }}>
            {loading ? <Loader2 size={16} /> : <Send size={16} />}
            {loading ? "Analyzing…" : "Analyze with AI"}
          </button>
        </div>

        <div className="glass-card" style={{ padding: 24, minHeight: 400 }}>
          {!analysis && !loading && (
            <div style={{ textAlign: "center", marginTop: 80, color: "var(--text-muted)" }}>
              <Cpu size={48} style={{ marginBottom: 16, opacity: 0.3 }} />
              <p>Configure parameters and click Analyze</p>
            </div>
          )}
          {loading && <div style={{ textAlign: "center", marginTop: 80 }}><Loader2 size={36} color="#3b82f6" /><p style={{ marginTop: 16, color: "var(--text-muted)", fontSize: 13 }}>Qwen3 analyzing…</p></div>}
          {analysis && !loading && (
            <div className="animate-fadeIn">
              {analysis.split("\n\n").map((para, i) => (
                <div key={i} style={{ marginBottom: 16 }}>
                  {para.startsWith("**") ? (
                    <>
                      <div style={{ fontSize: 12, fontWeight: 700, color: "var(--accent-blue)", marginBottom: 6 }}>{para.split("\n")[0].replace(/\*\*/g, "")}</div>
                      {para.split("\n").slice(1).map((line, j) => <div key={j} style={{ fontSize: 13, lineHeight: 1.8 }}>{line}</div>)}
                    </>
                  ) : <p style={{ fontSize: 13, color: "var(--text-muted)" }}>{para}</p>}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
