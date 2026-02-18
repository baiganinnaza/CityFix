
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import HeatMap, MarkerCluster
import plotly.express as px
import plotly.graph_objects as go
import os
import sys

# Ensure project root is in path for backend imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend import logic

# --- UI Helper ---

def render_template(template_name, **kwargs):
    """
    Loads an HTML template and injects variables.
    
    Args:
        template_name (str): Name of the file in frontend/templates/ (without extension).
        **kwargs: Variables to inject into the template using {{ variable }} syntax.
    """
    template_path = os.path.join(os.path.dirname(__file__), "templates", f"{template_name}.html")
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            template = f.read()
        for key, value in kwargs.items():
            template = template.replace(f"{{{{ {key} }}}}", str(value))
        st.markdown(template, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error loading template {template_name}: {e}")

# --- Page Configuration ---

st.set_page_config(
    page_title="CityFix Almaty",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Global Styles
css_path = os.path.join(os.path.dirname(__file__), "index.css")
with open(css_path, "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --- Application State ---

if "complaints_data" not in st.session_state:
    data = [
        {"Text": "Огромная яма на аль-Фараби, пробил колесо!", "Lat": 43.2031, "Lon": 76.9056, "Category": "Дороги", "Urgency": "Красный", "Urgency_Level": 3},
        {"Text": "Не горит фонарь возле школы №15", "Lat": 43.2301, "Lon": 76.9456, "Category": "Свет", "Urgency": "Желтый", "Urgency_Level": 2},
        {"Text": "Мусор не вывозят уже неделю, запах ужасный", "Lat": 43.2567, "Lon": 76.9286, "Category": "ЖКХ", "Urgency": "Красный", "Urgency_Level": 3},
        {"Text": "Открытый люк на тротуаре, очень опасно!", "Lat": 43.2422, "Lon": 76.8912, "Category": "Опасность", "Urgency": "Красный", "Urgency_Level": 3},
        {"Text": "Сломана скамейка в парке 28 панфиловцев", "Lat": 43.2593, "Lon": 76.9567, "Category": "Другое", "Urgency": "Зеленый", "Urgency_Level": 1},
        {"Text": "Прорвало трубу с горячей водой", "Lat": 43.2150, "Lon": 76.8800, "Category": "ЖКХ", "Urgency": "Желтый", "Urgency_Level": 2},
    ]
    st.session_state.complaints_data = pd.DataFrame(data)

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

df = st.session_state.complaints_data

def go_to(page):
    st.session_state.current_page = page
    st.rerun()

# --- Page Views ---

def show_landing():
    render_template("landing_hero")
    
    col_cta1, col_cta2 = st.columns([1, 1])
    with col_cta1:
        if st.button("Launch System Map", use_container_width=True, type="primary"):
            go_to("Map")
    with col_cta2:
        if st.button("Analytics Hub", use_container_width=True):
            go_to("Analytics")

    st.markdown("<br>", unsafe_allow_html=True)
    render_template("feature_grid")
    st.markdown("<br>", unsafe_allow_html=True)
    
    s1, s2, s3 = st.columns(3)
    with s1:
        render_template("card_header", title="Reports Processed", subtitle=f"Total: {len(df)}")
    with s2:
        render_template("card_header", title="Categories", subtitle="Managed: 5")
    with s3:
        render_template("card_header", title="Engine", subtitle="Type: LLM API")

def show_map():
    render_template("page_header", 
                    icon="📍", 
                    title="Issue Map", 
                    subtitle="Click on the map to mark a new issue location")

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
            for _, row in df.iterrows():
                folium.Marker(
                    [row["Lat"], row["Lon"]],
                    popup=folium.Popup(f"<b>{row['Category']}</b><br><span style='color:#6B7280'>{row['Text']}</span>", max_width=280),
                    tooltip=f"{row['Urgency']}",
                    icon=folium.Icon(color=color_map.get(row["Urgency"], "blue"), prefix="fa")
                ).add_to(cluster)

        alerts = logic.check_red_zones(df)
        if alerts:
            st.markdown(f'<div class="status-badge danger">🚨 {len(alerts)} critical zones detected</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-badge safe">✅ No critical zones nearby</div>', unsafe_allow_html=True)

        map_output = st_folium(m, width="100%", height=550, returned_objects=["last_clicked"])

    with col_form:
        render_template("card_header", title="Submit Report", subtitle="Describe the urban infrastructure problem")

        with st.form("complaint_form"):
            new_text = st.text_area("Description", height=120, placeholder="Example: Broken traffic light at Abay...")
            
            clicked_lat = logic.ALMATY_LAT
            clicked_lon = logic.ALMATY_LON
            if map_output and map_output.get("last_clicked"):
                clicked_lat = map_output["last_clicked"]["lat"]
                clicked_lon = map_output["last_clicked"]["lng"]

            render_template("coordinates_display", lat=f"{clicked_lat:.4f}", lon=f"{clicked_lon:.4f}")

            if st.form_submit_button("Send Report", use_container_width=True, type="primary"):
                if not new_text:
                    st.warning("Please provide a description.")
                else:
                    with st.spinner("Analyzing with AI..."):
                        result = logic.classify_complaint(new_text)
                        if result["Is_Valid"]:
                            new_rec = {"Text": new_text, "Lat": clicked_lat, "Lon": clicked_lon, **result}
                            st.session_state.complaints_data = pd.concat(
                                [st.session_state.complaints_data, pd.DataFrame([new_rec])],
                                ignore_index=True)
                            st.success("Report submitted!")
                            st.rerun()
                        else:
                            st.error(f"Rejected: {result['Reason']}")

def show_analytics():
    render_template("analytics_summary")
    
    if df.empty:
        st.info("No data available for analysis.")
        return

    with st.expander("🔍 Filter Analytics Data", expanded=False):
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            categories = st.multiselect("Filter by Category", df["Category"].unique(), default=df["Category"].unique())
        with f_col2:
            urgencies = st.multiselect("Filter by Urgency", df["Urgency"].unique(), default=df["Urgency"].unique())
        
        filtered_df = df[df["Category"].isin(categories) & df["Urgency"].isin(urgencies)]

    if filtered_df.empty:
        st.warning("No data matches the selected filters.")
        return

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        render_template("card_header", title="Scope", subtitle=f"{len(filtered_df)} Items")
    with c2:
        render_template("card_header", title="Critical", subtitle=len(filtered_df[filtered_df["Urgency"] == "Красный"]))
    with c3:
        render_template("card_header", title="Warning", subtitle=len(filtered_df[filtered_df["Urgency"] == "Желтый"]))
    with c4:
        render_template("card_header", title="Normal", subtitle=len(filtered_df[filtered_df["Urgency"] == "Зеленый"]))

    st.markdown("<br>", unsafe_allow_html=True)

    ch1, ch2 = st.columns(2)
    
    with ch1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_tree = px.treemap(
            filtered_df, 
            path=['Category', 'Urgency'],
            color='Urgency_Level',
            color_continuous_scale='RdYlGn_r',
            title="Density Analysis (Category > Urgency)"
        )
        fig_tree.update_layout(
            margin=dict(t=50, l=10, r=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter")
        )
        st.plotly_chart(fig_tree, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with ch2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        fig_bar = px.bar(
            filtered_df, x="Category", color="Urgency",
            color_discrete_map={"Красный": "#EF4444", "Желтый": "#F59E0B", "Зеленый": "#10B981"},
            title="Volume by Category"
        )
        fig_bar.update_layout(
            margin=dict(t=50, l=10, r=10, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter")
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    render_template("card_header", title="Detailed Records", subtitle="Complete dataset view and export")
    
    st.dataframe(
        filtered_df[["Category", "Urgency", "Text", "Lat", "Lon"]],
        use_container_width=True,
        hide_index=True
    )

    alerts = logic.check_red_zones(df)
    if alerts:
        st.markdown("<br>", unsafe_allow_html=True)
        st.error(f"⚠️ {len(alerts)} High-Risk Cluster(s) Detected in System")
        for a in alerts:
            st.info(a)

# --- Sidebar ---

def show_sidebar():
    with st.sidebar:
        render_template("sidebar_header")
        st.markdown("<br>", unsafe_allow_html=True)
        
        pages = ["Home", "Map & Issues", "Analytics"]
        current_idx = 0
        if st.session_state.current_page == "Map":
            current_idx = 1
        elif st.session_state.current_page == "Analytics":
            current_idx = 2
            
        sel = st.radio("NAVIGATION", pages, index=current_idx)
        
        if sel == "Home" and st.session_state.current_page != "Home":
            go_to("Home")
        elif sel == "Map & Issues" and st.session_state.current_page != "Map":
            go_to("Map")
        elif sel == "Analytics" and st.session_state.current_page != "Analytics":
            go_to("Analytics")
            
        render_template("sidebar_footer")

# --- Routing ---

show_sidebar()

if st.session_state.current_page == "Home":
    show_landing()
elif st.session_state.current_page == "Map":
    show_map()
elif st.session_state.current_page == "Analytics":
    show_analytics()
