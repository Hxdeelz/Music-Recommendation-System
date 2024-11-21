from flask import Flask, render_template
from routes.suggestions import suggestions_bp
from routes.recommendations import recommendations_bp
from os import path
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Register blueprints for routes
app.register_blueprint(suggestions_bp)
app.register_blueprint(recommendations_bp)

app.template_folder = path.join('templates')

@app.route('/')
def home():
    # Render the index.html file from the templates folder
    return render_template('index.html')

if __name__ == '__main__':
    # Run the app in debug mode for development
    app.run(debug=False, port=5000)
