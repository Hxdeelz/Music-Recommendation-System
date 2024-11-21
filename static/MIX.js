function fetchSuggestions() {
    const query = document.getElementById('song-name').value;
    const suggestionsDiv = document.getElementById('suggestions');

    if (query.length > 0) {
        fetch(`http://127.0.0.1:5000/suggestions?query=${query}`)
            .then(response => response.json())
            .then(data => {
                suggestionsDiv.innerHTML = '';
                if (data.length > 0) {
                    suggestionsDiv.style.display = 'block';
                    data.forEach(song => {
                        const suggestionElement = document.createElement('div');
                        suggestionElement.textContent = song;
                        suggestionElement.onclick = () => {
                            document.getElementById('song-name').value = song
                            suggestionsDiv.innerHTML = '';
                            suggestionsDiv.style.display = 'none';
                        };
                        suggestionsDiv.appendChild(suggestionElement);
                    });
                } else {
                    suggestionsDiv.style.display = 'none';
                }
            })
            .catch(error => console.error('Error fetching suggestions:', error));
    } else {
        suggestionsDiv.innerHTML = '';
        suggestionsDiv.style.display = 'none';
    }
}



function getRecommendations() {
    const input = document.getElementById('song-name').value;
    const [songName, artistName] = input.split(" by ").map(item => item.trim()); // Split by " by "

    fetch('http://127.0.0.1:5000/recommend', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ song: songName, artist: artistName || "" })
    })
        .then(response => response.json())
        .then(data => {
            const searchedSongEmbeddingDiv = document.getElementById('searched-song-embedding');
            const knnEmbeddedTracksDiv = document.getElementById('knn-embedded-tracks');
            const autoencoderEmbeddedTracksDiv = document.getElementById('autoencoder-embedded-tracks');
            const rfEmbeddedTracksDiv = document.getElementById('rf-embedded-tracks');

            searchedSongEmbeddingDiv.innerHTML = '';
            knnEmbeddedTracksDiv.innerHTML = '';
            autoencoderEmbeddedTracksDiv.innerHTML = '';
            rfEmbeddedTracksDiv.innerHTML = '';

            if (data.searched_song_code) {
                const searchedSongEmbedding = document.createElement('div');
                searchedSongEmbedding.innerHTML = data.searched_song_code;
                searchedSongEmbedding.classList.add('embedded-track', 'searched-track');
                searchedSongEmbeddingDiv.appendChild(searchedSongEmbedding);
            }

            if (Object.keys(data).length > 0) {
                const knnCodes = data.KNN_Code;
                const autoCodes = data.Autoencoder_Code;
                const rfCodes = data.RandomForest_Code;

                knnCodes.forEach((code) => {
                    const iframeElement = document.createElement('div');
                    iframeElement.innerHTML = code;
                    iframeElement.classList.add('embedded-track');
                    knnEmbeddedTracksDiv.appendChild(iframeElement);
                });

                autoCodes.forEach((code) => {
                    const iframeElement = document.createElement('div');
                    iframeElement.innerHTML = code;
                    iframeElement.classList.add('embedded-track');
                    autoencoderEmbeddedTracksDiv.appendChild(iframeElement);
                });

                rfCodes.forEach((code) => {
                    const iframeElement = document.createElement('div');
                    iframeElement.innerHTML = code;
                    iframeElement.classList.add('embedded-track');
                    rfEmbeddedTracksDiv.appendChild(iframeElement);
                });
            } else {
                knnEmbeddedTracksDiv.innerHTML += '<p>No recommendations found</p>';
                autoencoderEmbeddedTracksDiv.innerHTML += '<p>No recommendations found</p>';
                rfEmbeddedTracksDiv.innerHTML += '<p>No recommendations found</p>';
            }
        })
        .catch(error => console.error('Error:', error));
}
let focusedIndex = -1; // Declare focusedIndex globally to persist across events

document.getElementById('song-name').addEventListener('keydown', function (event) {
    const suggestionsDiv = document.getElementById('suggestions');
    const suggestions = Array.from(suggestionsDiv.querySelectorAll('div'));

    if (event.key === 'Enter') {
        // Trigger recommendations if Enter is pressed
        event.preventDefault();
        if (focusedIndex >= 0 && focusedIndex < suggestions.length) {
            document.getElementById('song-name').value = suggestions[focusedIndex].textContent; // Set input to selected suggestion
        }
        getRecommendations();
        focusedIndex = -1; // Reset focus after triggering recommendations
        suggestionsDiv.innerHTML = ''; // Clear suggestions
        suggestionsDiv.style.display = 'none';
    } else if (event.key === 'ArrowDown') {
        // Navigate suggestions with ArrowDown
        event.preventDefault();
        if (suggestions.length > 0) {
            focusedIndex = (focusedIndex + 1) % suggestions.length; // Loop to the top
            updateSuggestionFocus(suggestions, focusedIndex);
        }
    } else if (event.key === 'ArrowUp') {
        // Navigate suggestions with ArrowUp
        event.preventDefault();
        if (suggestions.length > 0) {
            focusedIndex = (focusedIndex - 1 + suggestions.length) % suggestions.length; // Loop to the bottom
            updateSuggestionFocus(suggestions, focusedIndex);
        }
    }
});

function updateSuggestionFocus(suggestions, index) {
    suggestions.forEach((suggestion, i) => {
        if (i === index) {
            suggestion.classList.add('focused'); // Highlight the focused suggestion
            suggestion.scrollIntoView({ block: 'nearest' }); // Ensure it's visible
        } else {
            suggestion.classList.remove('focused'); // Remove focus from others
        }
    });
}
document.addEventListener('click', (event) => {
    if (!event.target.closest('#suggestions') && !event.target.closest('#song-name')) {
        document.getElementById('suggestions').style.display = 'none';
        focusedIndex = -1; // Reset focus
    }
});