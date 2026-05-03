import pandas as pd
import numpy as np
import json 
import os
import requests 
from pathlib import Path
from dotenv import load_dotenv
import time

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

headers={
    "Authorization":f"Bearer {TMDB_TOKEN}",
    "Content-Type":"application/json"
}

GENRE_MAP={
    28:"Action",
    12:"Adventure",
    16:"Animation",
    35:"Comedy",
    80:"Crime",
    99:"Documentary",
    18:"Drama",
    10751:"Family",
    14:"Fantasy",
    36:"History",
    27:"Horror",
    10402:"Music",
    9648:"Mystery",
    10749:"Romance",
    878:"Science Fiction",
    10770:"TV Movie",
    53:"Thriller",
    10752:"War",
    37:"Western"
}

RAW_DATA_PATH=Path("data/raw")
PROCESSED_DATA_PATH=Path("data/processed")
PROCESSED_DATA_PATH.mkdir(parents=True, exist_ok=True)

def fetch_movie_details(movie_id):
    url=f"{base_url}/movie/{movie_id}"
    params={
        "append_to_response":"keywords"
    }
    try:
        response=requests.get(url,headers=headers,params=params)
        response.raise_for_status()
        data=response.json()
        runtime=data.get("runtime",None)
        keywords_data=data.get("keywords",{})
        keywords_list=keywords_data.get("keywords",[])
        keywords=[k["name"] for k in keywords_list]
        return {
            "runtime":runtime,
            "keywords":keywords
        }
        
    except requests.exceptions.RequestException as e:
        print(f"Error fetching details for movie ID {movie_id}: {e}")
        return {
            "runtime":None,
            "keywords":[]
        }   

def load_and_enrich_raw_data():
    raw_path = RAW_DATA_PATH/"indian_movies_raw.json"
    with open(raw_path,"r",encoding="utf-8") as f:
        movies=json.load(f)
    print(f"Loaded {len(movies)} movies from raw data.")
    print("Fetching runtime and keywords for each movies")
    print("This may take a few mintues - one API call per movie.")

    for i,movie in enumerate(movies):
        details=fetch_movie_details(movie["id"])
        movie["runtime"]=details["runtime"]
        movie["keywords"]=details["keywords"]

        if(i+1)%10==0:
            print(f"Processed {i+1}/{len(movies)} movies", end="\r")

        time.sleep(0.25)

    print(f"\n✅ Enriched all {len(movies)} movies with runtime and keywords.")
    return movies

def clean_movies(movies):
    print("Cleaning started")
    df=pd.DataFrame(movies)
    print(f"Shape of Dataframe : {df.shape}")

    columns_to_keep = [
        "id", "title", "original_title", "overview",
        "original_language", "language_name",
        "release_date", "popularity", "vote_average",
        "vote_count", "poster_path", "runtime",
        "genre_ids", "keywords"
    ]

    df=df[columns_to_keep]

    df["release_date"]=pd.to_datetime(df["release_date"],errors="coerce")

    df["release_year"]=df["release_date"].dt.year

    df["decade"]=(df["release_year"]//10*10)

    def map_genres(genre_ids):
        if not isinstance(genre_ids,list):
            return []
        return [GENRE_MAP.get(gid,"Unknown") for gid in genre_ids]
    
    df["genres"]=df["genre_ids"].apply(map_genres)

    df["primary_genre"]=df["genres"].apply(lambda x:x[0] if x else "Unknown")

    df["genre_string"]=df["genres"].apply(lambda x: ", ".join(x) if x else "Unknown")

    #handling missing values un runtime and overview columns
    median_runtime=df["runtime"].median()
    df["runtime"]=df["runtime"].fillna(median_runtime)
    df["runtime"]=df["runtime"].astype(int)

    df["overview"]=df["overview"].fillna("")

    #runtime categories

    def categorise_runtime(minutes):
        if minutes<=90:
            return "Short"
        elif minutes<=120:
            return "Medium"
        elif minutes<=150:
            return "Long"
        else:
            return "Very Long"

    df["runtime_category"]=df["runtime"].apply(categorise_runtime)

    #hidden gem criteria
    df["is_hidden_gem"] = (
        (df["vote_average"] >= 7.5) &
        (df["popularity"] < 30) &
        (df["vote_count"] >= 100)
    )

    df["poster_url"] = df["poster_path"].apply(
        lambda x: f"https://image.tmdb.org/t/p/w500{x}"
        if pd.notna(x) else None
    )

    df["keywords_str"]=df["keywords"].apply(lambda x: ", ".join(x) if isinstance(x,list) else "")

    #Remove Duplicates
    before=len(df)
    df=df.drop_duplicates(subset=["id"])
    after=len(df)
    print(f"Removed {before-after} duplicate movies based on ID.")

    #Filter Quality threshold 
    df=df[df["overview"].str.len()>10]
    df=df[df["runtime"]>0]

    final_columns = [
        "id", "title", "original_title", "overview",
        "language_name", "release_date", "release_year",
        "decade", "popularity", "vote_average", "vote_count",
        "runtime", "runtime_category", "primary_genre",
        "genre_string", "keywords_str", "poster_url",
        "is_hidden_gem"
    ]
    df = df[final_columns]
    print(f"Final columns: {len(df.columns)}")
    
    return df

def save_processed_data(df):
    csv_path=PROCESSED_DATA_PATH / "indian_movies_clean.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig", quoting=1)
    print(f"Saved CSV : {csv_path}")

    json_path=PROCESSED_DATA_PATH / "indian_movies_clean.json"
    df_json=df.copy()
    df_json.to_json(json_path,orient="records",force_ascii=False,indent=2,date_format="iso")
    print(f"Saved JSON : {json_path}")

    return csv_path,json_path

def load_processed_data():
    csv_path=PROCESSED_DATA_PATH/"indian_movies_clean.csv"
    if not csv_path.exists():
        print(f"Processed CSV not found . Run clean_movies() first.")
        return None
    df=pd.read_csv(csv_path,encoding="utf-8-sig")

    print(f"Loaded processed data from {csv_path} with shape {df.shape}")

if __name__ == "__main__":
    print("🧹 PRISM — Cleaning Movie Data")
    print("=" * 40)
    
    # Step 1 — Load raw data and enrich with details
    movies = load_and_enrich_raw_data()
    
    if not movies:
        print("❌ No raw data found. Run fetch_data.py first.")
        exit()
    
    # Step 2 — Clean the data
    df = clean_movies(movies)
    
    # Step 3 — Show summary statistics
    print("\n📊 Data Summary:")
    print(f"   Total movies: {len(df)}")
    print(f"   Languages: {df['language_name'].value_counts().to_dict()}")
    print(f"   Year range: {df['release_year'].min()} - {df['release_year'].max()}")
    print(f"   Avg rating: {df['vote_average'].mean():.2f}")
    print(f"   Hidden gems: {df['is_hidden_gem'].sum()}")
    print(f"   Runtime categories:\n{df['runtime_category'].value_counts()}")
    
    # Step 4 — Save
    save_processed_data(df)
    
    # Step 5 — Show sample cleaned movie
    print("\n🎬 Sample cleaned movie:")
    sample = df.iloc[0]
    print(f"   Title:     {sample['title']}")
    print(f"   Language:  {sample['language_name']}")
    print(f"   Year:      {sample['release_year']}")
    print(f"   Genres:    {sample['genre_string']}")
    print(f"   Runtime:   {sample['runtime']} min ({sample['runtime_category']})")
    print(f"   Rating:    {sample['vote_average']}")
    print(f"   Hidden:    {sample['is_hidden_gem']}")
    print(f"   Keywords:  {sample['keywords_str'][:100]}")















        


