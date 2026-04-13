import streamlit as st
import pandas as pd
import plotly.express as px
import folium
import os
from dotenv import load_dotenv
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Load environment variables
load_dotenv()

st.set_page_config(page_title="Disaster Response AI", page_icon="🚨", layout="wide")

st.title("🚨 Disaster Response AI Dashboard")
st.markdown("Real-time disaster detection from social media, news, and satellite imagery")

# Sidebar
st.sidebar.header("Data Sources")
refresh_posts = st.sidebar.button("🔄 Refresh Posts Data")

refresh_news = st.sidebar.button("🔄 Refresh News Data")

# Load sample data
@st.cache_data
def load_data():
    try:
        tweets_df = pd.read_csv('data/tweets_classified.csv')
        news_df = pd.read_csv('data/news.csv')
    except FileNotFoundError:
        # Create sample data if files don't exist
        st.warning("Sample data loaded - run fetch scripts for real data")
        tweets_df = pd.read_csv('data/sample_tweets.csv')
        # Add missing columns to sample_tweets for compatibility
        if 'is_disaster' not in tweets_df.columns:
            tweets_df['is_disaster'] = [1,1,0,1,1,0,1,0,1,0]
        if 'confidence' not in tweets_df.columns:
            tweets_df['confidence'] = [0.92,0.88,0.95,0.91,0.89,0.97,0.94,0.96,0.93,0.98]
        if 'location' not in tweets_df.columns:
            tweets_df['location'] = tweets_df.get('location', ['Miami, FL','Los Angeles, CA','New York, NY','Sydney, Australia','Houston, TX','Las Vegas, NV','Florida Keys','Chicago, IL','Oklahoma City','Miami Beach, FL'])
        news_df = pd.read_csv('data/sample_news.csv')
        # Ensure severity column exists
        if 'severity' not in news_df.columns:
            news_df['severity'] = [0.85,0.92,0.88,0.95,0.82]
    return tweets_df, news_df

tweets_df, news_df = load_data()

# Metrics Row
col1, col2, col3, col4 = st.columns(4)
total_tweets = len(tweets_df)
disaster_tweets = len(tweets_df[tweets_df['is_disaster'] == 1])
total_news = len(news_df)
high_severity = len(news_df[news_df['severity'] > 0.7]) if 'severity' in news_df.columns else 0

with col1:
    st.metric("Total Posts", total_tweets)

with col2:
    st.metric("Disaster Posts", disaster_tweets, delta=f"{disaster_tweets/total_tweets*100:.1f}%")

with col3:
    st.metric("News Articles", total_news)
with col4:
    st.metric("High Severity Alerts", high_severity)

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📱 Posts", "📰 News", "🗺️ Map", "📊 Analytics"])

with tab1:
    st.subheader("Classified Disaster Posts")

    if not tweets_df.empty:
        st.dataframe(tweets_df[['text', 'is_disaster', 'confidence', 'location']].head(20), 
                    width="stretch")
        
        # Sentiment distribution
        fig = px.pie(tweets_df, names='is_disaster', 
                    title='Disaster vs Non-Disaster Posts',

                    color_discrete_map={0: 'green', 1: 'red'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No post data available. Run `python scripts/fetch_posts.py` and `process_posts.py`")


with tab2:
    st.subheader("Latest Disaster News")
    if not news_df.empty:
        st.dataframe(news_df[['title', 'description', 'url', 'publishedAt']].head(10), 
                    use_container_width=True)
    else:
        st.info("No news data available. Run `python scripts/fetch_news.py`")

with tab3:
    st.subheader("Disaster Locations Map")
    # Sample disaster locations
    disaster_locations = [
        {"lat": 40.7128, "lon": -74.0060, "name": "NY Floods", "severity": 0.8},
        {"lat": 34.0522, "lon": -118.2437, "name": "LA Fires", "severity": 0.9},
        {"lat": 41.8781, "lon": -87.6298, "name": "Chicago Storm", "severity": 0.7}
    ]
    
    m = folium.Map(location=[39.8283, -98.5795], zoom_start=4)
    
    for loc in disaster_locations:
        folium.CircleMarker(
            location=[loc["lat"], loc["lon"]],
            radius=loc["severity"]*15,
            popup=f"{loc['name']}<br>Severity: {loc['severity']}",
            color='red' if loc["severity"] > 0.7 else 'orange',
            fill=True,
            fillColor='red' if loc["severity"] > 0.7 else 'orange'
        ).add_to(m)
    
    st.components.v1.html(m._repr_html_(), height=500)

with tab4:
    st.subheader("Disaster Analytics")
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Disaster Types', 'Severity Distribution', 'Tweet Volume', 'News Trends'),
        specs=[[{"type": "pie"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # Disaster types pie
    disaster_types = ['Floods', 'Fires', 'Earthquakes', 'Storms']
    counts = [25, 20, 15, 40]
    fig.add_trace(go.Pie(labels=disaster_types, values=counts, name="Types"), row=1, col=1)
    
    # Severity bar
    severities = ['Low', 'Medium', 'High', 'Critical']
    values = [10, 25, 40, 25]
    fig.add_trace(go.Bar(x=severities, y=values, name="Severity"), row=1, col=2)
    
    # Tweet volume
    fig.add_trace(go.Bar(x=['24h', '7d', '30d'], y=[150, 800, 2500], name="Tweets"), row=2, col=1)
    
    # News trend
    fig.add_trace(go.Scatter(x=['Mon', 'Tue', 'Wed', 'Thu', 'Fri'], 
                           y=[5, 12, 8, 20, 15], mode='lines+markers', name="News"), row=2, col=2)
    
    fig.update_layout(height=600, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**Built with Streamlit, NLP, and ML** | Refresh data using sidebar buttons")
