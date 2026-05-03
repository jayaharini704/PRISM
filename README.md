# 🎬 PRISM — AI-Powered Indian Cinema Intelligence Platform

> Discover hidden gems, explore trends, and find your next favourite Indian film using natural language.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://prism-cineintel-ai.streamlit.app)

---

## 🔗 Live Links

| | Link |
|--|------|
| 🚀 **Live App** | [prism-cineintel-ai.streamlit.app](https://prism-cineintel-ai.streamlit.app) |
| 💻 **Source Code** | [github.com/jayaharini704/PRISM](https://github.com/jayaharini704/PRISM) |
| 📊 **Tableau Dashboard** | Coming soon |

---

## 📌 What Is PRISM?

PRISM is an end-to-end data intelligence platform for Indian cinema. It combines a real-time data pipeline, statistical analysis, and a Groq-hosted LLaMA 3.3 AI layer to answer questions, find films, and surface insights from 288 Indian films across 5 languages spanning 1987–2026.

Built as a portfolio project to demonstrate production-grade data engineering, analytics, and LLM integration skills.

---

## ✨ Features

### 🔍 Vibe Search
Natural language film discovery powered by LLaMA 3.3. Type anything:
- *"Tamil comedy with magic 2 hours"*
- *"Hindi feel good sports movie"*
- *"Short Malayalam thriller highly rated"*

The LLM extracts intent, filters 288 films, and writes personalised recommendations grounded in real data — not hallucinations.

### 🤖 AI Cinema Analyst
Ask anything about Indian cinema:
- *"Which genre has the highest average rating?"*
- *"Tell me about Malayalam hidden gems"*
- *"Has Indian cinema gotten shorter over decades?"*

The AI answers from your actual dataset — a RAG-lite pattern where every insight is backed by real numbers.

### 📊 Analytics Dashboard
Key insights surfaced from the data:
- **The Quality Paradox** — Action dominates production (43%) but rates lowest (6.59/10). Drama rates highest (7.24/10) but is underproduced.
- **The OTT Runtime Drop** — Indian cinema peaked at 172 min average in the 2000s, dropped to 152 min in the 2010s as OTT platforms pushed for shorter content.
- **Malayalam Punches Above Its Weight** — Highest avg rating (7.31) with fewest major-language films (41). Hidden gem rate of 1.46 per 10 films.
- **Popularity Means Nothing** — Correlation between popularity and rating: -0.001. Viral ≠ Good.

### 💎 Hidden Gems
34 hidden gems identified — high quality (7.5+ rating), low visibility (popularity < 30), minimum 100 votes. Mostly Drama and Comedy, rarely Action despite Action dominating production.

---

## 🏗️ Architecture

```
TMDB API (288 Indian films · 5 languages)
         ↓
┌─────────────────────────────────────────┐
│           Data Pipeline                  │
│  fetch_data.py → clean_data.py → analysis.py │
└─────────────────────────────────────────┘
         ↓                    ↓
┌──────────────┐    ┌──────────────────────┐
│   Supabase   │    │ analysis_results.json │
│  PostgreSQL  │    │   (LLM knowledge)     │
└──────────────┘    └──────────────────────┘
      ↓  ↓                    ↓
┌──────────────┐    ┌──────────────────────┐
│recommender.py│    │   llm_insights.py     │
│ Vibe Search  │    │   AI Analyst Chat     │
└──────────────┘    └──────────────────────┘
      ↓                       ↓
              Groq · LLaMA 3.3 70B
                      ↓
┌──────────────────────────────────────────┐
│           Streamlit App                   │
│  Vibe Search · AI Chat · Home Dashboard  │
└──────────────────────────────────────────┘
                      ↓
         prism-cineintel-ai.streamlit.app
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Data Collection** | Python, TMDB API, Requests |
| **Data Processing** | Pandas, NumPy, SciPy |
| **Database** | PostgreSQL (Supabase) |
| **ORM** | SQLAlchemy |
| **AI / LLM** | Groq API, LLaMA 3.3 70B |
| **Frontend** | Streamlit |
| **Visualisation** | Plotly |
| **BI Dashboard** | Tableau Public |
| **Deployment** | Streamlit Cloud |
| **Version Control** | Git, GitHub |

---

## 📊 Dataset

- **Source:** TMDB (The Movie Database) API
- **Size:** 288 Indian films after deduplication
- **Languages:** Hindi (100), Tamil (97), Telugu (42), Malayalam (41), Kannada (8)
- **Year range:** 1987 — 2026
- **Features engineered:** runtime_category, decade, primary_genre, genre_string, keywords_str, is_hidden_gem, poster_url, gem_rate
- **Average rating:** 6.88 / 10
- **Hidden gems:** 34 films

---

## 🔬 Key Technical Decisions

**Why Supabase over local PostgreSQL?**
Supabase provides a free cloud PostgreSQL instance accessible from both local development and Streamlit Cloud deployment without environment-specific configuration. The session pooler connection string handles Streamlit Cloud's serverless connection pattern.

**Why normalise hidden gem counts?**
Raw hidden gem counts are biased by language sample size — Hindi has 17 gems but 100 films vs Malayalam's 6 gems from 41 films. Normalising to gem_rate (gems per 10 films) gives a fair quality comparison: Hindi 1.70, Malayalam 1.46, Tamil 0.82.

**Why temperature=0 for parsing, 0.7 for recommendations?**
Intent extraction requires deterministic output — same input must always produce the same JSON structure. Recommendation writing benefits from creative variation — different phrasings feel more natural to users.

---

## 📁 Project Structure

PRISM/
│
├── data/
│   ├── raw/                    ← raw TMDB API responses
│   └── processed/              ← cleaned CSVs and JSON
│
├── src/
│   ├── fetch_data.py           ← TMDB API data collection
│   ├── clean_data.py           ← cleaning + feature engineering
│   ├── database.py             ← Supabase PostgreSQL upload
│   ├── analysis.py             ← EDA + statistical insights
│   ├── recommender.py          ← vibe search + LLM recommendations
│   └── llm_insights.py         ← AI analyst chat
│
├── streamlit_app/
│   ├── app.py                  ← home page + KPI dashboard
│   └── pages/
│       ├── 01_vibe_search.py   ← vibe search interface
│       └── 02_ai_chat.py       ← AI analyst chat interface
│
├── notebooks/
│   └── exploration.ipynb       ← EDA and prototyping
│
├── .env                        ← secrets (not in repo)
├── requirements.txt
└── README.md

---

## 🚀 Run Locally

```bash
# Clone the repo
git clone https://github.com/jayaharini704/PRISM.git
cd PRISM

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Add your API keys to .env
cp .env.example .env
# Edit .env with your TMDB, Groq, and Supabase credentials

# Run the data pipeline (first time only)
python src/fetch_data.py
python src/clean_data.py
python src/database.py
python src/analysis.py

# Launch the app
streamlit run streamlit_app/app.py
```

---

## 🔑 Environment Variables

Create a `.env` file with:
TMDB_TOKEN=your_tmdb_read_access_token
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
DB_URL=your_supabase_postgresql_connection_string

---

## 📈 Insights Summary

| Insight | Finding |
|---------|---------|
| Most produced genre | Action (125 films, 43%) |
| Highest rated genre | Drama (7.24 avg) |
| Lowest rated genre | Action (6.59 avg) |
| Highest rated language | Malayalam (7.31 avg) |
| Peak runtime decade | 2000s (172 min avg) |
| Current runtime | 2020s (155 min avg) |
| Popularity vs rating correlation | -0.001 (essentially zero) |
| Total hidden gems | 34 films |
| Best hidden gem rate | Hindi (1.70 per 10 films) |
| Highest rated film | DDLJ (8.51) |

---

## 🚀 Roadmap

- [ ] Cast and director analysis — top actors/directors per language
- [ ] Similarity search — "movies like Vikram" with conversational preference refinement
- [ ] Sentence transformer embeddings for semantic similarity
- [ ] Expand dataset to 2000+ films for better vibe search coverage
- [ ] Tableau Public dashboard integration
- [ ] User ratings and watchlist feature

---

## 👩‍💻 Built By

**Jayaharini Srinivasan**
Software Engineer @ Volvo Group | Aspiring Data Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue)](https://www.linkedin.com/in/jayaharini-srinivasan-069aab247)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-black)](https://github.com/jayaharini704)

---

## 📄 Data Attribution

Movie data sourced from [The Movie Database (TMDB)](https://www.themoviedb.org/) API.
This product uses the TMDB API but is not endorsed or certified by TMDB.
