# 🎬 CineMatch AI — Movie Recommendation Platform

CineMatch AI is a modern, content-based movie recommendation platform that analyzes movie metadata to discover films aligned with user preferences. Built with Streamlit and powered by vector similarity algorithms, it combines real-time TMDB API data with a sleek, cinematic UI/UX.

## Key Features

* 🔍 **Smart Autocomplete Search:** Search across 5,000+ movies in the catalog.
* 🤖 **Content-Based Vector Matching:** Computes Cosine Similarity over genres, keywords, cast, and crew features.
* 📊 **Selected Film Intelligence:** Displays metadata including IMDb ratings, runtime, plot summaries, budgets, and revenue.
* 🍿 **Dynamic Grid Layout:** Displays multi-row recommendations (up to 12 films) with synopsis expanders and trailer links.
* ⭐ **Session Favorites & History:** Easily bookmark movies into a persistent sidebar favorites list.
* ⚡ **Optimized Performance:** API call caching using `@st.cache_data` ensures fast response times.

## Tech Stack

* **Frontend & Web Framework:** Streamlit, Custom HTML/CSS (Glassmorphism & Dark Palette)
* **Data Processing & ML:** Pandas, NumPy, Scikit-Learn (Cosine Similarity, Pickle)
* **API Integration:** TMDB (The Movie Database) v3 API
* **Language:** Python 3.x
