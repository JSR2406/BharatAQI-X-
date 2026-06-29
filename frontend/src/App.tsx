import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Home from "./pages/Home";
import AQIMap from "./pages/AQIMap";
import HCHOMap from "./pages/HCHOMap";
import Forecast from "./pages/Forecast";
import Explainability from "./pages/Explainability";
import AIAnalyst from "./pages/AIAnalyst";
import About from "./pages/About";
import "leaflet/dist/leaflet.css";
import "./index.css";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="aqi-map" element={<AQIMap />} />
          <Route path="hcho-map" element={<HCHOMap />} />
          <Route path="forecast" element={<Forecast />} />
          <Route path="explainability" element={<Explainability />} />
          <Route path="ai-analyst" element={<AIAnalyst />} />
          <Route path="about" element={<About />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
