import pandas as pd
from flask import Blueprint, request, jsonify
from rapidfuzz import fuzz, process
import traceback

data = pd.read_csv('data/updated_dataset.csv')

suggestions_bp = Blueprint('suggestions', __name__)

@suggestions_bp.route('/suggestions', methods=['GET'])
def suggestions():
    query = request.args.get('query', '').strip().lower()

    if not query:
        return jsonify([])  # Return empty if no query is provided

    try:
        # Prepare the dataset for fuzzy matching
        song_names = data['name'].fillna('').tolist()
        artists_combined = data['artists'].apply(
            lambda artists: ', '.join(artists) if isinstance(artists, list) else artists
        ).fillna('').tolist()
        
        # Combine song name and artist(s) for better matching context
        combined_entries = [
            f"{song_name} by {artist}" for song_name, artist in zip(song_names, artists_combined)
        ]

        # Use RapidFuzz for fuzzy matching
        matched_results = process.extract(
            query, 
            combined_entries, 
            scorer=fuzz.partial_ratio, 
            limit=50  # Adjust the number of results
        )

        # Extract the top results
        suggestions = [match[0] for match in matched_results if match[1] > 50]  # Filter by match quality
        
        return jsonify(suggestions)

    except Exception as e:
        print("Error:", traceback.format_exc())
        return jsonify({"error": "An error occurred while processing your request."}), 500