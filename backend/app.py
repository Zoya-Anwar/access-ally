from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/api/card_data', methods=['GET'])
def get_card_data():
    card_data = [
        {
            "id": 0,
            "name": "Nash",
            "age": 20,
            "src": "path/to/your/image.jpg",
            "bio": "Jack of all, Master of some",
            "genre": ["Metalcore", "Pop", "Rap"],
            "tracks": [
                {
                    "name": "Blood & Water",
                    "artist": "Memphis May Fire",
                    "img": "https://i.scdn.co/image/ab67616d0000b27336daf308de541e4019a82139",
                },
                # Add other tracks
            ],
        },
        # Add other card data
    ]
    return jsonify(card_data)

if __name__ == '__main__':
    app.run()



