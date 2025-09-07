import streamlit as st
import pickle
import pandas as pd
import numpy as np
import requests

# ---------------- Page Setup ----------------
st.set_page_config(page_title="Movie Recommender System", layout="wide")

# ---------------- Styles ----------------
st.markdown("""
<style>
    body { background-color: #000; color: #fff; font-family: 'Segoe UI', sans-serif; }
    .title { text-align: center; font-size: 46px; font-weight: 800; color: #e50914; margin-bottom: 20px; }
    .stSelectbox label { font-size: 18px; font-weight: 700; color: #e50914 !important; }
    div[data-baseweb="select"] { background-color: #141414; border: 2px solid #e50914; border-radius: 8px; }
    .stButton>button { background-color: #e50914; color: #fff; font-weight: 700; border-radius: 8px; padding: 12px 30px; font-size: 18px; transition: 0.3s; }
    .stButton>button:hover { background-color: #b00610; transform: scale(1.05); }

    .movie-card { text-align: center; background-color: #141414; padding: 15px; border-radius: 14px;
                  box-shadow: 0 4px 15px rgba(255,255,255,0.15); transition: transform .3s, box-shadow .3s; margin: 10px; }
    .movie-card:hover { transform: scale(1.06); box-shadow: 0 8px 20px rgba(255,255,255,0.3); }

    /* Enforce identical poster size for ALL images */
    .movie-poster { width: 150px; height: 200px; object-fit: cover; border-radius: 10px; margin-bottom: 10px;
                    display: block; margin-left: auto; margin-right: auto; }

    .movie-title { font-size: 14px; font-weight: 800; color: #fff; margin-bottom: 6px; }
    .movie-info { font-size: 12px; color: #bbb; margin-bottom: 4px; }
    .movie-genres { font-size: 11px; color: #e5e5e5; margin-bottom: 10px; }
    .trailer-btn { display: inline-block; background-color: #e50914; color: #fff; padding: 6px 14px; font-size: 13px;
                   font-weight: 700; border-radius: 6px; text-decoration: none; transition: .3s; }
    .trailer-btn:hover { background-color: #b00610; }
</style>
""", unsafe_allow_html=True)

# ---------------- Config ----------------
API_KEY = "d3eea56f1983a39c4290160c2fb03522"
TMDB_BASE = "https://api.themoviedb.org/3"
IMG_BASE = "https://image.tmdb.org/t/p/w500"
PLACEHOLDER = "https://via.placeholder.com/200x300?text=No+Image"

# ---------------- Helpers ----------------
def safe_get(url, params=None, timeout=12):
    try:
        r = requests.get(url, params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"TMDB HTTP error: {e}")
    except requests.exceptions.RequestException as e:
        st.error(f"Network error: {e}")
    return None

@st.cache_data(show_spinner=False)
def fetch_movie_details(movie_id: int):
    """
    One call with append_to_response=videos so we get details + trailers together.
    Returns a dict with safe fallbacks so UI never crashes.
    """
    params = {"api_key": API_KEY, "language": "en-US", "append_to_response": "videos"}
    data = safe_get(f"{TMDB_BASE}/movie/{movie_id}", params=params)

    if not data:
        return {
            "poster": PLACEHOLDER, "title": "Unknown", "rating": 0.0, "year": "N/A",
            "genres": "Unknown", "trailer": "#"
        }

    poster_path = data.get("poster_path")
    poster_url = f"{IMG_BASE}{poster_path}" if poster_path else PLACEHOLDER

    title = data.get("title", "Unknown")
    rating = round(float(data.get("vote_average", 0.0) or 0.0), 1)

    release_date = data.get("release_date") or ""
    year = release_date.split("-")[0] if release_date else "N/A"

    genres_list = [g.get("name", "") for g in data.get("genres", [])]
    genres = ", ".join([g for g in genres_list if g]) or "Unknown"

    trailer_key = None
    for v in (data.get("videos", {}) or {}).get("results", []):
        if v.get("type") == "Trailer" and v.get("site") == "YouTube" and v.get("key"):
            trailer_key = v["key"]
            break
    trailer = f"https://www.youtube.com/watch?v={trailer_key}" if trailer_key else "#"

    return {
        "poster": poster_url,
        "title": title,
        "rating": rating,
        "year": year,
        "genres": genres,
        "trailer": trailer
    }

def top_k_indices(distances: np.ndarray, k: int = 5, self_index: int = None):
    """Fast top-k without sorting the whole array."""
    if self_index is not None:
        distances = distances.copy()
        distances[self_index] = -np.inf  # exclude the selected item itself
    k = min(k, distances.shape[0]-1)
    if k <= 0:
        return []
    # argpartition to get k largest, then sort those
    part_idx = np.argpartition(distances, -k)[-k:]
    return part_idx[np.argsort(distances[part_idx])[::-1]]

def recommend(selected_title: str, k: int = 5):
    """Return up to k recommended movie detail dicts."""
    # Find the exact row index of the selected title
    idx_matches = movies.index[movies["title"] == selected_title].tolist()
    if not idx_matches:
        st.warning("Selected movie not found in dataset.")
        return []
    i = idx_matches[0]

    distances = similarity[i]
    rec_indices = top_k_indices(distances, k=k, self_index=i)

    results = []
    for j in rec_indices:
        movie_id = int(movies.iloc[j]["movie_id"])
        results.append(fetch_movie_details(movie_id))
    return results

# ---------------- Data ----------------
movies_dict = pickle.load(open("movie_dict.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl", "rb"))

# ---------------- UI ----------------
st.markdown("<h1 class='title'>🎬 Movie Recommender System 🎥</h1>", unsafe_allow_html=True)

selected_movie_name = st.selectbox(
    "🍿 Pick a movie you like, and we will recommend similar ones:",
    movies["title"].values
)

if st.button("🔍 Recommend Movies"):
    with st.spinner("Finding great picks for you..."):
        recs = recommend(selected_movie_name, k=5)

    if not recs:
        st.info("No recommendations available.")
    else:
        cols = st.columns(len(recs))
        for col, movie in zip(cols, recs):
            with col:
                st.markdown(f"""
                    <div class="movie-card">
                        <img src="{movie['poster']}" class="movie-poster" loading="lazy" alt="Poster">
                        <div class="movie-title">{movie['title']}</div>
                        <div class="movie-info">⭐ {movie['rating']} | 📅 {movie['year']}</div>
                        <div class="movie-genres">{movie['genres']}</div>
                        <a href="{movie['trailer']}" target="_blank" class="trailer-btn">▶ Watch Trailer</a>
                    </div>
                """, unsafe_allow_html=True)
