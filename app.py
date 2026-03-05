import pickle
import streamlit as st
import pandas as pd
import requests
import urllib.parse
import re
import time
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("TMDB_API_KEY")

import gdown
# file_id = "1UiS8_1EusgWUmA2WzWnj-o1VApj2AYdl"
# if os.path.exists("similarity.pkl"):
#     os.remove("similarity.pkl")
  
url = f"https://drive.google.com/uc?id={file_id}"
gdown.download(url, "similarity.pkl", quiet=False, fuzzy=True)

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ---------------- BACKGROUND STYLE ---------------- #
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    color: white;
}
img {
    border-radius: 15px;
    transition: transform 0.3s;
}
img:hover {
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# ---------------- TITLE ---------------- #
st.markdown("""
<h1 style='text-align: center;'>🎬 Movie Recommender</h1>
<p style='text-align: center; color: lightgray;'>
Discover movies similar to your favourites
</p>
""", unsafe_allow_html=True)

# ---------------- HELPER FUNCTIONS ---------------- #

def extract_year(title):
    match = re.search(r'\((\d{4})\)', title)
    return match.group(1) if match else ""

@st.cache_data(show_spinner=False)
def fetch_poster(movie_name):
    year = extract_year(movie_name)
    clean_name = movie_name.split('(')[0].strip()
    encoded_name = urllib.parse.quote(clean_name)

    if year:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={encoded_name}&year={year}"
    else:
        url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={encoded_name}"

    # Retry 2 times if TMDB fails
    for _ in range(2):
        try:
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                continue

            data = response.json()
            results = data.get('results', [])

            for movie in results:
                poster_path = movie.get('poster_path')
                if poster_path:
                    return f"https://image.tmdb.org/t/p/w500{poster_path}"

        except:
            pass

        time.sleep(0.2)

    # DO NOT cache broken responses
    return "https://via.placeholder.com/500x750?text=No+Poster"

def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

    recommended_names = []
    recommended_posters = []

    for i in distances[1:6]:
        movie_name = movies.iloc[i[0]].title
        recommended_names.append(movie_name)
        recommended_posters.append(fetch_poster(movie_name))
        time.sleep(0.15)

    return recommended_names, recommended_posters

# ---------------- LOAD DATA ---------------- #

with open('movies_dict.pkl', 'rb') as f:
    movies_dict = pickle.load(f)

with open('similarity.pkl', 'rb') as f:
    similarity = pickle.load(f)

movies = pd.DataFrame(movies_dict)

# ---------------- UI SELECT ---------------- #

st.markdown("### 🎯 Choose a Movie")

selected_movie = st.selectbox(
    "",
    movies['title'].values
)

recommend_clicked = st.button("✨ Show Recommendations")

# ---------------- SHOW RESULTS ---------------- #

if recommend_clicked:
    names, posters = recommend(selected_movie)

    st.markdown("---")
    st.subheader("✨ Recommended for you")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"<h4 style='text-align:center'>{names[0]}</h4>", unsafe_allow_html=True)
        st.image(posters[0], use_container_width=True)

    with col2:
        st.markdown(f"<h4 style='text-align:center'>{names[1]}</h4>", unsafe_allow_html=True)
        st.image(posters[1], use_container_width=True)

    with col3:
        st.markdown(f"<h4 style='text-align:center'>{names[2]}</h4>", unsafe_allow_html=True)
        st.image(posters[2], use_container_width=True)

    with col4:
        st.markdown(f"<h4 style='text-align:center'>{names[3]}</h4>", unsafe_allow_html=True)
        st.image(posters[3], use_container_width=True)

    with col5:
        st.markdown(f"<h4 style='text-align:center'>{names[4]}</h4>", unsafe_allow_html=True)
        st.image(posters[4], use_container_width=True)