import pandas as pd
import os
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

def get_secret(key):
    """
    Gets secrets from Streamlit Cloud when deployed,
    falls back to .env when running locally.
    """
    try:
        import streamlit as st
        return st.secrets[key]
    except Exception:
        return os.getenv(key)

TMDB_TOKEN = get_secret("TMDB_TOKEN")
DB_URL = get_secret("DB_URL")

PROCESSED_DATA_PATH=Path("data/processed")

def get_engine():
    if not DB_URL:
        raise ValueError(
            "Database URL not found in .env - add supabase connection string"
        )
    engine=create_engine(
        DB_URL,
        pool_pre_ping=True
    )
    return engine

def create_table(engine):
    sql="""
       CREATE TABLE IF NOT EXISTS movies(
            id INTEGER PRIMARY KEY,
            title TEXT,
            original_title TEXT,
            overview TEXT,
            language_name TEXT,
            release_date DATE,
            release_year INTEGER, 
            decade INTEGER,
            popularity FLOAT,
            vote_average FLOAT,
            vote_count INTEGER,
            runtime INTEGER,
            runtime_category TEXT,
            primary_genre TEXT,
            genre_string TEXT,
            keywords_str TEXT,
            poster_url TEXT,
            is_hidden_gem BOOLEAN
        );
    """

    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print("Database table 'movies' created or already exists.")

def upload_data(df,engine):
    columns_to_upload=[
        "id", "title", "original_title", "overview", "language_name",
        "release_date", "release_year", "decade", "popularity", "vote_average", 
        "vote_count", "runtime", "runtime_category", "primary_genre", "genre_string", 
        "keywords_str", "poster_url", "is_hidden_gem"]
    
    df_upload=df[columns_to_upload].copy()
    
    df_upload["release_date"]=pd.to_datetime(df["release_date"],errors="coerce")
    df_upload["is_hidden_gem"]=df_upload["is_hidden_gem"].astype(bool)

    df_upload.to_sql(
        name="movies",
        con=engine,
        if_exists="replace",
        method="multi",
        chunksize=100,
        index=False
    )

    print(f"Uploaded {len(df_upload)} movies to Supabase.")

def verify_upload(engine):
        
    checks = {
        "Total movies": 
            "SELECT COUNT(*) FROM movies",
        
        "Average rating": 
            "SELECT ROUND(AVG(vote_average)::numeric, 2) FROM movies",
        
        "Movies by language": 
            """SELECT language_name, COUNT(*) as count 
               FROM movies 
               GROUP BY language_name 
               ORDER BY count DESC""",
        
        "Runtime breakdown": 
            """SELECT runtime_category, COUNT(*) as count 
               FROM movies 
               GROUP BY runtime_category 
               ORDER BY count DESC""",
        
        "Hidden gems count": 
            "SELECT COUNT(*) FROM movies WHERE is_hidden_gem = TRUE",

        "Decade breakdown":
            """SELECT decade, COUNT(*) as count
               FROM movies
               GROUP BY decade
               ORDER BY decade ASC"""
    }
    
    print("\n📊 Database Verification:")
    print("=" * 40)

    with engine.connect() as conn:
        for check_name,sql in checks.items():
            result=conn.execute(text(sql))
            rows=result.fetchall()
            print(f"\n{check_name}:")
            for row in rows:
                print(f"  {row}")

if __name__=="__main__":
    print("🗄️  PRISM — Uploading to Database")
    print("=" * 40)

    json_path = PROCESSED_DATA_PATH / "indian_movies_clean.json"

    if not json_path.exists():
        print("❌ Clean data not found. Run clean_data.py first.")
        exit()

    df = pd.read_json(json_path, orient="records")
    print(f"✅ Loaded {len(df)} movies from JSON")
    print(f"   Columns: {list(df.columns)}")

    print("\n🔌 Connecting to Supabase...")
    engine = get_engine()
    print("✅ Connected")

    create_table(engine)

    print("\n⬆️  Uploading data...")
    upload_data(df,engine)

    verify_upload(engine)

    print("\n🎉 Done! Your data is live in Supabase.")
          

    
    