from flask import Flask, render_template,request
import pickle as pkl
import pandas as pd
import requests
import os

app = Flask(__name__)
# Ensure models folder exists
os.makedirs("models", exist_ok=True)

# Movie dict
MOVIE_DICT_PATH = "models/movie_dict.pkl"
MOVIE_DICT_URL = "https://drive.google.com/uc?export=download&id=1OXagqFdqQzrTE7Sm7VA1lxbCZtRCvEwF"

if not os.path.exists(MOVIE_DICT_PATH):
    r = requests.get(MOVIE_DICT_URL)
    with open(MOVIE_DICT_PATH, "wb") as f:
        f.write(r.content)

movie_list = pkl.load(open(MOVIE_DICT_PATH,"rb"))
movie = pd.DataFrame(movie_list)

# Similarity
SIMILARITY_PATH = "models/similarity.pkl"
SIMILARITY_URL = "https://drive.google.com/uc?export=download&id=1zmQ2YGJnj4ipoao5UMvSLh3aulnLt2qq"

if not os.path.exists(SIMILARITY_PATH):
    r = requests.get(SIMILARITY_URL)
    with open(SIMILARITY_PATH, "wb") as f:
        f.write(r.content)

similarity = pkl.load(open(SIMILARITY_PATH,"rb"))

def fetch_poster(movie_id):
    response = requests.get(
        f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=358d592916f1b0708bdb7d9039c8c525&language=en-US"
    )
    data = response.json()
    poster_path = data.get('poster_path')

    if poster_path:
        return "https://image.tmdb.org/t/p/w500/" + poster_path
    else:
        return "https://via.placeholder.com/500x750?text=No+Image"


def recommend_movie(user_input):
    #movie_index = movie[movie['title'] == user_input].index[0]
    filtered = movie[movie['title'] == user_input]
    if filtered.empty:
        return {}

    movie_index = filtered.index[0]
    distance = similarity[movie_index]

    recommendation_list = sorted(list(enumerate(distance)), key=lambda x:x[1], reverse=True)[1:6]
    
    
    recommendation_dict = {}

    for i in recommendation_list:
        movie_id = movie.iloc[i[0]].id
        poster = fetch_poster(movie_id)
        name = movie.iloc[i[0]].title
        #recommend_movie_names.append(movie.iloc[i[0]].title)
        recommendation_dict[movie_id] = [name, poster]
    return recommendation_dict

@app.route('/', methods=['GET', 'POST'])
def home():
    movie_names_suggestion = movie['title'].values

    print("METHOD:", request.method)

    if request.method == 'POST':
        print("FORM DATA:", request.form)
        selected_movie = request.form.get('user_selection')
        if not selected_movie:
            return render_template("index.html", movie=movie_names_suggestion, recommendation=None, selected_movie=None)
        recommendation = recommend_movie(selected_movie)
        return render_template("index.html", movie=movie_names_suggestion, recommendation=recommendation, selected_movie=selected_movie)

    return render_template("index.html", movie=movie_names_suggestion, recommendation=None, selected_movie=None)

'''if __name__ == "__main__":
    app.run(debug=True)'''

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000) 