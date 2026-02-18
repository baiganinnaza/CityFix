
import pandas as pd
import numpy as np
import random
import os
import json
import re
from openai import OpenAI
from dotenv import load_dotenv

# App configuration
ALMATY_LAT = 43.2389
ALMATY_LON = 76.8897

# Load environment variables from backend directory
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

_client = None

def _get_client():
    """Returns the OpenAI-compatible client for Together AI."""
    global _client
    if _client is None:
        _client = OpenAI(
            api_key=os.getenv("TOGETHER_API_KEY"),
            base_url=os.getenv("TOGETHER_API_BASE", "https://api.together.xyz/v1"),
        )
    return _client

SYSTEM_PROMPT = """You are a classification system for Almaty city complaints.

Analyze the complaint text and return:
1. CATEGORY (one of: Дороги, ЖКХ, Свет, Опасность, Другое)
2. URGENCY (Красный, Желтый, Зеленый)
3. VALIDITY (boolean)

Definitions for categories:
- Дороги: potholes, cracks, asphalt, sidewalks, crossings
- ЖКХ: water, heating, sewage, garbage, elevators, housing
- Свет: street lights, traffic lights
- Опасность: life threats (open manholes, broken wires, gas leaks, fires)
- Другое: benches, playgrounds, landscaping, etc.

Urgency levels:
- Красный: Immediate threat to life/health.
- Желтый: Serious problem interfering with normal life.
- Зеленый: Minor issue or inconvenience.

Respond STRICTLY with a JSON object:
{"category": "...", "urgency": "...", "urgency_level": integer, "is_valid": boolean, "reason": "OK or reason for rejection"}

urgency_level: Красный=3, Желтый=2, Зеленый=1, invalid=0.

The JSON object MUST be at the very start of the response.
"""

def classify_complaint(text):
    """
    Classifies a city complaint using the configured LLM API.
    
    Args:
        text (str): The user complaint description.
        
    Returns:
        dict: A dictionary containing Category, Urgency, Urgency_Level, Is_Valid, and Reason.
    """
    try:
        client = _get_client()
        model = os.getenv("TOGETHER_MODEL", "ServiceNow-AI/Apriel-1.6-15b-Thinker")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Complaint: {text}"},
            ],
            temperature=0.1,
            max_tokens=4096,
        )

        raw = (response.choices[0].message.content or "").strip()
        parsed = _parse_llm_json(raw)

        if parsed:
            return {
                "Category": parsed.get("category", "Другое"),
                "Urgency": parsed.get("urgency", "Зеленый"),
                "Urgency_Level": int(parsed.get("urgency_level", 1)),
                "Is_Valid": bool(parsed.get("is_valid", True)),
                "Reason": parsed.get("reason", "OK"),
            }

        return {
            "Category": "Другое",
            "Urgency": "Желтый",
            "Urgency_Level": 2,
            "Is_Valid": True,
            "Reason": "Fallback",
        }

    except Exception:
        return {
            "Category": "Ошибка",
            "Urgency": "Не определено",
            "Urgency_Level": 0,
            "Is_Valid": False,
            "Reason": "System Error",
        }

def _parse_llm_json(raw: str) -> dict | None:
    """Robustly extracts a JSON object from the model response."""
    # Strip thinking blocks and markdown
    cleaned = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL).strip()
    if "<think>" in cleaned and "</think>" not in cleaned:
        cleaned = cleaned.split("<think>")[0].strip()

    cleaned = re.sub(r"```json\s*", "", cleaned)
    cleaned = re.sub(r"```\s*", "", cleaned)
    cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Regex search for JSON block
    match = re.search(r'^\s*(\{[\s\S]*?"category"[\s\S]*?\})', cleaned, re.IGNORECASE)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    matches = list(re.finditer(r'\{[\s\S]*?"category"[\s\S]*?\}', cleaned, re.IGNORECASE))
    if matches:
        for m in matches:
            try:
                content = m.group()
                if content.count('{') == content.count('}'):
                    return json.loads(content)
            except json.JSONDecodeError:
                continue

    if cleaned.startswith('{') and not cleaned.endswith('}'):
        try:
            return json.loads(cleaned + '}')
        except:
            pass

    return None

def generate_synthetic_data(n=30):
    """Generates synthetic complaints for testing and demonstration."""
    data = []
    problem_templates = [
        "Огромная яма на дороге, пробил колесо.",
        "Не горит фонарь у подъезда, очень темно.",
        "Мусор не вывозят уже неделю, запах ужасный.",
        "Открытый люк на детской площадке, опасно!",
        "Прорвало трубу с горячей водой, кипятком заливает улицу.",
        "Сломан светофор на перекрестке, постоянные пробки.",
        "Упало дерево на машину во дворе.",
        "В подъезде грязно, никто не убирает.",
        "Свисают сосульки с крыши прямо над входом.",
        "Нет отопления в доме, батареи ледяные.",
    ]

    for _ in range(n):
        lat = ALMATY_LAT + random.uniform(-0.05, 0.05)
        lon = ALMATY_LON + random.uniform(-0.09, 0.09)
        text = random.choice(problem_templates)

        data.append({
            "Text": text,
            "Lat": lat,
            "Lon": lon,
            "Category": "Другое",
            "Urgency": "Зеленый",
            "Urgency_Level": 1,
            "Is_Valid": True,
        })

    return pd.DataFrame(data)

def check_red_zones(df):
    """Identifies clusters of critical reports."""
    if df.empty:
        return []
    red_complaints = df[df["Urgency"] == "Красный"]
    if len(red_complaints) < 3:
        return []
    
    alerts = []
    visited_indices = set()
    for idx, row in red_complaints.iterrows():
        if idx in visited_indices:
            continue
        neighbors = red_complaints[
            (np.abs(red_complaints["Lat"] - row["Lat"]) < 0.015) & 
            (np.abs(red_complaints["Lon"] - row["Lon"]) < 0.015)
        ]
        if len(neighbors) >= 3:
            visited_indices.update(neighbors.index)
            center_lat = neighbors["Lat"].mean()
            center_lon = neighbors["Lon"].mean()
            alerts.append(f"Systemic issue risk! Location: ({center_lat:.4f}, {center_lon:.4f}). Reports: {len(neighbors)}")
    return alerts
