import { NavLink, Outlet } from "react-router-dom";
import {
  Home, Map, Wind, TrendingUp, Brain, Cpu, Info,
  Satellite, Activity
} from "lucide-react";

const navItems = [
  { to: "/",              icon: Home,       label: "Home" },
  { to: "/aqi-map",      icon: Map,        label: "AQI Map" },
  { to: "/hcho-map",     icon: Wind,       label: "HCHO Map" },
  { to: "/forecast",     icon: TrendingUp, label: "Forecast" },
  { to: "/explainability",icon: Brain,     label: "Explainability" },
  { to: "/ai-analyst",   icon: Cpu,        label: "AI Analyst" },
  { to: "/about",        icon: Info,       label: "About" },
];

export default function Layout() {
  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-primary)" }}>
      {/* Sidebar */}
      <aside className="sidebar" style={{ width: 220, flexShrink: 0, padding: "20px 12px", display: "flex", flexDirection: "column", gap: 4 }}>
        {/* Logo */}
        <div style={{ padding: "12px 8px 24px", borderBottom: "1px solid var(--border)", marginBottom: 12 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{ width: 36, height: 36, borderRadius: 10, background: "linear-gradient(135deg,#3b82f6,#8b5cf6)", display: "flex", alignItems: "center", justifyContent: "center" }}>
              <Satellite size={18} color="#fff" />
            </div>
            <div>
              <div className="gradient-text" style={{ fontFamily: "'Space Grotesk',sans-serif", fontWeight: 700, fontSize: 14 }}>BharatAQI-X</div>
              <div style={{ fontSize: 10, color: "var(--text-muted)" }}>Digital Twin</div>
            </div>
          </div>
        </div>

        {/* Nav */}
        {navItems.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) => `nav-item${isActive ? " active" : ""}`}
          >
            <Icon size={16} />
            <span style={{ fontSize: 14, fontWeight: 500 }}>{label}</span>
          </NavLink>
        ))}

        {/* Status */}
        <div style={{ marginTop: "auto", padding: "12px 8px", borderTop: "1px solid var(--border)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
            <div className="animate-pulse-glow" style={{ width: 8, height: 8, borderRadius: "50%", background: "#10b981" }} />
            <span style={{ fontSize: 11, color: "var(--text-muted)" }}>BAH 2026 · Live</span>
          </div>
          <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 4 }}>
            <Activity size={10} style={{ display: "inline", marginRight: 4 }} />
            ISRO Sentinel-5P Feed
          </div>
        </div>
      </aside>

      {/* Main */}
      <main style={{ flex: 1, overflow: "auto", padding: "24px 28px" }}>
        <Outlet />
      </main>
    </div>
  );
}
