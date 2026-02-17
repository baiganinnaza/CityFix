from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
import os

def download_and_save():
    model_name = "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli"
    model_path = "./local_model"
    
    print(f"⏳ Начинаю скачивание мощной модели {model_name}...")
    print("Это займет время (около 800-900 МБ)... Не закрывайте окно.")
    
    # Download model and tokenizer
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    
    # Save locally
    model.save_pretrained(model_path)
    tokenizer.save_pretrained(model_path)
    
    print(f"✅ Модель успешно сохранена в {model_path}!")
    print("Теперь можно запускать 'streamlit run app.py'.")

if __name__ == "__main__":
    download_and_save()
