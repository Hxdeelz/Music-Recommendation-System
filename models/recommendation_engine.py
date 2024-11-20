from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
from sklearn.ensemble import RandomForestClassifier
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow import keras


# Set environment variable to disable oneDNN optimizations if desired
# os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load data
data = pd.read_csv("data/updated_dataset.csv")  
# Define features to normalize
features = ['duration_ms', 'year', 'acousticness', 'danceability', 'energy', 
            'instrumentalness', 'liveness', 'loudness', 'speechiness', 'tempo', 
            'valence', 'mode', 'key', 'popularity', 'explicit']

# Standardize features
scaler = StandardScaler()
data[features] = scaler.fit_transform(data[features])

# KNN Model
knn = NearestNeighbors(n_neighbors=6, metric='cosine')
knn.fit(data[features])

def get_knn_recommendations(song_row, top_n=5):
    if song_row.empty:
        return []
    
    input_song_index = song_row.index[0]
    input_song_vector = data[features].iloc[input_song_index].values.reshape(1, -1)
    
    distances, indices = knn.kneighbors(input_song_vector)
    similar_indices = indices.flatten()[1:top_n+1]
    
    recommendations = data.iloc[similar_indices][['name', 'artists', 'embed_track']].values.tolist()
    recommendations = [f"{name} by {artists}" for name, artists, embedded_code in recommendations]
    embedded_codes = data.iloc[similar_indices]['embed_track'].values.tolist()
    return recommendations, embedded_codes

# Load the encoder model
encoder = keras.models.load_model("data/updated_encoder_model.h5", compile=False)

# Compile the encoder model (if needed)
# encoder.compile(optimizer='adam', loss='mse')

# Generate song embeddings
song_embeddings = encoder.predict(data[features])

def get_autoencoder_recommendations(song_row, top_n=5):
    if song_row.empty:
        return []
    
    input_song_index = song_row.index[0]
    input_song_embedding = song_embeddings[input_song_index].reshape(1, -1)
    
    similarities = cosine_similarity(input_song_embedding, song_embeddings)
    similar_indices = similarities[0].argsort()[-top_n-1:][::-1][1:]
    
    recommendations = data.iloc[similar_indices][['name', 'artists', 'embed_track']].values.tolist()
    recommendations = [f"{name} by {artists}" for name, artists, embedded_code in recommendations]
    embedded_codes = data.iloc[similar_indices]['embed_track'].values.tolist()
    return recommendations, embedded_codes

# KMeans Clustering
n_clusters = 10  # Number of clusters
kmeans = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
data['cluster'] = kmeans.fit_predict(data[features])

# Random Forest Classifier
rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
rf_classifier.fit(data[features], data['cluster'])

def get_rf_recommendations(song_row, top_n=5):
    if song_row.empty:
        return []
    
    input_song_index = song_row.index[0]
    input_song_vector = data[features].iloc[input_song_index].values.reshape(1, -1)
    
    predicted_cluster = rf_classifier.predict(input_song_vector)[0]
    cluster_songs = data[data['cluster'] == predicted_cluster]
    cluster_songs = cluster_songs[cluster_songs.index != input_song_index]
    
    top_recommendations = cluster_songs.sample(min(top_n, len(cluster_songs)))
    recommendations = top_recommendations[['name', 'artists', 'embed_track']].values.tolist()
    recommendations = [f"{name} by {artists}" for name, artists, embedded_code in recommendations]
    embedded_codes = top_recommendations['embed_track'].values.tolist()
    return recommendations, embedded_codes

def generate_recommendation_list(song_row, top_n=5):
    knn_recs, knn_codes = get_knn_recommendations(song_row, top_n)
    autoencoder_recs, autoencoder_codes = get_autoencoder_recommendations(song_row, top_n)
    rf_recs, rf_codes = get_rf_recommendations(song_row, top_n)
    
    max_len = max(len(knn_recs), len(autoencoder_recs), len(rf_recs))
    knn_recs.extend([""] * (max_len - len(knn_recs)))
    autoencoder_recs.extend([""] * (max_len - len(autoencoder_recs)))
    rf_recs.extend([""] * (max_len - len(rf_recs)))
    
    knn_codes.extend([""] * (max_len - len(knn_codes)))
    autoencoder_codes.extend([""] * (max_len - len(autoencoder_codes)))
    rf_codes.extend([""] * (max_len - len(rf_codes)))
    
    return pd.DataFrame({
        'KNN': knn_recs,
        'KNN_Code': knn_codes,
        'Autoencoder': autoencoder_recs,
        'Autoencoder_Code': autoencoder_codes,
        'RandomForest': rf_recs,
        'RandomForest_Code': rf_codes
    })


# @app.route('/')
# def home():
#     with open('index.html', 'r') as file:
#         index_html = file.read()
#     return render_template_string(index_html)

# @app.route('/style.css')
# def css():
#     return send_from_directory('.', 'style.css')

# @app.route('/recommend', methods=['POST'])
# def recommend():
#     try:
#         request_data = request.get_json()
#         song_name = request_data.get('song')  # Get the 'song' key from the request JSON
#         artist_name = request_data.get('artist')  # Get the 'artist' key from the request JSON

#         # Ensure the song name and artist exist in the dataset
#         song_row = data[(data['name'] == song_name) & (data['artists'] == artist_name)]
#         if song_row.empty:
#             return jsonify({"error": "Song by specified artist not found"}), 404

#         # Generate the searched song embedding
#         searched_song_embedding = song_row['embed_track'].values[0]

#         # Generate recommendations
#         recommendations_df = generate_recommendation_list(song_row,top_n=5)

#         # Structure the response
#         recommendations = {
#             'searched_song_code': searched_song_embedding,
#             'KNN': recommendations_df['KNN'].dropna().tolist(),
#             'KNN_Code': recommendations_df['KNN_Code'].dropna().tolist(),
#             'Autoencoder': recommendations_df['Autoencoder'].dropna().tolist(),
#             'Autoencoder_Code': recommendations_df['Autoencoder_Code'].dropna().tolist(),
#             'RandomForest': recommendations_df['RandomForest'].dropna().tolist(),
#             'RandomForest_Code': recommendations_df['RandomForest_Code'].dropna().tolist()
#         }

#         print(f"Recommendations: {recommendations}")
#         return jsonify(recommendations)
#     except Exception as e:
#         print("Error occurred: ", e)
#         print(traceback.format_exc())
#         return jsonify({"error": str(e)}), 500


# @app.route('/suggestions', methods=['GET'])
# def suggestions():
#     query = request.args.get('query', '').strip().lower()

#     # Search for matches in either song name or any artist in the 'artists' list
#     results = data[
#         data['name'].str.contains(query, case=False) | 
#         data['artists'].apply(lambda artists: any(query in artist.lower() for artist in artists) if isinstance(artists, list) else query in artists.lower())
#     ][['name', 'artists']].head(30)
    
#     # Format the suggestions as "song name by artist name(s)"
#     suggestions = results.apply(
#         lambda row: f"{row['name']} by {', '.join(row['artists'])}" if isinstance(row['artists'], list)
#         else f"{row['name']} by {row['artists']}", axis=1
#     ).tolist()
    
#     return jsonify(suggestions)



# if __name__ == "__main__":
#     app.run(debug=False, port=5000)