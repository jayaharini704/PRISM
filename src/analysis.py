import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine,text
from dotenv import load_dotenv
from pathlib import Path
from scipy import stats

load_dotenv()

DB_URL=os.getenv("DB_URL")
PROCESSED_DATA_PATH=Path("data/processed")

def get_engine():
    return create_engine(DB_URL,pool_pre_ping=True)

def load_data():
    json_path=PROCESSED_DATA_PATH/"indian_movies_clean.json"
    df=pd.read_json(json_path,orient="records")
    print(f"✅ Loaded {len(df)} movies for analysis")
    return df

def analyse_runtime_trends(df):
    print("\n📊 Analyzing Runtime Trends by decade...")
    print("=" * 40)
    
    runtime_by_decade = df.groupby("decade")["runtime"].agg(
        [
            "mean",
            "median",
            "std",
            "count"
        ])
    
    runtime_by_decade.columns = ["avg_runtime", 
        "median_runtime", 
        "std_runtime", 
        "movie_count"
    ]
    print(runtime_by_decade)

    movies_90s=df[df["decade"]==1990]["runtime"]
    movies_20s=df[df["decade"]==2020]["runtime"]

    if  len(movies_90s)>5 and len(movies_20s)>5:
        t_stat,p_value=stats.ttest_ind(movies_90s,movies_20s)
        print(f"Statistical test 1990 svs 2020s movies runtime")
        print(f"1990s movies average runtime : {movies_90s.mean():.1f} mins")
        print(f"2020s movies average runtime : {movies_20s.mean():.1f} mins")
        print(f"Difference : {movies_90s.mean() - movies_20s.mean():.1f} mins")
        print(f"p-value : {p_value:.4f}")

        if p_value < 0.05:
            print("   ✅ Statistically significant difference")
            print("   The runtime change is REAL, not random")
        else:
            print("   ⚠️ Not statistically significant")
            print("   Could be due to small sample size")
    
    return runtime_by_decade

def analyze_genre_trends(df):
    print("\n📊 Analyzing Genre Trends by decade...")
    print("=" * 40)
    
    genre_decade=df.groupby(["decade","primary_genre"])["id"].count().reset_index()
    genre_decade.columns=["decade","primary_genre","count"]

    top_genre_per_decade = genre_decade.loc[
    genre_decade.groupby("decade")["count"].idxmax()
][["decade", "primary_genre", "count"]]

    print("Dominant Genre per Decade:")
    print(top_genre_per_decade.to_string(index=False))

    overall_genres=df["primary_genre"].value_counts()
    print("\nOverall Genre Distribution:")
    print(overall_genres.to_string())

    genre_ratings=df.groupby("primary_genre")["vote_average"].agg(
        ["mean","count"]
    )

    genre_ratings.columns=["avg_rating","movie_count"]

    genre_ratings=genre_ratings[genre_ratings["movie_count"]>=5].sort_values("avg_rating",ascending=False)

    print("\nGenre ratings (min 5 movies):")
    print(genre_ratings)
    
    return genre_decade, genre_ratings

def analyze_hidden_gems(df):
    print("\n🔍 Analyzing Hidden Gems...")
    print("=" * 40)
    
    gems = df[df["is_hidden_gem"] == True].copy()
    
    print(f"Total hidden gems: {len(gems)}")
    

    gems_by_language = gems["language_name"].value_counts()
    print("\nHidden gems by language:")
    print(gems_by_language)
    
    gems_by_genre = gems["primary_genre"].value_counts().head(5)
    print("\nTop genres among hidden gems:")
    print(gems_by_genre)
    
    gems_by_decade = gems["decade"].value_counts().sort_index()
    print("\nHidden gems by decade:")
    print(gems_by_decade)
    

    non_gems = df[df["is_hidden_gem"] == False]
    
    print(f"\nHidden gems avg rating:     {gems['vote_average'].mean():.2f}")
    print(f"Non-hidden gems avg rating: {non_gems['vote_average'].mean():.2f}")
    print(f"Hidden gems avg popularity: {gems['popularity'].mean():.2f}")
    print(f"Non-gems avg popularity:    {non_gems['popularity'].mean():.2f}")
    

    top_gems = gems.nlargest(10, "vote_average")[[

        "title", "language_name", "primary_genre",
        "release_year", "vote_average", "runtime",
        "keywords_str", "poster_url"
    ]]
    
    print("\nTop 10 Hidden Gems:")
    print(top_gems[["title", "language_name", 
                     "vote_average", "release_year"]].to_string(index=False))
    
    return gems, top_gems

def analyse_ratings(df):
    print("\n⭐ Analyzing Ratings...")
    print("=" * 40)

    print("Overall rating statistics")
    print(df["vote_average"].describe().round(2))

    bins=[0,5,6,7,7.5,8,10]
    labels=["Poor (<5)","Below Average(5-6)","Average (6-7)","Good (7-7.5)","Great (7.5-8)","Excellent(8+)"]
    
    df["rating_bucket"]=pd.cut(
        df["vote_average"],
        bins=bins,
        labels=labels
   )

    rating_dist=df["rating_bucket"].value_counts().sort_index()
    print("\nRating distribution:")
    print(rating_dist)

    top_rated=df.nlargest(10,"vote_average")[["title", "language_name", "vote_average", 
        "vote_count", "release_year"]]

    print("\nTop 10 highest rated movies:")
    print(top_rated.to_string(index=False))

    print("\n Correlation between rating and popularity:")
    correlation=df["popularity"].corr(df["vote_average"])
    print(f"{correlation:.3f}")

    if abs(correlation) < 0.3:
        print("   Weak correlation — popular ≠ good quality")
    elif abs(correlation) < 0.7:
        print("   Moderate correlation")
    else:
        print("   Strong correlation")
    
    return rating_dist

def cinema_evolution_summary(df):
    print("\n🎬 Cinema Evolution Summary:")
    print("=" * 40)
    
    summary={}

    runtime_by_decade=df.groupby("decade")["runtime"].mean().round(1)
    summary["runtime_by_decade"]=runtime_by_decade.to_dict()

    volume_by_decade=df.groupby("decade")["id"].count()
    summary["volume_by_decade"]=volume_by_decade.to_dict()

    #Top genre by decade
    genre_decade=df.groupby(["decade","primary_genre"])["id"].count().reset_index()
    genre_decade.columns=["decade","genre","count"]

    top_genres={}

    for decade in genre_decade["decade"].unique():
        decade_data=genre_decade[genre_decade["decade"]==decade]
        top_genre=decade_data.loc[
            decade_data["count"].idxmax(),"genre"]
        top_genres[int(decade)]=top_genre
    summary["top_genre_by_decade"]=top_genres

    #Language stats
    language_stats = df.groupby("language_name").agg(
        movie_count=("id", "count"),
        avg_rating=("vote_average", "mean"),
        avg_runtime=("runtime", "mean"),
        avg_popularity=("popularity", "mean"),
        hidden_gems=("is_hidden_gem", "sum")
    ).round(2)

    # Normalise hidden gems by movie count
    # gem_rate = gems per 10 movies — fair comparison across languages
    language_stats["gem_rate"] = (
        language_stats["hidden_gems"] /
        language_stats["movie_count"] * 10
    ).round(2)

    summary["language_stats"] = language_stats.to_dict()

    #Overall stats
    summary["total_movies"]=len(df)
    summary["year_range"]=f"{int(df["release_year"].min())} - {int(df["release_year"].max())}"
    summary["avg_rating"]=round(df["vote_average"].mean(), 2)
    summary["total_hidden_gems"]=df["is_hidden_gem"].sum()
    summary["most_productive_decade"]=int(volume_by_decade.idxmax())
    
    summary["runtime_trend"]=(
        f"Average runtime dropped from "
        f"{runtime_by_decade.iloc[0]:.0f} min"
        f" ({int(runtime_by_decade.index[0])}s) to "
        f"{runtime_by_decade.iloc[-1]:.0f} min "
        f"({int(runtime_by_decade.index[-1])}s)"
    )

    print(f"Total movies analysed: {summary['total_movies']}")
    print(f"Year range: {summary['year_range']}")
    print(f"Runtime trend: {summary['runtime_trend']}")
    print(f"Most productive decade: {summary['most_productive_decade']}s")
    
    print("\nLanguage statistics (normalised):")
    print(language_stats[["movie_count", "avg_rating", 
                        "avg_runtime", "hidden_gems", 
                        "gem_rate"]].to_string())
    
    return summary,language_stats

def analyse_by_language(df,lang_stats):
    print("\n🌍 Language Cinema Profiles")
    print("=" * 40)

    lang_profile = lang_stats.copy()

    blockbusters = df.groupby("language_name")["popularity"].apply(
        lambda x: (x > 50).sum()
    ).rename("blockbusters")
    lang_profile = lang_profile.join(blockbusters)

    # Hidden gem rate — gems per 10 movies
    lang_profile["gem_rate"] = (
        lang_profile["hidden_gems"] /
        lang_profile["movie_count"] * 10
    ).round(2)

    print("\nFull language profile:")
    print(lang_profile.to_string())

    print("\nHidden gem rate (gems per 10 movies):")
    print(
        lang_profile[["movie_count", "hidden_gems", "gem_rate", "blockbusters"]]
        .sort_values("gem_rate", ascending=False)
    )

    # Signature genre — what does each language specialise in?
    print("\nSignature genre per language:")
    for lang in df["language_name"].unique():
        lang_df = df[df["language_name"] == lang]
        top_genre = lang_df["primary_genre"].value_counts().index[0]
        top_pct = (
            lang_df["primary_genre"].value_counts().iloc[0] /
            len(lang_df) * 100
        )
        print(f"   {lang}: {top_genre} ({top_pct:.0f}% of films)")

    # Highest rated film per language
    print("\nHighest rated film per language:")
    top_per_lang = df.loc[
        df.groupby("language_name")["vote_average"].idxmax()
    ][["language_name", "title", "vote_average", "release_year"]]
    print(top_per_lang.to_string(index=False))

    # Runtime by language
    print("\nAverage runtime by language (minutes):")
    runtime_lang = df.groupby("language_name")["runtime"].mean().round(1)
    print(runtime_lang.sort_values(ascending=False))

    return lang_profile


def save_analysis_results(runtime_trends, genre_trends,
                           genre_ratings, top_gems,
                           rating_dist, summary,
                           lang_profile):
    import json

    results = {
        "summary": summary,
        "runtime_by_decade": runtime_trends.to_dict(),
        "genre_ratings": genre_ratings.to_dict(),
        "top_hidden_gems": top_gems.to_dict(orient="records"),
        "language_profiles": lang_profile.to_dict(),
    }

    output_path = PROCESSED_DATA_PATH / "analysis_results.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            results, f,
            ensure_ascii=False,
            indent=2,
            default=str
        )

    print(f"\n✅ Analysis results saved to {output_path}")
    return output_path


if __name__ == "__main__":
    print("🔍 PRISM — Analysis Engine")
    print("=" * 40)

    df = load_data()

    runtime_trends = analyse_runtime_trends(df)
    genre_trends, genre_ratings = analyze_genre_trends(df)
    gems, top_gems = analyze_hidden_gems(df)
    rating_dist = analyse_ratings(df)

    summary, lang_stats = cinema_evolution_summary(df)

    lang_profile = analyse_by_language(df, lang_stats)

    save_analysis_results(
        runtime_trends, genre_trends, genre_ratings,
        top_gems, rating_dist, summary, lang_profile
    )

    print("\n🎉 Analysis complete!")
    print("Results saved — ready for LLM and Tableau.")