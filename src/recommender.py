import os
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

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
GROQ_API_KEY = get_secret("GROQ_API_KEY")
GROQ_MODEL = get_secret("GROQ_MODEL") or "llama-3.3-70b-versatile"
DB_URL = get_secret("DB_URL")

PROCESSED_DATA_PATH=Path("data/processed")

client=Groq(api_key=GROQ_API_KEY)

def load_movies():
    json_path=PROCESSED_DATA_PATH/"indian_movies_clean.json"
    df=pd.read_json(json_path,orient="records")
    return df

def parse_user_input(user_input):
    system_prompt="""
You are a movie search parameter extractor for Indian Cinema.
Extract search parameters from the user's natural language input.

Return ONLY  a valid JSON object with these exact keys:
{
    "language":null or one of ["Hindi", "Tamil", "Telugu", "Malayalam", "Kannada"],
    "genres":[] or or list from ["Action", "Adventure", "Animation", "Comedy", "Crime", 
               "Documentary", "Drama", "Family", "Fantasy", "History", "Horror", 
               "Music", "Mystery", "Romance", "Science Fiction", "Thriller", "War"],
    "themes":[] or list of theme keywords the user mentioned,
    "runtime_category":null or one of ["Short","Medium","Long","Very Long"],
    "runtime_min":null or integer minutes,
    "runtime_max":null or integer minutes,
    "min_rating":null or float between 0-10,
    "mood":null or one of ["light","dark","feel-good","intense","emotional"],
    "decade":null or one of [1980,1990,2000,2010,2020]
}

Rules:
-"2 hours" or "2 hr" means runtime_min=100,runtime_max=130
-"short" means runtime_category="Short" (under 90 mins)
-"under 90 mins" means runtime_max=90
-"magic","vampire","ghost","witch" -> themes=["magic"/"supernatural"] AND genres=["Fantasy","Horror"]
-"aliens","space","future" -> themes=["sci-fi"] AND genres=["Science Fiction"]
-"sports","athlete","cricket","fottball" -> themes=["sports"]
-"fashion","makeup","modelling" -> themes=["fashion/glamour"]
-"feel-good","light","fun"-> mood="light"
-"dark","intense","serious","thriller"-> mood="dark"
-"good movies only" or "highly rated" -> min_rating=7.5
-If user mentions a movie name, extract it's language/genre as hints only
-return null for any field not mentioned
-return only the json object , no explanation,no markdown,no code block, no comments
"""

    try:
        response=client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role":"system","content":system_prompt},
                {"role":"user","content":user_input}
            ],
            temperature=0,
            max_tokens=500
        )

        raw=response.choices[0].message.content.strip()

        raw=raw.replace("```json","").replace("```","").strip()

        params=json.loads(raw)
        print(f"Parsed Parameters : {params}")
        return params
    
    except json.JSONDecodeError as e:
        print(f"JSON parsing failed : {e}")
        print(f"raw response : {raw}")
        return {}
    
    except Exception as e:
        print(f"LLM parsing failed : {e}")
        return {}

def filter_movies(df,params):
    filtered=df.copy()

    #Language Filter
    if params.get("language"):
        filtered=filtered[filtered["language_name"]==params["language"]]
        print(f" After Language Filter : {len(filtered)} movies")

    #Genre Filter
    if params.get("genres") and len(params["genres"]) > 0:
        genre_mask = filtered["genre_string"].apply(
            lambda x: any(
                genre.lower() in str(x).lower()
                for genre in params["genres"]
            )
        )
        filtered_by_genre = filtered[genre_mask]
        
        if len(filtered_by_genre) >= 1:
            filtered = filtered_by_genre
            print(f"   After genre filter: {len(filtered)} movies")
        else:
            print(f"   No genre matches — genre is a hard requirement")
            filtered = filtered_by_genre

    #Theme Filter
    if params.get("themes") and len(params["themes"])>0:
        theme_mask=filtered.apply(
            lambda row: any(
                theme.lower() in str(row["keywords_str"]).lower() or
                theme.lower() in str(row["overview"]).lower()
                for theme in params["themes"]
            ),
            axis=1
        )
        if theme_mask.sum()>=3:
            filtered=filtered[theme_mask]
            print(f" After Theme Filter : {len(filtered)} movies")   
        else:
            print("The filter is too strict - relaxing") 

    #Runtime Category filter
    if params.get("runtime_category"):
        filtered=filtered[filtered["runtime_category"]==params["runtime_category"]]
        print(f" After Runtime Category filter : {len(filtered)} movies")

    #Runtime Range Filter
    if params.get("runtime_min"):
        filtered=filtered[filtered["runtime"] >= params["runtime_min"]]
    if params.get("runtime_max"):
        filtered=filtered[filtered["runtime"] <= params["runtime_max"]]
    if params.get("runtime_min") or params.get("runtime_max"):
        print(f" After Runtime Range Filter : {len(filtered)} movies")

    # Minimum rating filter
    if params.get("min_rating"):
        filtered = filtered[
            filtered["vote_average"] >= params["min_rating"]
        ]
        print(f"   After rating filter: {len(filtered)} movies")

    # Decade filter
    if params.get("decade"):
        filtered = filtered[
            filtered["decade"] == params["decade"]
        ]
        print(f"   After decade filter: {len(filtered)} movies")

     # Fallback — if nothing matches return top rated
    if len(filtered) == 0:
        print("   ⚠️ No exact matches — relaxing to language only")
        # Try language only as fallback
        if params.get("language"):
            filtered = df[
                df["language_name"] == params["language"]
            ].nlargest(10, "vote_average")
        # If still empty show top rated overall
        if len(filtered) == 0:
            filtered = df.nlargest(10, "vote_average")

    return filtered


def generate_recommendations(user_input,params,filtered_df):
    if filtered_df.empty:
        print("No movies found matching your criteria")
    top_movies=filtered_df.nlargest(5,"vote_average")

    movies_context=[]
    for _,movie in top_movies.iterrows():
        movies_context.append({
            "title":movie["title"],
            "language":movie["language_name"],
            "year": int(movie["release_year"]),
            "rating":float(movie["vote_average"]),
            "runtime":int(movie["runtime"]),
            "genres":movie["genre_string"],
            "overview":movie["overview"][:200],
            "keywords":movie["keywords_str"][:100]
        })

    system_prompt=system_prompt = """
You are PRISM — an Indian cinema recommendation expert.
Write warm, knowledgeable recommendations for each movie.

IMPORTANT HONESTY RULES:
- Only recommend a movie if it GENUINELY matches the user's request
- If a movie does NOT match — wrong genre, wrong theme, wrong language
  — say so honestly. Do not invent reasons it matches.
- Never call a horror film a comedy
- Never call a drama an action film
- If none of the movies match well say clearly:
  "I couldn't find an exact match — here are the closest options"
- Suggest the user broaden their search if no good matches exist

Format each recommendation exactly like this:

🎬 [Movie Title] ([Year]) — [Language]
⭐ Rating: [X.X]/10 | ⏱️ Runtime: [X] min
Why you'll love it: [2-3 honest sentences. Only recommend if 
it genuinely matches. If it does not match say so clearly.]

Keep tone conversational. Only use information provided.
Do not make up plot details or themes.
"""

    user_message = f"""
User searched for: "{user_input}"

Here are the matching movies:
{json.dumps(movies_context, ensure_ascii=False, indent=2)}

Write personalised recommendations for each movie 
explaining why it matches what the user is looking for.
"""
    
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        
        return response.choices[0].message.content
    
    except Exception as e:
        print(f"❌ Recommendation generation failed: {e}")
        # Fallback — return basic info without LLM
        result = []
        for _, movie in top_movies.iterrows():
            result.append(
                f"🎬 {movie['title']} ({int(movie['release_year'])}) "
                f"— {movie['language_name']}\n"
                f"⭐ {movie['vote_average']}/10 | "
                f"⏱️ {movie['runtime']} min\n"
            )
        return "\n".join(result)

def vibe_search(user_input):
    print(f"Vibe search of user input : {user_input}")
    print("=" * 40)

    df=load_movies()

    print("\n🤖 Parsing your request...")
    params = parse_user_input(user_input)
    
    if not params:
        return {
            "movies": [],
            "recommendations": "Sorry, I couldn't understand your search. Try something like 'Tamil comedy 2 hours' or 'Hindi drama with romance'.",
            "params": {}
        }
    
    # Step 3 — Filter movies
    print("\n🎬 Finding matching movies...")
    filtered = filter_movies(df, params)
    
    # Step 4 — Generate recommendations
    top_5 = filtered.nlargest(5, "vote_average")

    # Generate recommendations from the same top 5
    print("\n✍️ Generating recommendations...")
    recommendations = generate_recommendations(
        user_input, params, top_5
    )
    
    # Step 5 — Prepare results
    top_5 = filtered.nlargest(5, "vote_average")
    
    results = {
        "movies": top_5[[
            "id", "title", "language_name", "primary_genre",
            "genre_string", "release_year", "vote_average",
            "runtime", "runtime_category", "overview",
            "keywords_str", "poster_url", "is_hidden_gem"
        ]].to_dict(orient="records"),
        "recommendations": recommendations,
        "params": params,
        "total_matches": len(filtered)
    }
    
    return results


if __name__ == "__main__":
    print("🎬 PRISM — Vibe Search Engine")
    print("=" * 40)
    
    # Test with different vibe inputs
    test_queries = [
        "Tamil comedy with magic 2 hours",
        "Hindi feel good movie with sports",
        "short Malayalam thriller",
        "Telugu action blockbuster highly rated",
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        result = vibe_search(query)
        
        print(f"\n📊 Found {result['total_matches']} matches")
        print(f"\n🎬 Top recommendations:")
        print(result["recommendations"])
        print(f"\n📋 Movie data (first result):")
        if result["movies"]:
            first = result["movies"][0]
            print(f"   {first['title']} ({first['release_year']})")
            print(f"   {first['vote_average']}/10 | {first['runtime']} min")
        
        import time
        time.sleep(2)
