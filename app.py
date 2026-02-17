import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster
import plotly.express as px
import plotly.graph_objects as go
import logic

# ═══════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════
st.set_page_config(
    page_title="CityFix AI · Almaty",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ═══════════════════════════════════════════════════════
# GLOBAL STYLES (LIGHT THEME)
# ═══════════════════════════════════════════════════════
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ── Base ── */
    html, body, .stApp {
        font-family: 'Inter', sans-serif !important;
    }
    .stApp {
        background: #FFFFFF;
    }

    /* ── Hide Streamlit default ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #F7F8FA 0%, #FFFFFF 100%);
        border-right: 1px solid rgba(0, 166, 126, 0.12);
    }
    section[data-testid="stSidebar"] .stRadio > label {
        color: #6B7280 !important;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: rgba(0,0,0, 0.02);
        border: 1px solid rgba(0,0,0,0.06);
        border-radius: 12px;
        padding: 12px 16px !important;
        margin-bottom: 6px;
        transition: all 0.3s ease;
    }
    section[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        background: rgba(0, 166, 126, 0.06);
        border-color: rgba(0, 166, 126, 0.25);
    }

    /* ── Glass Card (Light) ── */
    .glass-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 20px;
        padding: 32px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .glass-card:hover {
        border-color: rgba(0, 166, 126, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0, 166, 126, 0.08), 0 4px 12px rgba(0,0,0,0.06);
    }

    /* ── Metric Card ── */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.08);
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00A67E, #00B4D8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 8px 0;
    }
    .metric-label {
        color: #6B7280;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .metric-card.red .metric-value {
        background: linear-gradient(135deg, #EF4444, #DC2626);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card.yellow .metric-value {
        background: linear-gradient(135deg, #F59E0B, #D97706);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-card.green .metric-value {
        background: linear-gradient(135deg, #10B981, #059669);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* ── Landing Hero ── */
    .landing-bg {
        background: radial-gradient(ellipse at 20% 50%, rgba(0, 166, 126, 0.06) 0%, transparent 50%),
                    radial-gradient(ellipse at 80% 20%, rgba(0, 180, 216, 0.04) 0%, transparent 50%);
        min-height: 70vh;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        padding: 40px 20px;
    }
    .hero-badge {
        background: rgba(0, 166, 126, 0.08);
        border: 1px solid rgba(0, 166, 126, 0.25);
        color: #00A67E;
        padding: 8px 20px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 2px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 24px;
        animation: fadeInDown 0.8s ease;
    }
    .hero-title {
        font-size: 4.5rem;
        font-weight: 900;
        line-height: 1.05;
        text-align: center;
        margin-bottom: 16px;
        color: #1A1F2E;
        animation: fadeInUp 1s ease;
    }
    .hero-title .accent {
        background: linear-gradient(135deg, #00A67E, #00B4D8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
        font-size: 1.25rem;
        color: #6B7280;
        text-align: center;
        max-width: 600px;
        margin: 0 auto 40px;
        line-height: 1.7;
        animation: fadeInUp 1.2s ease;
    }

    /* ── Feature Cards ── */
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin: 40px 0;
    }
    .feature-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 16px;
        padding: 28px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.3s ease;
    }
    .feature-card:hover {
        border-color: rgba(0, 166, 126, 0.3);
        transform: translateY(-4px);
        box-shadow: 0 12px 28px rgba(0, 166, 126, 0.08);
    }
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 16px;
    }
    .feature-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1A1F2E;
        margin-bottom: 8px;
    }
    .feature-desc {
        color: #6B7280;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    /* ── Page Header ── */
    .page-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 28px;
        padding-bottom: 20px;
        border-bottom: 1px solid #E5E7EB;
    }
    .page-header-icon {
        font-size: 2rem;
        background: linear-gradient(135deg, #00A67E, #00B4D8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .page-header-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1A1F2E;
    }
    .page-header-sub {
        color: #6B7280;
        font-size: 0.9rem;
    }

    /* ── Status Badge ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-badge.safe {
        background: rgba(16, 185, 129, 0.08);
        color: #059669;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    .status-badge.danger {
        background: rgba(239, 68, 68, 0.08);
        color: #DC2626;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }

    /* ── Animations ── */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeInDown {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* ── Form styling ── */
    .stTextArea textarea {
        background: #F9FAFB !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        color: #1A1F2E !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextArea textarea:focus {
        border-color: #00A67E !important;
        box-shadow: 0 0 0 2px rgba(0, 166, 126, 0.15) !important;
    }

    /* ── Button ── */
    .stButton > button {
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.5px;
        transition: all 0.3s ease !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #00A67E, #00B4D8) !important;
        border: none !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 166, 126, 0.3) !important;
    }

    /* ── Divider ── */
    hr {
        border-color: #E5E7EB !important;
    }

    /* ── Alert override ── */
    .stAlert {
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════
if "complaints_data" not in st.session_state:
    st.session_state.complaints_data = pd.DataFrame(columns=[
        "Text", "Lat", "Lon", "Category", "Urgency", "Urgency_Level"
    ])
    with st.spinner("⏳ Загружаю нейросеть mDeBERTa..."):
        logic.get_model()

if "current_page" not in st.session_state:
    st.session_state.current_page = "Landing"

df = st.session_state.complaints_data

# ═══════════════════════════════════════════════════════
# NAVIGATION
# ═══════════════════════════════════════════════════════
def go_to(page):
    st.session_state.current_page = page
    st.rerun()

# ═══════════════════════════════════════════════════════
# LANDING PAGE
# ═══════════════════════════════════════════════════════
def show_landing():
    st.markdown("""
    <div class="landing-bg">
        <div class="hero-badge">🧠 Powered by AI</div>
        <div class="hero-title">
            <span class="accent">CityFix</span> Almaty
        </div>
        <div class="hero-subtitle">
            Интеллектуальная платформа мониторинга городских проблем.<br>
            Отправляйте жалобы, а ИИ мгновенно классифицирует их по категории и срочности.
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, cta_col, _ = st.columns([2, 1, 2])
    with cta_col:
        if st.button("🚀  Запустить систему", use_container_width=True, type="primary"):
            go_to("Map")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown("""
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">🗺️</div>
            <div class="feature-title">Интерактивная карта</div>
            <div class="feature-desc">Отмечайте проблемы прямо на карте Алматы с точными координатами.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🧠</div>
            <div class="feature-title">AI-Классификация</div>
            <div class="feature-desc">Нейросеть mDeBERTa автоматически определяет категорию и срочность.</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Аналитика</div>
            <div class="feature-desc">Дашборд с визуализацией данных и автоматическими алертами опасных зон.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Жалоб обработано</div>
            <div class="metric-value">{len(df)}</div>
        </div>
        """, unsafe_allow_html=True)
    with s2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Категорий</div>
            <div class="metric-value">5</div>
        </div>
        """, unsafe_allow_html=True)
    with s3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">Модель</div>
            <div class="metric-value" style="font-size:1.4rem">mDeBERTa</div>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# MAP PAGE
# ═══════════════════════════════════════════════════════
def show_map():
    st.markdown("""
    <div class="page-header">
        <span class="page-header-icon">📍</span>
        <div>
            <div class="page-header-title">Карта жалоб</div>
            <div class="page-header-sub">Кликните по карте, чтобы указать место проблемы</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_map, col_form = st.columns([3, 1], gap="large")

    with col_map:
        m = folium.Map(
            location=[logic.ALMATY_LAT, logic.ALMATY_LON],
            zoom_start=12,
            tiles="CartoDB positron"
        )

        if not df.empty:
            heat_data = [[r["Lat"], r["Lon"]] for _, r in df.iterrows()]
            HeatMap(heat_data, radius=18, blur=15, gradient={0.4: '#10B981', 0.65: '#F59E0B', 1: '#EF4444'}).add_to(m)

            cluster = MarkerCluster().add_to(m)
            color_map = {"Красный": "red", "Желтый": "orange", "Зеленый": "green"}
            icon_map = {
                "Дороги": "road", "ЖКХ": "wrench",
                "Свет": "lightbulb-o", "Опасность": "exclamation-triangle",
                "Другое": "info-sign"
            }
            for _, row in df.iterrows():
                folium.Marker(
                    [row["Lat"], row["Lon"]],
                    popup=folium.Popup(f"<b>{row['Category']}</b><br><span style='color:#6B7280'>{row['Text']}</span>", max_width=280),
                    tooltip=f"{row['Urgency']}",
                    icon=folium.Icon(
                        color=color_map.get(row["Urgency"], "blue"),
                        icon=icon_map.get(row["Category"], "info-sign"),
                        prefix="fa"
                    )
                ).add_to(cluster)

        alerts = logic.check_red_zones(df)
        if alerts:
            st.markdown(f'<div class="status-badge danger">🚨 {len(alerts)} критических зон обнаружено</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge safe">✅ Критических зон нет</div>', unsafe_allow_html=True)

        map_output = st_folium(m, width="100%", height=550, returned_objects=["last_clicked"])

    with col_form:
        st.markdown("""
        <div class="glass-card" style="padding:24px">
            <div style="font-size:1.2rem; font-weight:700; margin-bottom:4px; color:#1A1F2E;">📝 Новая жалоба</div>
            <div style="color:#6B7280; font-size:0.85rem;">Опишите городскую проблему</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("complaint_form"):
            new_text = st.text_area(
                "Текст жалобы",
                height=120,
                placeholder="Например: На перекрестке Абая и Сейфуллина не работает светофор..."
            )

            clicked_lat = logic.ALMATY_LAT
            clicked_lon = logic.ALMATY_LON
            if map_output and map_output.get("last_clicked"):
                clicked_lat = map_output["last_clicked"]["lat"]
                clicked_lon = map_output["last_clicked"]["lng"]

            st.markdown(f"""
            <div style="background:rgba(0,166,126,0.05); border:1px solid rgba(0,166,126,0.2);
                        border-radius:10px; padding:12px; margin:8px 0;">
                <span style="color:#00A67E; font-weight:600;">📍 Координаты</span><br>
                <span style="color:#6B7280; font-size:0.85rem;">{clicked_lat:.5f}, {clicked_lon:.5f}</span>
            </div>
            """, unsafe_allow_html=True)

            submitted = st.form_submit_button("Отправить →", use_container_width=True, type="primary")

            if submitted:
                if not new_text:
                    st.error("Пожалуйста, введите текст жалобы.")
                else:
                    with st.spinner("🧠 AI анализирует..."):
                        result = logic.classify_complaint(new_text)
                        if not result["Is_Valid"]:
                            st.error(f"❌ Отклонено: {result['Reason']}")
                        else:
                            new_rec = {"Text": new_text, "Lat": clicked_lat, "Lon": clicked_lon, **result}
                            st.session_state.complaints_data = pd.concat(
                                [st.session_state.complaints_data, pd.DataFrame([new_rec])],
                                ignore_index=True)
                            st.success(f"✅ {result['Category']} · {result['Urgency']}")
                            st.rerun()

# ═══════════════════════════════════════════════════════
# ANALYTICS PAGE
# ═══════════════════════════════════════════════════════
def show_analytics():
    st.markdown("""
    <div class="page-header">
        <span class="page-header-icon">📊</span>
        <div>
            <div class="page-header-title">Аналитика</div>
            <div class="page-header-sub">Сводная панель по городским проблемам</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.markdown("""
        <div class="glass-card" style="text-align:center; padding:60px">
            <div style="font-size:3rem; margin-bottom:16px;">📭</div>
            <div style="font-size:1.2rem; font-weight:600; margin-bottom:8px; color:#1A1F2E;">Данных пока нет</div>
            <div style="color:#6B7280;">Отправьте жалобу на карте, чтобы увидеть аналитику.</div>
        </div>
        """, unsafe_allow_html=True)
        return

    total = len(df)
    red = len(df[df["Urgency"] == "Красный"])
    yellow = len(df[df["Urgency"] == "Желтый"])
    green = len(df[df["Urgency"] == "Зеленый"])

    c1, c2, c3, c4 = st.columns(4, gap="medium")
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Всего</div><div class="metric-value">{total}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card red"><div class="metric-label">Критические</div><div class="metric-value">{red}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card yellow"><div class="metric-label">Средние</div><div class="metric-value">{yellow}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card green"><div class="metric-label">Низкие</div><div class="metric-value">{green}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    alerts = logic.check_red_zones(df)
    if alerts:
        st.markdown('<div class="status-badge danger" style="margin-bottom:16px;">🚨 Обнаружены критические скопления!</div>', unsafe_allow_html=True)
        for a in alerts:
            st.warning(a)
    else:
        st.markdown('<div class="status-badge safe" style="margin-bottom:16px;">✅ Критических скоплений нет</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    ch1, ch2 = st.columns(2, gap="large")

    with ch1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_pie = px.pie(
            df, names="Category", hole=0.55,
            color_discrete_sequence=["#00A67E", "#00B4D8", "#F59E0B", "#EF4444", "#8B5CF6"],
            title="Категории жалоб"
        )
        fig_pie.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1A1F2E", family="Inter"),
            legend=dict(font=dict(size=12)),
            title=dict(font=dict(size=16, color="#1A1F2E")),
            margin=dict(t=50, b=20, l=20, r=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with ch2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_bar = px.bar(
            df, x="Category", color="Urgency",
            color_discrete_map={"Красный": "#EF4444", "Желтый": "#F59E0B", "Зеленый": "#10B981"},
            title="Срочность по категориям"
        )
        fig_bar.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1A1F2E", family="Inter"),
            xaxis=dict(showgrid=False, color="#6B7280"),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", color="#6B7280"),
            legend=dict(font=dict(size=12)),
            title=dict(font=dict(size=16, color="#1A1F2E")),
            margin=dict(t=50, b=20, l=20, r=20),
            bargap=0.3
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with st.expander("📂 Просмотр данных"):
        st.dataframe(df, use_container_width=True)

# ═══════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════
def show_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding:16px 0 8px;">
            <span style="font-size:1.6rem; font-weight:800;">
                <span style="background: linear-gradient(135deg, #00A67E, #00B4D8);
                             -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                    CityFix
                </span> AI
            </span>
            <div style="color:#6B7280; font-size:0.75rem; margin-top:4px;">Almaty Smart City Monitor</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("🏠  На главную", use_container_width=True):
            go_to("Landing")

        st.divider()

        sel = st.radio(
            "НАВИГАЦИЯ",
            ["📍  Карта и Жалобы", "📊  Аналитика"],
            index=0 if st.session_state.current_page == "Map" else 1
        )

        if sel == "📍  Карта и Жалобы" and st.session_state.current_page != "Map":
            go_to("Map")
        elif sel == "📊  Аналитика" and st.session_state.current_page != "Analytics":
            go_to("Analytics")

        st.markdown("""
        <div style="position:fixed; bottom:20px; left:20px; right:20px;
                    color:#9CA3AF; font-size:0.7rem; text-align:center;">
            CityFix AI v3.5 · Almaty 2026
        </div>
        """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# ROUTER
# ═══════════════════════════════════════════════════════
if st.session_state.current_page == "Landing":
    show_landing()
else:
    show_sidebar()
    if st.session_state.current_page == "Map":
        show_map()
    elif st.session_state.current_page == "Analytics":
        show_analytics()
