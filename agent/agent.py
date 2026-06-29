"""
BharatAQI-X: Agentic AI Environmental Analyst
LangChain + Ollama (Qwen3) with Gemini API fallback.
"""
import logging, os, json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

try:
    from langchain_ollama import ChatOllama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    GEMINI_AVAILABLE = bool(os.getenv("GOOGLE_API_KEY"))
except ImportError:
    GEMINI_AVAILABLE = False

from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser


def aqi_category(aqi: float) -> str:
    if aqi <= 50:   return "Good"
    if aqi <= 100:  return "Satisfactory"
    if aqi <= 200:  return "Moderate"
    if aqi <= 300:  return "Poor"
    if aqi <= 400:  return "Very Poor"
    return "Severe"


ANALYST_PROMPT = ChatPromptTemplate.from_template("""
You are BharatAQI-X, an expert AI environmental analyst specializing in Indian air quality.
You have expertise in atmospheric chemistry, satellite remote sensing, public health,
and Indian environmental policy (CPCB/MoEFCC/GRAP regulations).

=== CURRENT DATA ===
Location: {city}, India  |  Date: {date}
AQI: {aqi} ({aqi_category})  |  PM2.5: {pm25} µg/m³  |  PM10: {pm10} µg/m³
NO2: {no2} µg/m³  |  SO2: {so2} µg/m³  |  CO: {co} mg/m³  |  O3: {o3} µg/m³
HCHO: {hcho} mol/m² (Sentinel-5P)
Temperature: {temperature}°C  |  Humidity: {humidity}%  |  Wind: {wind_speed} m/s
Active Fires Nearby: {fire_count} (NASA FIRMS)

Provide a structured analysis with these sections:
**ROOT CAUSE ANALYSIS** - Primary pollution sources
**48-HOUR PREDICTION** - AQI trend forecast
**HEALTH EFFECTS** - Risks by population group
**GOVERNMENT ADVICE** - CPCB/GRAP policy actions
**CITIZEN ADVICE** - Practical protective steps
**ENVIRONMENTAL INSIGHT** - HCHO + fire correlation analysis
""")


def _get_llm(model_name: str = "qwen3"):
    if OLLAMA_AVAILABLE:
        try:
            llm = ChatOllama(model=model_name, temperature=0.3)
            llm.invoke("test")
            return llm
        except Exception as e:
            logger.warning(f"Ollama failed: {e}")
    if GEMINI_AVAILABLE:
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.3,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
    raise RuntimeError("No LLM available. Set GOOGLE_API_KEY or install Ollama.")


def _mock_analysis(data: dict) -> str:
    cat = aqi_category(data.get("aqi", 0))
    aqi = data.get("aqi", 100)
    city = data.get("city", "India")
    fire_count = data.get("fire_count", 0)
    wind = data.get("wind_speed", 2)
    return f"""**ROOT CAUSE ANALYSIS**
AQI {aqi} ({cat}) in {city} is driven by vehicular emissions (~45%), industrial activity (~25%), and secondary aerosol formation. Low wind speed ({wind} m/s) is trapping pollutants. {fire_count} active fires contribute ~15% to PM2.5 via biomass burning.

**48-HOUR PREDICTION**
AQI expected to {'improve with increasing winds' if wind > 4 else 'remain elevated due to stagnant conditions'}. Predicted range: {max(0,aqi-30):.0f}–{aqi+30:.0f}.

**HEALTH EFFECTS**
• General population: {'Avoid prolonged outdoor exposure' if aqi > 150 else 'Normal activities OK'}.
• Children/elderly: Limit outdoor time; keep windows closed.
• Asthma/COPD patients: Carry rescue inhaler; avoid outdoor exercise.

**GOVERNMENT ADVICE**
• Activate GRAP Stage {'III' if aqi > 300 else 'II' if aqi > 200 else 'I'}.
• Enforce BS-VI emission norms; halt construction >500m² if AQI >300.
• Issue public advisory via Sameer App.

**CITIZEN ADVICE**
• {'Wear N95/KN95 mask for all outdoor activity' if aqi > 200 else 'Surgical mask for brief outdoor trips'}.
• Run HEPA air purifier indoors; keep windows closed.
• Avoid outdoor exercise 6–9 AM (peak pollution).

**ENVIRONMENTAL INSIGHT**
HCHO at {data.get('hcho','N/A')} mol/m² indicates {'elevated' if float(data.get('hcho',0) or 0) > 5e-5 else 'moderate'} formaldehyde from VOC oxidation. {fire_count} FIRMS fires {'significantly' if fire_count > 10 else 'marginally'} contribute to aerosol loading."""


class BharatAQIAgent:
    def __init__(self, model_name: str = "qwen3", use_mock: bool = False):
        self.use_mock = use_mock
        if not use_mock:
            try:
                self.llm   = _get_llm(model_name)
                self.chain = ANALYST_PROMPT | self.llm | StrOutputParser()
            except Exception as e:
                logger.warning(f"LLM init failed ({e}). Using mock mode.")
                self.use_mock = True

    def analyze(self, data: dict) -> str:
        data.setdefault("aqi_category", aqi_category(data.get("aqi", 0)))
        if self.use_mock:
            return _mock_analysis(data)
        try:
            return self.chain.invoke(data)
        except Exception as e:
            logger.error(f"Inference error: {e}")
            return _mock_analysis(data)


def analyze_location(**kwargs) -> str:
    use_mock = kwargs.pop("use_mock", True)
    agent = BharatAQIAgent(use_mock=use_mock)
    kwargs.setdefault("aqi_category", aqi_category(kwargs.get("aqi", 0)))
    return agent.analyze(kwargs)


if __name__ == "__main__":
    print(analyze_location(
        city="Delhi", aqi=285, pm25=120, pm10=210,
        no2=68, so2=22, co=2.1, o3=45, hcho=6.2e-5,
        temperature=18, humidity=75, wind_speed=1.2,
        fire_count=8, date="2024-01-15", use_mock=True,
    ))
