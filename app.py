import time
import pickle
import pandas as pd
import requests
import streamlit as st

# ==============================================================================
# 1. PAGE CONFIGURATION & SESSION STATE
# ==============================================================================
st.set_page_config(
    page_title="CineMatch AI — Movie Recommendation Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State for Favorites & Recent Searches
if "favorites" not in st.session_state:
    st.session_state.favorites = []
if "recent_searches" not in st.session_state:
    st.session_state.recent_searches = []

API_KEY = "d6cea28726742c28938919a601952665"

# ==============================================================================
# 2. CUSTOM STYLING & DARK RED THEME (CSS)
# ==============================================================================
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    :root {
        --bg-main: #0F172A;
        --bg-secondary: #111827;
        --card-bg: #1E293B;
        --accent-red: #DC2626;
        --accent-red-dark: #991B1B;
        --text-white: #FFFFFF;
        --text-muted: #94A3B8;
        --border-color: rgba(255, 255, 255, 0.1);
    }

    html, body, [data-testid="stAppViewContainer"] {
        background-color: var(--bg-main) !important;
        font-family: 'Inter', sans-serif !important;
        color: var(--text-white) !important;
    }

    [data-testid="stSidebar"] {
        background-color: var(--bg-secondary) !important;
        border-right: 1px solid var(--border-color) !important;
    }

    /* Dark Red Styled Cards in Sidebar */
    .sidebar-red-card {
        background: linear-gradient(135deg,#0F172A );
        border: 1px solid rgba(220, 38, 38, 0.4);
        box-shadow: 0 4px 15px rgba(220, 38, 38, 0.15);
        border-radius: 12px;
        padding: 1.2rem;
        margin-bottom: 1.2rem;
        
    }

    .sidebar-card-title {
        color: #FFFFFF !important;
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }
/* Banner Hero Section with Theater Background Image */
    .banner-hero {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.2) 0%, rgba(15, 23, 42, 0.4) 100%),
                    url('https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?auto=format&fit=crop&w=1920&q=80');
        background-size: cover;
        background-position: center;
        border-radius: 16px;
        padding: 3rem 2.5rem;
        border: 1px solid rgba(220, 38, 38, 0.3);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 2rem;
    }
    

    .banner-title-flex {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
    }

    .banner-title-text {
        color: #FFFFFF !important;
        font-size: 3.2rem !important;
        font-weight: 800 !important;
        letter-spacing: -1px;
        line-height: 1;
        margin: 0 !important;
    }

    .banner-subtitle-text {
        color: #38BDF9 !important;
        font-size: 1.1rem !important;
        font-weight: 500;
        margin-top: 0.6rem;
    }

    /* Detail & Rec Cards */
    .detail-card {
        background: rgba(30, 41, 59, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid var(--border-color);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 2rem;
    }

    .meta-tag {
        background-color: rgba(56, 189, 248, 0.15);
        color: #38BDF8;
        border: 1px solid rgba(56, 189, 248, 0.3);
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 4px;
        margin-bottom: 4px;
    }

    .rating-badge {
        background: linear-gradient(90deg, #F59E0B, #D97706);
        color: #FFFFFF;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 0.8rem;
        display: inline-block;
    }

    .rec-card {
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 10px;
        padding: 0.75rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
    }

    .rec-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(220, 38, 38, 0.2);
        border-color: rgba(220, 38, 38, 0.4);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #DC2626, #991B1B) !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        transition: background-color 0.2s ease !important;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #B91C1C, #7F1D1D) !important;
    }

    [data-testid="stMetricValue"] {
        color: #38BDF8 !important;
        font-weight: 700 !important;
    }

    .footer {
        text-align: center;
        padding: 2.5rem 0 1rem 0;
        color: var(--text-muted);
        font-size: 0.85rem;
        border-top: 1px solid var(--border-color);
        margin-top: 3rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# 3. API & DATA FETCHING UTILITIES
# ==============================================================================
@st.cache_data(show_spinner=False)
def fetch_movie_full_details(movie_id: int):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get("poster_path")
            poster_url = (
                f"https://image.tmdb.org/t/p/w500/{poster_path}"
                if poster_path
                else "https://via.placeholder.com/500x750?text=No+Poster"
            )
            genres = [g["name"] for g in data.get("genres", [])]
            return {
                "poster": poster_url,
                "rating": round(data.get("vote_average", 0.0), 1),
                "overview": data.get("overview", "No plot overview available."),
                "release_year": data.get("release_date", "N/A")[:4],
                "runtime": f"{data.get('runtime', 0)} mins",
                "genres": genres[:3],
                "tagline": data.get("tagline", ""),
                "popularity": round(data.get("popularity", 0.0), 1),
                "vote_count": data.get("vote_count", 0),
                "language": data.get("original_language", "en").upper(),
                "budget": f"${data.get('budget', 0):,}" if data.get('budget') else "N/A",
                "revenue": f"${data.get('revenue', 0):,}" if data.get('revenue') else "N/A"
            }
    except requests.exceptions.RequestException:
        pass

    return {
        "poster": "https://via.placeholder.com/500x750?text=No+Poster",
        "rating": 0.0,
        "overview": "Information unavailable.",
        "release_year": "N/A",
        "runtime": "N/A",
        "genres": [],
        "tagline": "",
        "popularity": 0.0,
        "vote_count": 0,
        "language": "N/A",
        "budget": "N/A",
        "revenue": "N/A"
    }


def add_favorite(title: str):
    if title not in st.session_state.favorites:
        st.session_state.favorites.append(title)
        st.toast(f"Saved '{title}' to Favorites.")


# ==============================================================================
# 4. DATA LOAD & RECOMMENDATION ALGORITHM
# ==============================================================================
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies_df = pd.DataFrame(movies_dict)
    similarity_matrix = pickle.load(open('similarity.pkl', 'rb'))
    return movies_df, similarity_matrix


try:
    movies, similarity = load_data()
except Exception:
    st.error("Error loading model data files ('movies_dict.pkl', 'similarity.pkl'). Please verify file path.")
    st.stop()


def recommend(movie_title: str, top_n: int = 4):
    movie_index = movies[movies['title'] == movie_title].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1: top_n + 1]

    rec_data = []
    for item in movies_list:
        idx = item[0]
        score = item[1]
        m_id = movies.iloc[idx].id
        m_title = movies.iloc[idx].title
        details = fetch_movie_full_details(m_id)
        details["title"] = m_title
        details["id"] = m_id
        details["similarity_score"] = round(score * 100, 1)
        rec_data.append(details)

    return rec_data


# ==============================================================================
# 5. SIDEBAR DESIGN (DARK RED THEMED SECTIONS)
# ==============================================================================
with st.sidebar:
    # Settings Red Card
    st.markdown("""
        <div class="sidebar-red-card">
            <div class="sidebar-card-title">SETTINGS</div>
        </div>
    """, unsafe_allow_html=True)
    num_recommendations = st.slider(
        "Recommendation Count:",
        min_value=4,
        max_value=12,
        value=8,
        step=4
    )

    st.write("")

    # Favorites Red Card
    st.markdown("""
        <div class="sidebar-red-card">
            <div class="sidebar-card-title">FAVORITES</div>
        </div>
    """, unsafe_allow_html=True)
    if st.session_state.favorites:
        for fav in st.session_state.favorites:
            st.markdown(f"<span style='color: white;'>• <b>{fav}</b></span>", unsafe_allow_html=True)
    else:
        st.caption("No favorite titles saved yet.")

    st.write("")

    # Recent Searches Red Card
    st.markdown("""
        <div class="sidebar-red-card">
            <div class="sidebar-card-title">RECENT SEARCHES</div>
        </div>
    """, unsafe_allow_html=True)
    if st.session_state.recent_searches:
        for recent in list(dict.fromkeys(reversed(st.session_state.recent_searches)))[:5]:
            st.markdown(f"<span style='color: white;'>• <b>{recent}</b></span>", unsafe_allow_html=True)
    else:
        st.caption("No recent searches.")

    st.write("")

    # Engine Architecture Info
    st.markdown("""
        <div class="sidebar-red-card">
            <div class="sidebar-card-title">ENGINE ARCHITECTURE</div>
            <p style="font-size: 0.85rem; color: #E2E8F0; margin-bottom: 0;"><strong>Cosine Similarity Engine</strong><br>Vectorizing movie attributes (genres, keywords, cast & crew) in high-dimensional feature space.</p>
        </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 6. HERO HEADER BANNER (THEATER BACKGROUND & ICON MATCHING SCREENSHOT)
# ==============================================================================
st.markdown("""
    <div class="banner-hero">
        <div class="banner-title-flex">
            <svg width="46" height="46" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
                <rect x="2" y="4" width="20" height="16" rx="2" ry="2"></rect>
                <path d="M2 8h20"></path>
                <path d="M6 4v4"></path>
                <path d="M10 4v4"></path>
                <path d="M14 4v4"></path>
                <path d="M18 4v4"></path>
            </svg>
            <h1 class="banner-title-text">CineMatch AI</h1>
        </div>
        <div class="banner-subtitle-text">Discover your next favorite movie powered by AI-driven content similarity.</div>
    </div>
""", unsafe_allow_html=True)

# ==============================================================================
# 7. SEARCH & SELECTED MOVIE DETAILS PANEL
# ==============================================================================
st.caption("Search or select a movie from our curated catalog:")
selected_movie_name = st.selectbox(
    "Search or select a movie:",
    movies['title'].values,
    index=None,
    placeholder="Type a movie title (e.g. Inception, The Dark Knight)...",
    label_visibility="collapsed"
)

if selected_movie_name:
    if selected_movie_name not in st.session_state.recent_searches:
        st.session_state.recent_searches.append(selected_movie_name)

    curr_id = movies[movies['title'] == selected_movie_name].iloc[0].id
    curr_details = fetch_movie_full_details(curr_id)

    st.markdown("### Selected Film Details")
    with st.container():
        st.markdown('<div class="detail-card">', unsafe_allow_html=True)
        col_img, col_info = st.columns([1, 3])

        with col_img:
            st.image(curr_details["poster"], use_container_width=True)

        with col_info:
            st.markdown(f"## {selected_movie_name} ({curr_details['release_year']})")
            if curr_details["tagline"]:
                st.markdown(f"*\"{curr_details['tagline']}\"*")

            genre_tags = " ".join([f"<span class='meta-tag'>{g}</span>" for g in curr_details["genres"]])
            st.markdown(f"{genre_tags} <span class='rating-badge'>Rating: {curr_details['rating']} / 10</span>",
                        unsafe_allow_html=True)

            st.write("")
            st.markdown(f"**Runtime:** {curr_details['runtime']} | **Language:** {curr_details['language']}")
            st.markdown(f"**Overview:** {curr_details['overview']}")

            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("Popularity Score", curr_details["popularity"])
            m_col2.metric("Budget", curr_details["budget"])
            m_col3.metric("Revenue", curr_details["revenue"])

            # Add to Favorites
            st.button(
                f"Add '{selected_movie_name}' to Favorites",
                on_click=add_favorite,
                args=(selected_movie_name,)
            )

        st.markdown('</div>', unsafe_allow_html=True)

    st.write("---")

    # ==============================================================================
    # 8. RECOMMENDATION ENGINE & GRID DISPLAY
    # ==============================================================================
    st.markdown(f"### Recommendations for {selected_movie_name}")

    if st.button("Generate AI Recommendations", use_container_width=True):
        start_time = time.time()

        with st.spinner("Analyzing high-dimensional feature vectors and fetching metadata..."):
            recommendations = recommend(selected_movie_name, top_n=num_recommendations)
            elapsed_time = round(time.time() - start_time, 2)

        GRID_COLS = 4
        for i in range(0, len(recommendations), GRID_COLS):
            row = recommendations[i: i + GRID_COLS]
            cols = st.columns(GRID_COLS)

            for col, item in zip(cols, row):
                with col:
                    with st.container():
                        st.markdown('<div class="rec-card">', unsafe_allow_html=True)
                        st.image(item["poster"], use_container_width=True)

                        st.markdown(f"**{item['title']}** ({item['release_year']})")
                        st.markdown(
                            f"<span class='rating-badge'>Score: {item['rating']}</span> &nbsp; <span class='meta-tag'>{item['similarity_score']}% Match</span>",
                            unsafe_allow_html=True)

                        with st.expander("Synopsis"):
                            st.caption(item["overview"])

                        # Two Action Buttons: Favorite and Watch Trailer
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            st.button(
                                "Favorite",
                                key=f"fav_{item['id']}",
                                on_click=add_favorite,
                                args=(item['title'],),
                                use_container_width=True
                            )
                        with btn_col2:
                            trailer_url = f"https://www.youtube.com/results?search_query={item['title'].replace(' ', '+')}+official+trailer"
                            st.link_button("Trailer", trailer_url, use_container_width=True)

                        st.markdown('</div>', unsafe_allow_html=True)

        st.write("---")

        # ==============================================================================
        # 9. EXPLAINABILITY & DASHBOARD METRICS SECTION
        # ==============================================================================
        st.markdown("### Recommendation Insights and Analytics")
        st.info(
            f"**Recommendation Logic:** These movies were matched because they share strong cosine similarity vectors "
            f"across genres, cast, crew, and thematic keywords with **{selected_movie_name}**."
        )

        avg_match = round(sum(r['similarity_score'] for r in recommendations) / len(recommendations), 1)

        stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
        stat_col1.metric("Catalog Size", f"{len(movies):,}")
        stat_col2.metric("Processing Time", f"{elapsed_time}s")
        stat_col3.metric("Average Similarity", f"{avg_match}%")
        stat_col4.metric("Engine Metric", "Cosine Similarity")

else:
    st.write("")
    st.caption("Select a movie title from the dropdown above to view recommendations.")

# ==============================================================================
# 10. FOOTER
# ==============================================================================
st.markdown("""
    <div class="footer">
        CineMatch AI Platform &bull; Powered by TMDB API, Scikit-Learn, Pandas & Streamlit<br>
        Developed by <strong>Shraddha</strong>
    </div>
""", unsafe_allow_html=True)