
import pandas as pd
import numpy as np
import random
import os
from transformers import pipeline

# --- Configuration ---
ALMATY_LAT = 43.2389
ALMATY_LON = 76.8897

# --- AI Model (Cached Locally) ---
def load_model():
    """
    Loads the mDeBERTa model from the local_model folder (already downloaded).
    """
    # Абсолютный путь к папке с моделью (рядом с logic.py)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(base_dir, "local_model")
    
    if os.path.exists(model_path):
        print(f"✅ Загрузка модели из {model_path}...")
        return pipeline("zero-shot-classification", model=model_path, device=-1)
    
    raise FileNotFoundError(
        f"❌ Модель не найдена в {model_path}!\n"
        f"Сначала запустите: python download_model.py"
    )

# Global model instance
_classifier = None

def get_model():
    global _classifier
    if _classifier is None:
        _classifier = load_model()
    return _classifier

# --- Classification Logic ---

def classify_complaint(text):
    """
    Classifies using mDeBERTa Multi-lingual LLM.
    Category-first approach: classify what the complaint is about,
    then determine urgency. Only reject obvious spam.
    Returns: {Category, Urgency, Urgency_Level, Is_Valid, Reason}
    """
    try:
        classifier = get_model()
        
        # ── Step 1: Category (what is the complaint about?) ──
        # Use detailed descriptive labels so the model understands context
        category_hypotheses = {
            "сломанная дорога, яма на дороге, проблема с асфальтом или тротуаром": "Дороги",
            "проблема с водой, отоплением, канализацией, мусором или жилым домом": "ЖКХ",
            "не работает фонарь, нет освещения, темно на улице": "Свет",
            "опасность для жизни, пожар, обрыв провода, открытый люк, утечка газа": "Опасность",
            "сломанная скамейка, детская площадка, благоустройство, другая городская проблема": "Другое",
        }
        
        cat_result = classifier(
            text, 
            list(category_hypotheses.keys()), 
            multi_label=False
        )
        
        best_hypothesis = cat_result["labels"][0]
        best_category = category_hypotheses[best_hypothesis]
        cat_score = cat_result["scores"][0]
        
        # ── Step 2: Spam check (only reject if VERY confident it's not a complaint) ──
        spam_labels = [
            "жалоба на городскую проблему или поломку",
            "бессмысленный текст, спам, реклама или случайные символы"
        ]
        spam_result = classifier(text, spam_labels, multi_label=False)
        
        is_spam = spam_result["labels"][0] == spam_labels[1]
        spam_score = spam_result["scores"][0] if is_spam else 0
        
        # Only reject if model is >55% confident it's spam AND category score is low
        if is_spam and spam_score > 0.55 and cat_score < 0.3:
            return {
                "Category": "Не определено",
                "Urgency": "Не определено",
                "Urgency_Level": 0,
                "Is_Valid": False,
                "Reason": f"Текст не похож на жалобу ({int(spam_score*100)}%)"
            }

        # ── Step 3: Urgency ──
        urgency_hypotheses = {
            "пожар, взрыв, обрыв провода, утечка газа, угроза жизни": ("Красный", 3),
            "серьезная поломка, нет воды или отопления, большая яма": ("Желтый", 2),
            "мелкий ремонт, грязь, эстетическая проблема, сломанная скамейка": ("Зеленый", 1),
        }
        
        urg_result = classifier(
            text,
            list(urgency_hypotheses.keys()),
            multi_label=False
        )
        
        best_urg = urg_result["labels"][0]
        urgency, urgency_level = urgency_hypotheses[best_urg]
            
        return {
            "Category": best_category,
            "Urgency": urgency,
            "Urgency_Level": urgency_level,
            "Is_Valid": True,
            "Reason": "OK"
        }
    except Exception as e:
        print(f"Classification Error: {e}")
        return {
            "Category": "Ошибка",
            "Urgency": "Не определено",
            "Urgency_Level": 0,
            "Is_Valid": False,
            "Reason": f"Ошибка модели: {str(e)}"
        }

# --- Synthetic Data Generation ---

def generate_synthetic_data(n=30):
    """
    Generates n synthetic complaints with existing coordinates around Almaty.
    """
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
    
    # Pre-calculated dummy classifications to avoid slow loading on synth generation
    # purely for test data generation speed
    
    for _ in range(n):
        lat = ALMATY_LAT + random.uniform(-0.05, 0.05)
        lon = ALMATY_LON + random.uniform(-0.09, 0.09)
        text = random.choice(problem_templates)
        
        # Minimalist fake classification for synth data to avoid heavy model calls during synth generation
        # In real app usage, everything goes through classify_complaint
        
        complaint = {
            "Text": text,
            "Lat": lat,
            "Lon": lon,
            "Category": "Другое", # placeholder
            "Urgency": "Зеленый",
            "Urgency_Level": 1,
            "Is_Valid": True
        }
        data.append(complaint)
        
    return pd.DataFrame(data)

# --- Analysis Logic ---

def check_red_zones(df, radius_km=1.0):
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
            alerts.append(f"Внимание! Риск системной аварии в районе координат ({center_lat:.4f}, {center_lon:.4f}). Обнаружено {len(neighbors)} критических жалоб!")
    return alerts
