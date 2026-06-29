import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { Wind, AlertTriangle } from "lucide-react";

const HCHO_HOTSPOTS = [
  { lat: 28.6,  lon: 77.2,  hcho: 8.2e-5, state: "Delhi",         cluster: 0 },
  { lat: 30.2,  lon: 75.8,  hcho: 7.4e-5, state: "Punjab",        cluster: 1 },
  { lat: 25.3,  lon: 83.0,  hcho: 6.8e-5, state: "Uttar Pradesh", cluster: 2 },
  { lat: 22.5,  lon: 88.4,  hcho: 6.1e-5, state: "West Bengal",   cluster: 3 },
  { lat: 21.0,  lon: 82.0,  hcho: 5.9e-5, state: "MP/CG",         cluster: 4 },
  { lat: 26.5,  lon: 80.3,  hcho: 5.7e-5, state: "Uttar Pradesh", cluster: 2 },
  { lat: 31.6,  lon: 74.9,  hcho: 7.1e-5, state: "Punjab",        cluster: 1 },
  { lat: 24.0,  lon: 93.0,  hcho: 4.8e-5, state: "Manipur",       cluster: 5 },
  { lat: 20.5,  lon: 85.0,  hcho: 5.2e-5, state: "Odisha",        cluster: 6 },
  { lat: 23.3,  lon: 85.3,  hcho: 4.5e-5, state: "Jharkhand",     cluster: 7 },
  { lat: 26.1,  lon: 91.7,  hcho: 4.2e-5, state: "Assam",         cluster: 8 },
  { lat: 17.4,  lon: 78.5,  hcho: 3.8e-5, state: "Telangana",     cluster: 9 },
];

function hchoColor(val: number): string {
  if (val > 7e-5) return "#7c3aed";
  if (val > 5e-5) return "#ef4444";
  if (val > 3e-5) return "#f97316";
  return "#f59e0b";
}

export default function HCHOMap() {
  return (
    <div className="animate-fadeIn">
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, display: "flex", alignItems: "center", gap: 10 }}>
          <Wind size={22} color="#8b5cf6" /> HCHO Hotspot Map
        </h1>
        <p style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>
          Formaldehyde (HCHO) hotspots detected from Sentinel-5P satellite data using DBSCAN + Isolation Forest
        </p>
      </div>

      {/* Info */}
      <div className="glass-card" style={{ padding: "10px 16px", marginBottom: 16, display: "flex", gap: 20, alignItems: "center" }}>
        <AlertTriangle size={14} color="#f59e0b" />
        <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
          Larger circles = higher HCHO concentration. Purple = extreme hotspot (industrial/biomass burning)
        </span>
        <div style={{ display: "flex", gap: 12, marginLeft: "auto" }}>
          {[
            { label: ">7e-5", color: "#7c3aed" },
            { label: ">5e-5", color: "#ef4444" },
            { label: ">3e-5", color: "#f97316" },
            { label: "<3e-5", color: "#f59e0b" },
          ].map(({ label, color }) => (
            <div key={label} style={{ display: "flex", alignItems: "center", gap: 5 }}>
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: color }} />
              <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{label}</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ borderRadius: 16, overflow: "hidden", height: 500, marginBottom: 20 }}>
        <MapContainer center={[22, 80]} zoom={5} style={{ height: "100%", width: "100%" }}>
          <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" attribution="&copy; CartoDB" />
          {HCHO_HOTSPOTS.map((h, i) => (
            <CircleMarker
              key={i}
              center={[h.lat, h.lon]}
              radius={Math.max(8, h.hcho / 3e-6)}
              pathOptions={{ fillColor: hchoColor(h.hcho), fillOpacity: 0.8, color: "#fff", weight: 1 }}
            >
              <Popup>
                <div style={{ fontFamily: "Inter,sans-serif" }}>
                  <b>{h.state}</b><br />
                  HCHO: <b style={{ color: hchoColor(h.hcho) }}>{h.hcho.toExponential(2)} mol/m²</b><br />
                  Cluster: {h.cluster}
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      {/* Hotspot table */}
      <div className="glass-card" style={{ padding: 20 }}>
        <h3 style={{ fontSize: 14, fontWeight: 600, marginBottom: 14 }}>Top HCHO Hotspots by State</h3>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ color: "var(--text-muted)", fontSize: 11 }}>
              {["Rank","State","HCHO (mol/m²)","Cluster","Risk Level"].map(h => (
                <th key={h} style={{ textAlign: "left", padding: "6px 12px", borderBottom: "1px solid var(--border)" }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {[...HCHO_HOTSPOTS].sort((a,b) => b.hcho - a.hcho).map((h, i) => (
              <tr key={i} style={{ borderBottom: "1px solid rgba(30,45,64,0.5)" }}>
                <td style={{ padding: "8px 12px", color: "var(--text-muted)" }}>#{i+1}</td>
                <td style={{ padding: "8px 12px", fontWeight: 500 }}>{h.state}</td>
                <td style={{ padding: "8px 12px", color: hchoColor(h.hcho), fontFamily: "monospace", fontWeight: 600 }}>{h.hcho.toExponential(2)}</td>
                <td style={{ padding: "8px 12px", color: "var(--text-muted)" }}>{h.cluster}</td>
                <td style={{ padding: "8px 12px" }}>
                  <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 20, background: `${hchoColor(h.hcho)}20`, color: hchoColor(h.hcho) }}>
                    {h.hcho > 7e-5 ? "Extreme" : h.hcho > 5e-5 ? "High" : h.hcho > 3e-5 ? "Moderate" : "Low"}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
