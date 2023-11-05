from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from route import Route, Coordinate, RouteSet

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# A variable to store the selected options (you can use a database instead)
selected_options = {
    'country': '',
    'selected_categories': [],
    'specific_descriptors': ''
}

@app.route('/api/card_data', methods=['POST'])
def get_card_data():
    global selected_options
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
    template_json = {'paths': paths}

    return jsonify(template_json)


if __name__ == '__main__':
    app.run()



