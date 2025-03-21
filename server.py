from flask import Flask, send_from_directory
from flask_cors import CORS
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

# Serve movies.json from the 'data/' folder with today's date
@app.route('/data/movies_<string:date>.json')
def serve_movies(date):
    # Build the path to the file in the 'data/' directory
    file_path = os.path.join(os.getcwd(), 'data', f'movies_{date}.json')
    
    if os.path.exists(file_path):
        return send_from_directory(os.path.join(os.getcwd(), 'data'), f'movies_{date}.json')
    else:
        return f"File movies_{date}.json not found.", 404

if __name__ == '__main__':
    app.run(port=8000)
