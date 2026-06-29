const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

async function apiFetch(path: string, options?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) throw new Error(`API error ${res.status}: ${res.statusText}`);
  return res.json();
}

export const api = {
  health:    () => apiFetch("/health"),
  cities:    () => apiFetch("/cities"),
  mapData:   (pollutant = "aqi") => apiFetch(`/map-data?pollutant=${pollutant}`),
  predict:   (body: object) => apiFetch("/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
  forecast:  (city: string, days = 7) => apiFetch(`/forecast?city=${city}&days=${days}`),
  hotspots:  (method = "any", top_n = 50) => apiFetch(`/hotspots?method=${method}&top_n=${top_n}`),
  explain:   (city = "Delhi") => apiFetch(`/explain?city=${city}`),
  analyze:   (body: object) => apiFetch("/analyze", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) }),
};

export function aqiColor(aqi: number): string {
  if (aqi <= 50)  return "#10b981";
  if (aqi <= 100) return "#84cc16";
  if (aqi <= 200) return "#f59e0b";
  if (aqi <= 300) return "#f97316";
  if (aqi <= 400) return "#ef4444";
  return "#7c3aed";
}

export function aqiCategory(aqi: number): string {
  if (aqi <= 50)  return "Good";
  if (aqi <= 100) return "Satisfactory";
  if (aqi <= 200) return "Moderate";
  if (aqi <= 300) return "Poor";
  if (aqi <= 400) return "Very Poor";
  return "Severe";
}

export const INDIA_CITIES_MOCK = [
  { name: "Delhi",     latitude: 28.61, longitude: 77.21, aqi: 285 },
  { name: "Mumbai",    latitude: 19.08, longitude: 72.88, aqi: 118 },
  { name: "Kolkata",   latitude: 22.57, longitude: 88.36, aqi: 198 },
  { name: "Chennai",   latitude: 13.08, longitude: 80.27, aqi: 92 },
  { name: "Bangalore", latitude: 12.97, longitude: 77.59, aqi: 85 },
  { name: "Hyderabad", latitude: 17.39, longitude: 78.49, aqi: 105 },
  { name: "Pune",      latitude: 18.52, longitude: 73.86, aqi: 97 },
  { name: "Ahmedabad", latitude: 23.02, longitude: 72.57, aqi: 142 },
  { name: "Lucknow",   latitude: 26.85, longitude: 80.95, aqi: 220 },
  { name: "Kanpur",    latitude: 26.45, longitude: 80.33, aqi: 268 },
  { name: "Patna",     latitude: 25.59, longitude: 85.14, aqi: 245 },
  { name: "Jaipur",    latitude: 26.91, longitude: 75.79, aqi: 165 },
];
