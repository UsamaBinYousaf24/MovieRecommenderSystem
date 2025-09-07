# 🎬 Movie Recommender System  

A **content-based movie recommendation system** built using **Machine Learning** that suggests the **top 5 similar movies** based on user input.  
It uses **CountVectorizer** for vectorization, **Cosine Similarity** for measuring similarity, and **Streamlit** for an interactive UI.  
The system fetches **movie posters, ratings, genres, and trailers** using the **TMDB API**.

---

## 🚀 Features  
- 🎥 Recommends **top 5 similar movies**  
- 📊 Uses **CountVectorizer** for feature extraction  
- 🔍 Computes similarity using **Cosine Similarity**  
- 🖼️ Displays **posters, ratings, genres, and trailers**  
- 🌐 **Streamlit-based interactive web app**  
- 🛠 **Future deployment planned**  

---

## 🛠 Tech Stack  
- **Python** 🐍  
- **Pandas** & **NumPy** – Data manipulation  
- **Scikit-learn** – CountVectorizer & Cosine Similarity  
- **Streamlit** – Web app interface  
- **TMDB API** – Fetching posters, genres, and trailers  

---

## 📂 Project Structure  
```bash
Movie-Recommender-System/
│── app.py                # Main Streamlit app
│── movie_dict.pkl        # Preprocessed movie dataset
│── similarity.pkl        # Precomputed similarity matrix
│── requirements.txt      # Project dependencies
│── README.md             # Project documentation
