from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from route import Route, Coordinate, RouteSet, reverse_geocode

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# A variable to store the selected options (you can use a database instead)
selected_options = {
    'country': '',
    'selected_categories': [],
    'specific_descriptors': ''
}

import os


def list_sample_html_filenames_in_directory():
    root_directory = os.path.join(os.getcwd(), 'static', 'routeset_631408cd')
    html_filenames = []
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            if file.endswith(".html"):
                # Get the path relative to the 'static' directory
                relative_path = os.path.relpath(os.path.join(root, file), root_directory)
                html_filenames.append("http://127.0.0.1:8001/static/" + "routeset_631408cd/" + relative_path)
    return html_filenames



@app.route('/api/card_data', methods=['POST'])
def get_card_data():
    global selected_options
    try:
        uuids = []
        # Get the data from the request form
        country = request.form.get('country')
        selected_categories = request.form.getlist('categories')  # Use getlist to handle multiple checkboxes
        specific_descriptors = request.form.get('specific_descriptors')

        # Save the data to the selected_options variable
        selected_options['country'] = country
        selected_options['selected_categories'] = selected_categories
        selected_options['specific_descriptors'] = specific_descriptors

        start_location = Coordinate(longitude=-4.4824, latitude=54.1663)
        route_set = RouteSet(start=start_location, distance=2.0, num_routes=2)

        parent_directory = route_set.routeset_directory
        uuids = route_set.generate_routes(save_individual_maps=True)

        paths = [f'{parent_directory}/route{uuid}/{uuid}_webmap.html' for uuid in uuids]
        path_descriptions = [single_route.path_description for single_route in route_set.routes]

        end_coordinates = [r.end for r in route_set.routes]
        destinations = reverse_geocode(end_coordinates)
    except:
        path_descriptions = ["lorem", "ipsum", "fox", "cat", "hungry", "jumped", "tree", "three", "liar", "man"]
        destinations = ["manchester", "york", "newcastle", "leeds", "sheffield", "huddersfield", "durham :(", "london", "glasgow", "twitter"]
        paths = list_sample_html_filenames_in_directory()

    recommendations = []
    for i in range(len(paths)):
        current_recommendation = {"path": paths[i], "destination": destinations[i], "description": path_descriptions[i]}
        recommendations.append(current_recommendation)

    # Convert the HTML content to JSON
    template_json = {'recommendations': recommendations}

    print(template_json)
    return jsonify(template_json)

if __name__ == '__main__':
    app.run()



