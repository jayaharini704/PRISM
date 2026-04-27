import requests
import json
import os
import time
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
TMDB_TOKEN=os.getenv("TMDB_TOKEN")

base_url="https://api.themoviedb.org/3"

HEADERS={
    "Authorization":f"Bearer {TMDB_TOKEN}",
    "Content-Type":"application/json"
}

RAW_DATA_PATH=Path("data/raw")
RAW_DATA_PATH.mkdir(parents=True, exist_ok=True)

INDIAN_LANGUAGES={
    "hi":"Hindi",
    "ta":"Tamil",
    "te":"Telugu",
    "kn":"Kannada",
    "ml":"Malayalam",
}

def fetch_movies_by_language(language_code,page=1):
    url=f"{base_url}/discover/movie"
    params={
        "with_original_language":language_code,
        "page":page,
        "sort_by":"popularity.desc",
        "include_adult":False,
        "vote_count.gte":50
    }

    try:
        response=requests.get(url,params=params,headers=HEADERS)
        response.raise_for_status()
        data=response.json()
        return data.get("results",[])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movies for language {language_code} page {page}: {e}")
        return []

def fetch_all_movies(pages_per_language=10):
    """
    Fetches multiple pages of movies for all Indian languages.
    Total movies = 5 languages × pages × 20 movies per page
    With 10 pages: 5 × 10 × 20 = 1000 movies minimum
    
    Args:
        pages_per_language: how many pages to fetch per language
    
    Returns:
        List of all movies combined
    """
    
    all_movies = []
    
    for language_code, language_name in INDIAN_LANGUAGES.items():
        print(f"\nFetching {language_name} movies...")
        
        for page in range(1, pages_per_language + 1):
            print(f"  Page {page}/{pages_per_language}", end="\r")
            
            # Fetch one page
            movies = fetch_movies_by_language(language_code, page)
            
            if not movies:
                print(f"  No more movies found at page {page}")
                break
            
            # Add language name to each movie
            for movie in movies:
                movie["language_name"] = language_name
            
            # Add to our collection
            all_movies.extend(movies)
            
            # Wait 0.25 seconds between calls
            # This respects TMDB's rate limit
            time.sleep(0.25)
    
    print(f"\n✅ Total movies fetched: {len(all_movies)}")
    return all_movies


def save_raw_data(movies):
    """
    Saves raw movie data as JSON file.
    We save raw data before cleaning so we
    can always go back to the original.
    """
    
    output_path = RAW_DATA_PATH / "indian_movies_raw.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Saved {len(movies)} movies to {output_path}")
    return output_path


def load_raw_data():
    """
    Loads previously saved raw data.
    So you don't have to call the API every time.
    """
    input_path = RAW_DATA_PATH / "indian_movies_raw.json"
    
    if not input_path.exists():
        print("❌ No raw data found. Run fetch_all_movies() first.")
        return []
    
    with open(input_path, "r", encoding="utf-8") as f:
        movies = json.load(f)
    
    print(f"✅ Loaded {len(movies)} movies from {input_path}")
    return movies

if __name__ == "__main__":
    print("🎬 PRISM — Fetching Indian Movie Data")
    print("=" * 40)
    
    # Fetch all movies
    # Start with 5 pages per language = ~500 movies
    # Increase to 20+ later for more data
    movies = fetch_all_movies(pages_per_language=5)
    
    if movies:
        save_raw_data(movies)
        
        # Show a sample movie so you can see what the data looks like
        print("\n📽️ Sample movie data:")
        print(json.dumps(movies[0], indent=2, ensure_ascii=False))
    else:
        print("❌ No movies fetched. Check your TMDB token in .env")


