import pandas as pd
from flask import Blueprint, request, jsonify
import traceback
from models.recommendation_engine import generate_recommendation_list  

recommendations_bp = Blueprint('recommendations', __name__)

# Load dataset
data = pd.read_csv("data/updated_dataset.csv")  

@recommendations_bp.route('/recommend', methods=['POST'])
def recommend():
    try:
        request_data = request.get_json()
        song_name = request_data.get('song')  # Get the 'song' key from the request JSON
        artist_name = request_data.get('artist')  # Get the 'artist' key from the request JSON

        # Ensure the song name and artist exist in the dataset
        song_row = data[(data['name'] == song_name) & (data['artists'] == artist_name)]
        if song_row.empty:
            return jsonify({"error": "Song by specified artist not found"}), 404

        # Generate the searched song embedding
        searched_song_embedding = song_row['embed_track'].values[0]

        # Generate recommendations
        recommendations_df = generate_recommendation_list(song_row,top_n=5)

        # Structure the response
        recommendations = {
            'searched_song_code': searched_song_embedding,
            'KNN': recommendations_df['KNN'].dropna().tolist(),
            'KNN_Code': recommendations_df['KNN_Code'].dropna().tolist(),
            'Autoencoder': recommendations_df['Autoencoder'].dropna().tolist(),
            'Autoencoder_Code': recommendations_df['Autoencoder_Code'].dropna().tolist(),
            'RandomForest': recommendations_df['RandomForest'].dropna().tolist(),
            'RandomForest_Code': recommendations_df['RandomForest_Code'].dropna().tolist()
        }

        print(f"Recommendations: {recommendations}")
        return jsonify(recommendations)
    except Exception as e:
        print("Error occurred: ", e)
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500
