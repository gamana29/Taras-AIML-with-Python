# Disaster Response AI

## Setup Instructions (Windows)

1. **Activate Virtual Environment:**
   ```
   disaster_ai\venv\Scripts\activate
   ```

2. **Install Dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Download NLTK Data:**
   ```
   python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"
   ```

4. **Fetch Data (Optional - requires API keys in .env):**
   ```
   python scripts/fetch_posts.py
   python scripts/fetch_news.py
   python scripts/process_posts.py
   ```


5. **Run Dashboard:**
   ```
   streamlit run app.py
   ```

## Folder Structure
```
disaster_ai/
├── data/           # Sample CSVs and fetched data
├── models/         # ML models
├── scripts/        # Data fetching/processing
├── app.py          # Streamlit dashboard
├── requirements.txt
├── .env            # API keys (copy and fill)
└── README.md
```

## Features
- Real-time Reddit post fetching and disaster classification
- News aggregation
- Interactive dashboard with maps and charts
- Works with sample data out-of-the-box

## API Keys Required
1. [Reddit API](https://www.reddit.com/prefs/apps) 
2. [NewsAPI](https://newsapi.org/)
