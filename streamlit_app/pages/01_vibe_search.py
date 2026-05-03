import sys
import os
from pathlib import Path
import streamlit as st


sys.path.append(str(Path(__file__).parent.parent.parent))

from src.recommender import vibe_search, load_movies

st.set_page_config(
    page_title="PRISM — Vibe Search",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Vibe Search")
st.caption(
    "Describe what you want in plain English — "
    "PRISM finds the perfect Indian film for you"
)

st.markdown("---")

examples = [
    "Tamil Action 3 hours",
    "Hindi sports feel good",
    "Malayalam thriller highly rated",
    "Telugu detective",
    "Short Malayalam thriller",
    "Hindi feel good family movie",
]

st.markdown("**✨ Try these or type your own:**")

selected_example = st.pills(
    "Examples",
    options=examples,
    label_visibility="collapsed"
)

# Use pill selection OR manual text input
# whichever has a value
manual_query = st.text_input(
    "Or describe your own vibe:",
    placeholder="e.g. Tamil Action 3 hours...",
    key="search_input"
)

# Priority — manual input overrides pill selection
query = manual_query if manual_query else selected_example

if query:
    st.caption(f"🔍 Click Find Movies button to search for: *{query}*")

search_btn = st.button("🔍 Find Movies", type="primary")

if search_btn and query:
    with st.spinner("🤖 Analysing your vibe..."):
        result = vibe_search(query)

    st.markdown("---")
    st.markdown(
        f"### Found **{result['total_matches']}** matching films"
    )

    movies = result["movies"]

    st.markdown("#### 🤖 PRISM Recommends")
    st.markdown(result["recommendations"])

    st.markdown("---")

    if movies:
        st.markdown("#### 🎬 Top Matches")

        num_movies = len(movies[:3])

        if num_movies == 1:
            col_left, col_center, col_right = st.columns([1, 2, 1])
            cols = [col_center]
        else:
            cols = st.columns(num_movies)

        for i, movie in enumerate(movies[:3]):
            with cols[i]:
                # Poster
                if movie.get("poster_url"):
                    st.image(
                        movie["poster_url"],
                        use_container_width=True
                    )

                # Title
                st.markdown(f"**{movie['title']}**")

                # Metadata
                st.caption(
                    f"{movie['language_name']} · "
                    f"{int(movie['release_year'])} · "
                    f"{movie['primary_genre']}"
                )

                # Rating
                st.metric(
                    "Rating",
                    f"{movie['vote_average']}/10"
                )

                # Runtime
                st.caption(
                    f"⏱️ {movie['runtime']} min "
                    f"({movie['runtime_category']})"
                )

                # Hidden gem badge
                if movie.get("is_hidden_gem"):
                    st.success("💎 Hidden Gem")

                # Plot expander
                with st.expander("Plot"):
                    st.write(
                        movie.get(
                            "overview",
                            "No overview available"
                        )
                    )

    if movies and len(movies) > 3:
        st.markdown("#### Also worth watching:")
        for movie in movies[3:]:
            st.markdown(
                f"**{movie['title']}** ({int(movie['release_year'])}) "
                f"— {movie['language_name']} · "
                f"⭐ {movie['vote_average']}/10 · "
                f"⏱️ {movie['runtime']} min"
            )

    st.markdown("---")

    with st.expander("🔍 How PRISM understood your search"):
        params = result["params"]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Extracted parameters:**")
            if params.get("language"):
                st.write(f"🗣️ Language: {params['language']}")
            if params.get("genres"):
                st.write(f"🎭 Genres: {', '.join(params['genres'])}")
            if params.get("themes"):
                st.write(f"🎯 Themes: {', '.join(params['themes'])}")
            if params.get("mood"):
                st.write(f"😊 Mood: {params['mood']}")

        with col2:
            if params.get("runtime_min") or params.get("runtime_max"):
                st.write(
                    f"⏱️ Runtime: "
                    f"{params.get('runtime_min', '?')}–"
                    f"{params.get('runtime_max', '?')} min"
                )
            if params.get("min_rating"):
                st.write(f"⭐ Min rating: {params['min_rating']}")
            if params.get("decade"):
                st.write(f"📅 Era: {params['decade']}s")

        # Raw JSON for technical users
        with st.expander("Raw JSON"):
            st.json(params)