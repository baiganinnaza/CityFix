# 🏙️ CityFix Almaty AI

Professional intelligent platform for monitoring and classifying urban infrastructure problems in Almaty, powered by Large Language Models (LLM).

## ✨ Key Features

- **🧠 AI-Powered Classification**: Instant analysis of complaints using Together AI (Apriel-1.6-15b) to determine category, urgency, and validity.
- **🗺️ Interactive Map Hub**: Real-time visualization of city issues with heatmaps and marker clustering.
- **📊 Advanced Analytics Hub**: Deep insights through hierarchical charts (Treemaps), volume metrics, and interactive data filtering.
- **🚨 Intelligent Alerts**: Automatic detection of high-risk clusters ("Red Zones") to identify systemic infrastructure failures.
- **🎨 Professional UI**: Sleek, glassmorphism-inspired design with a modular template system.

## 📁 Project Structure

```bash
CityProblems/
├── backend/            # Business Logic & AI
│   ├── .env            # Core configuration (API Keys)
│   └── logic.py        # Classification engine & Cluster analysis
├── frontend/           # Presentation Layer (Streamlit)
│   ├── templates/      # Modular HTML UI components
│   ├── index.css       # Global design system
│   └── main.py         # App entry point & Navigation
├── README.md           # Project documentation
└── requirements.txt    # Project dependencies
```

## 🚀 Getting Started

1. **Setup Environment**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API**:
   Create `backend/.env` and add your `TOGETHER_API_KEY`.

3. **Run Application**:
   From the project root:
   ```bash
   streamlit run frontend/main.py
   ```

## 📋 Categorization Schema

| Category | Description |
|-----------|-------------|
| **Дороги** | Potholes, asphalt cracks, crossings, sidewalks. |
| **ЖКХ** | Water, heating, sewage, garbage, elevators. |
| **Свет** | Broken street lights or traffic lights. |
| **Опасность** | Direct threats (open manholes, gas leaks, fires). |
| **Другое** | Landscaping, benches, playgrounds. |

## 🛠️ Technical Stack

- **Streamlit**: Modern reactive web interface.
- **Together AI**: High-performance reasoning LLM for classification.
- **Folium**: Geographical data visualization.
- **Plotly**: Advanced data analytics and interactive charting.
- **CSS3/HTML5**: Custom design system with modular templates.
