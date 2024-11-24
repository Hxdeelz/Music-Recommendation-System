# Music Recommendation System (MRS) 🎶

A machine learning-powered web application that provides personalized music recommendations based on user input.
This project uses multiple algorithms to generate song recommendations, with an intuitive interface to explore and interact with the results.

---

## This project was built by:
    Miar wely and Hadeel Tarif

---

## How to run the project
    - run the app.py file with the command "python app.py" 
    - after running it you'll see the pre traind encoder model being loading 
    - after a few sec you will get the link to the website, follow link
    - after that you will be taken to the user interface where you will see a search box
        in the search box you can type the song name or the artist name and scroll throw the suggestions to find the song you are looking for.
    - after that press search and you will be presented with 3 sections each section represents an output for an algorithm with 5 songs.
    - you can interact and listen to each song and save it directly to your spotify account if you are logged in.

    
## Features ✨
- **Search Suggestions**:
  - Type a song name or artist name, and get autocomplete suggestions.
- **Recommendations**:
  - Recommendations from three algorithms:
    - **K-Nearest Neighbors (KNN)**.
    - **Autoencoder-based embedding similarity**.
    - **Random Forest clustering**.
- **Spotify Integration**:
  - Interact with song embeddings and directly save songs to your Spotify account (if logged in).
- **Dynamic and responsive user interface**.

---

## Project Structure 📂

MRS_FINAL/
├── app.py                     # Main application file
├── routes/                    # Folder for route files
│   ├── suggestions.py         # Route for fetching suggestions
│   ├── recommendations.py     # Route for recommendations
├── static/                    # Static files (CSS, JS, etc.)
│   ├── style.css              # CSS file for styling
│   ├── MIX.js                 # JavaScript file for client-side logic
├── templates/                 # HTML templates
│   ├── index.html             # Main HTML file
├── models/                    # Folder for logic or utilities (e.g., recommendation engine)
│  ├── recommendation_engine.py  # Recommendation logic/models
├── data/                      # Folder for datasets and models
│   ├── updated_dataset.csv    # Dataset for song information
│   ├── updated_encoder_model.h5 # Trained encoder model
└── README.md
