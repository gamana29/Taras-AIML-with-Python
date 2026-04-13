import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import os
import subprocess
import joblib
import re
from dotenv import load_dotenv
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Real-time Disaster Response AI", page_icon="⚡", layout="wide")

st.title("⚡ Real-time Disaster Response AI")
st.markdown("**Live Reddit post/news monitoring with instant disaster detection**")

# Global data storage
if 'tweets_df' not in st.session_state:
    st.session_state.tweets_df = pd.DataFrame()
if 'news_df' not in st.session_state:
    st.session_state.news_df = pd.DataFrame()
if 'disaster_alerts' not in st.session_state:
    st.session_state.disaster_alerts = 0
if 'model' not in st.session_state:
    st.session_state.model = None
if 'last_update' not in st.session_state:
    st.session_state.last_update = None

# Load model
@st.cache_resource
def load_model():
    model_path = os.path.join("disaster_ai/models", "disaster_classifier.pkl")
    try:
        model = joblib.load(model_path)
        st.success("✅ ML Model loaded")
        return model
    except:
        st.warning("⚠️ Model not found, using rule-based")
        return None

st.session_state.model = load_model()

data_dir = "disaster_ai/data"

@st.cache_data(ttl=30)
def load_data():
    try:
        tweets_df = pd.read_csv(os.path.join(data_dir, "tweets_classified.csv"))
        news_df = pd.read_csv(os.path.join(data_dir, "news.csv"))
    except:
        tweets_df = pd.read_csv(os.path.join(data_dir, "sample_posts.csv"))
        news_df = pd.read_csv(os.path.join(data_dir, "sample_news.csv"))
    return tweets_df, news_df

def run_script(script):
    with st.spinner(f"Running {script}..."):
        try:
            result = subprocess.run(['python', os.path.join('disaster_ai/scripts', f'{script}.py')], 
                                  cwd='.', capture_output=True, text=True, timeout=30)
            st.success(f"✅ {script} completed")
            st.session_state.last_update = datetime.now().strftime("%H:%M:%S")
            return True
        except:
            st.error(f"❌ {script} failed (check API keys in .env)")
            return False

# Sidebar
st.sidebar.header("🔄 Controls")
if st.sidebar.button("🔥 Fetch Posts"):
    run_script("fetch_posts")
if st.sidebar.button("📰 Fetch News"):
    run_script("fetch_news")
if st.sidebar.button("🤖 Process/ Classify"):
    run_script("process_posts")

st.sidebar.info(f"**Last update:** {st.session_state.last_update or 'Never'}")

# Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Posts", len(st.session_state.tweets_df))
col2.metric("News", len(st.session_state.news_df))
col3.metric("🚨 Alerts", st.session_state.disaster_alerts)

# Load data
st.session_state.tweets_df, st.session_state.news_df = load_data()
st.session_state.disaster_alerts = len(st.session_state.tweets_df[st.session_state.tweets_df.get('is_disaster', 0) == 1])

# Tabs
tab1, tab2, tab3 = st.tabs(["📱 Posts", "📰 News", "🗺️ Map"])

with tab1:
    if not st.session_state.tweets_df.empty:
        disasters = st.session_state.tweets_df[st.session_state.tweets_df.get('is_disaster', 0) == 1].sort_values('confidence', ascending=False)
        st.dataframe(disasters[['text', 'confidence', 'location']].head(10), width="stretch")
        fig = px.pie(st.session_state.tweets_df, names='is_disaster', title='Disaster Ratio', color_discrete_map={0: 'green', 1: 'red'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Click fetch buttons")

with tab2:
    if not st.session_state.news_df.empty:
        st.dataframe(st.session_state.news_df[['title', 'description', 'publishedAt', 'severity']].head(10), width="stretch")

with tab3:
    m = folium.Map(location=[39.8, -98.5], zoom_start=4)
    if not st.session_state.tweets_df.empty:
        disasters = st.session_state.tweets_df[st.session_state.tweets_df.get('is_disaster', 0) == 1].head(20)
        for _, row in disasters.iterrows():
            lat, lon = 39.8, -98.5
            if 'Miami' in str(row.get('location', '')):
                lat, lon = 25.76, -80.19
            folium.CircleMarker([lat, lon], radius=15, popup=row.get('text', '')[:50], color='red').add_to(m)
    st.components.v1.html(m._repr_html_(), height=500)

st.markdown("**Live at:** " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

