import os
import json
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
PROCESSED_DATA_PATH = Path("data/processed")

client = Groq(api_key=GROQ_API_KEY)


def load_analysis_context():
    analysis_path = PROCESSED_DATA_PATH / "analysis_results.json"

    if not analysis_path.exists():
        print("❌ Analysis results not found. Run analysis.py first.")
        return {}

    with open(analysis_path, "r", encoding="utf-8") as f:
        context = json.load(f)

    return context


def load_sample_movies():
    import pandas as pd
    json_path = PROCESSED_DATA_PATH / "indian_movies_clean.json"
    df = pd.read_json(json_path, orient="records")

    # Send top 20 rated movies as examples
    sample = df.nlargest(20, "vote_average")[[
        "title", "language_name", "primary_genre",
        "release_year", "vote_average", "runtime",
        "keywords_str"
    ]].to_dict(orient="records")

    return sample


def build_system_context(analysis_context, sample_movies):
    context_str = f"""
You are PRISM's AI Cinema Analyst — an expert on Indian cinema 
with access to a dataset of {analysis_context.get('summary', {}).get('total_movies', 288)} Indian films.

YOUR DATA — Use this to answer questions. Do not guess or use 
information outside this dataset:

OVERALL STATISTICS:
- Total movies analysed: {analysis_context.get('summary', {}).get('total_movies', 'N/A')}
- Year range: {analysis_context.get('summary', {}).get('year_range', 'N/A')}
- Average rating: {analysis_context.get('summary', {}).get('avg_rating', 'N/A')}/10
- Total hidden gems: {analysis_context.get('summary', {}).get('total_hidden_gems', 'N/A')}
- Most productive decade: {analysis_context.get('summary', {}).get('most_productive_decade', 'N/A')}s
- Runtime trend: {analysis_context.get('summary', {}).get('runtime_trend', 'N/A')}

RUNTIME BY DECADE (minutes):
{json.dumps(analysis_context.get('runtime_by_decade', {}), indent=2)}

GENRE RATINGS (avg rating per genre):
{json.dumps(analysis_context.get('genre_ratings', {}), indent=2)}

LANGUAGE PROFILES:
{json.dumps(analysis_context.get('language_profiles', {}), indent=2)}

TOP 20 HIGHEST RATED FILMS IN DATASET:
{json.dumps(sample_movies, indent=2, ensure_ascii=False)}

RULES FOR ANSWERING:
- Only use data provided above
- If asked about something not in your data say so honestly
- Give specific numbers and film titles when relevant
- Keep answers concise — 3-5 sentences unless user asks for detail
- Be conversational and enthusiastic about Indian cinema
- Never make up film titles, ratings, or statistics
"""
    return context_str


def chat_with_analyst(user_question, conversation_history=None):
    """
    Main chat function — answers questions about
    Indian cinema using real analysis data.

    Supports multi-turn conversation — remembers
    previous messages in the conversation.

    Args:
        user_question: string question from user
        conversation_history: list of previous messages
                             for multi-turn conversation

    Returns:
        dict with answer and updated history
    """

    if conversation_history is None:
        conversation_history = []

    # Load context fresh each time
    # In production you'd cache this
    analysis_context = load_analysis_context()
    sample_movies = load_sample_movies()
    system_context = build_system_context(
        analysis_context, sample_movies
    )

    # Build messages — system context + history + new question
    messages = [
        {"role": "system", "content": system_context}
    ]

    # Add conversation history for multi-turn memory
    messages.extend(conversation_history)

    # Add current question
    messages.append({
        "role": "user",
        "content": user_question
    })

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=1000
        )

        answer = response.choices[0].message.content

        # Update conversation history
        conversation_history.append({
            "role": "user",
            "content": user_question
        })
        conversation_history.append({
            "role": "assistant",
            "content": answer
        })

        return {
            "answer": answer,
            "history": conversation_history
        }

    except Exception as e:
        print(f"❌ Chat failed: {e}")
        return {
            "answer": "Sorry I encountered an error. Please try again.",
            "history": conversation_history
        }


if __name__ == "__main__":
    print("🤖 PRISM — AI Cinema Analyst")
    print("=" * 40)
    print("Ask me anything about Indian cinema.")
    print("Type 'quit' to exit.\n")

    history = []

    # Test questions to run automatically
    test_questions = [
        "Which genre has the highest average rating?",
        "Tell me about hidden gems in Malayalam cinema",
        "Has Indian cinema gotten shorter over the decades?",
        "Which is the highest rated film in your dataset?",
        "What makes a hidden gem different from a mainstream hit?"
    ]

    for question in test_questions:
        print(f"\n❓ {question}")
        result = chat_with_analyst(question, history)
        history = result["history"]
        print(f"🤖 {result['answer']}")
        print("-" * 40)

        import time
        time.sleep(1)