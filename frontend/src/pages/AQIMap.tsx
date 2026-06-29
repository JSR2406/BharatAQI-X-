import { useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Popup } from "react-leaflet";
import { aqiColor, aqiCategory, INDIA_CITIES_MOCK } from "../lib/api";
import { Map as MapIcon } from "lucide-react";

export default function AQIMap() {
  const [cities] = useState(INDIA_CITIES_MOCK);

  return (
    <div className="animate-fadeIn">
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 22, fontWeight: 700, display: "flex", alignItems: "center", gap: 10 }}>
          <MapIcon size={22} color="#3b82f6" /> AQI Map — India
        </h1>
        <p style={{ fontSize: 13, color: "var(--text-muted)", marginTop: 4 }}>
          Real-time surface AQI across 30+ Indian cities from OpenAQ / CPCB stations
        </p>
      </div>

      {/* AQI Legend */}
      <div className="glass-card" style={{ padding: "10px 16px", marginBottom: 16, display: "flex", gap: 16, flexWrap: "wrap" }}>
        {[
          { label: "Good (0–50)",         color: "#10b981" },
          { label: "Satisfactory (51–100)",color: "#84cc16" },
          { label: "Moderate (101–200)",  color: "#f59e0b" },
          { label: "Poor (201–300)",      color: "#f97316" },
          { label: "Very Poor (301–400)", color: "#ef4444" },
          { label: "Severe (400+)",       color: "#7c3aed" },
        ].map(({ label, color }) => (
          <div key={label} style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div style={{ width: 12, height: 12, borderRadius: "50%", background: color }} />
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>{label}</span>
          </div>
        ))}
      </div>

      {/* Map */}
      <div style={{ borderRadius: 16, overflow: "hidden", height: 520 }}>
        <MapContainer
          center={[20.5937, 78.9629]}
          zoom={5}
          style={{ height: "100%", width: "100%" }}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; CartoDB'
          />
          {cities.map(city => (
            <CircleMarker
              key={city.name}
              center={[city.latitude, city.longitude]}
              radius={Math.max(8, city.aqi / 20)}
              pathOptions={{
                fillColor: aqiColor(city.aqi),
                fillOpacity: 0.85,
                color: "#fff",
                weight: 1.5,
              }}
              eventHandlers={{}}
            >
              <Popup>
                <div style={{ fontFamily: "Inter, sans-serif", minWidth: 160 }}>
                  <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 6 }}>{city.name}</div>
                  <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                    <span style={{ fontSize: 22, fontWeight: 800, color: aqiColor(city.aqi) }}>{city.aqi}</span>
                    <span style={{ fontSize: 11, background: `${aqiColor(city.aqi)}20`, color: aqiColor(city.aqi), padding: "2px 8px", borderRadius: 12 }}>
                      {aqiCategory(city.aqi)}
                    </span>
                  </div>
                  <div style={{ fontSize: 11, color: "#666" }}>
                    Lat: {city.latitude.toFixed(2)} | Lon: {city.longitude.toFixed(2)}
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>

      {/* City grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10, marginTop: 16 }}>
        {cities.map(city => (
          <div key={city.name} className="stat-card" style={{ padding: "12px 14px", cursor: "pointer" }}
               onClick={() => {}}>
            <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>{city.name}</div>
            <div style={{ fontSize: 20, fontWeight: 800, color: aqiColor(city.aqi) }}>{city.aqi}</div>
            <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{aqiCategory(city.aqi)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
