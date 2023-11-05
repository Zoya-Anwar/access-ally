from flask import Flask, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/api/card_data', methods=['POST'])
def get_card_data():
    with open('routesets/routeset_3d068197/route_98d2795a/98d2795a_webmap.html', 'r') as file:
        template_content = file.read()

    # Convert the HTML content to JSON
    template_json = {'html_content': str(template_content)}

    return jsonify(template_json)

@app.route('/show_card')
def show():
    return render_template('routesets/routeset_3d068197/route_98d2795a/map.html')

if __name__ == '__main__':
    app.run()


