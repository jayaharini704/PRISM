import streamlit as st

st.set_page_config(
    page_title="PRISM — Indian Cinema Intelligence",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.sidebar.markdown("# 🎬")

st.sidebar.title("PRISM")
st.sidebar.caption(
    "AI-Powered Indian Cinema Intelligence"
)
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Navigate:**
- 🏠 Home — Overview & insights
- 🔍 Vibe Search — Find your next film
- 🤖 AI Analyst — Ask anything
""")
st.sidebar.markdown("---")
st.sidebar.markdown("""
**Dataset:**
- 288 Indian films
- 5 languages
- 1987 — 2026
- Powered by TMDB & Groq LLaMA 3.3
""")

st.title("🎬 PRISM")
st.subheader("AI-Powered Indian Cinema Intelligence Platform")
st.markdown("""
Welcome to PRISM — your intelligent guide to Indian cinema.
Discover hidden gems, explore trends, and find your next 
favourite film using natural language.
""")

st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🎬 Films Analysed", "288")
with col2:
    st.metric("⭐ Avg Rating", "6.88 / 10")
with col3:
    st.metric("💎 Hidden Gems", "34")
with col4:
    st.metric("🗓️ Years Covered", "1987 — 2026")

st.markdown("---")

st.subheader("📊 Key Insights From The Data")

col1, col2 = st.columns(2)

with col1:
    st.info("""
    **🎭 The Quality Paradox**
    
    Action dominates Indian cinema — 43% of all films.
    Yet Drama consistently rates highest at 7.24/10
    vs Action's 6.59/10.
    
    India mass produces its lowest quality genre.
    """)

    st.success("""
    **💎 Hidden Gems Are Mostly Drama**
    
    11 Drama and 8 Comedy hidden gems vs
    only 7 Action hidden gems — despite Action
    dominating production.
    """)

with col2:
    st.warning("""
    **📉 The OTT Runtime Drop**
    
    Indian cinema peaked at 172 min average
    in the 2000s, then dropped sharply to
    152 min in the 2010s as OTT platforms
    pushed for shorter content.
    """)

    st.error("""
    **📊 Popularity Means Nothing**
    
    Correlation between popularity and rating: -0.001
    
    The most watched Indian films are no better
    or worse than unknown ones. Viral ≠ Good.
    """)

st.markdown("---")


st.subheader("🚀 Get Started")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🔍 Vibe Search
    Find films using natural language.
    
    Try: *"Tamil Action 3 hours"*
    or *"Hindi feel good sports movie"*
    
    👈 Click **Vibe Search** in the sidebar
    """)

with col2:
    st.markdown("""
    ### 🤖 AI Analyst
    Ask anything about Indian cinema.
    
    Try: *"Which genre rates highest?"*
    or *"Tell me about Malayalam hidden gems"*
    
    👈 Click **AI Analyst** in the sidebar
    """)