import requests
import folium
from collections import namedtuple

# Define a named tuple for coordinates
Coordinate = namedtuple('Coordinate', ['longitude', 'latitude'])

# Utility function to convert (Long, Lat) to (Lat, Long) for folium
def to_lat_long(coord: Coordinate) -> tuple:
    return (coord.latitude, coord.longitude)

def fetch_osrm_route(start: Coordinate, end: Coordinate, osrm_url: str = 'http://localhost:5000') -> dict:
    # Use (Long, Lat) order directly as it's the default
    coordinates = f"{start.longitude},{start.latitude};{end.longitude},{end.latitude}"
    route_url = f"{osrm_url}/route/v1/walking/{coordinates}?overview=full&geometries=geojson"

    response = requests.get(route_url)
    if response.status_code != 200:
        raise ConnectionError(f"Failed to fetch the route from OSRM. HTTP Status Code: {response.status_code}.")

    return response.json()

def plot_route_on_map(route: dict, start: Coordinate, end: Coordinate) -> folium.Map:
    # Convert OSRM's (Long, Lat) coordinates to Folium's (Lat, Long) format
    route_coords = [to_lat_long(Coordinate(longitude=coord[0], latitude=coord[1])) for coord in route['routes'][0]['geometry']['coordinates']]

    # Initialize a folium map centered on the starting point of the route
    route_map = folium.Map(location=to_lat_long(start), zoom_start=14)

    # Add the route line to the map
    folium.PolyLine(
        locations=route_coords,  # Coordinates are now in (Lat, Long) format suitable for folium
        color='blue',
        weight=5,
        opacity=0.7
    ).add_to(route_map)

    # Add markers for start and end points
    folium.Marker(location=to_lat_long(start), popup='Start', icon=folium.Icon(color='green')).add_to(route_map)
    folium.Marker(location=to_lat_long(end), popup='End', icon=folium.Icon(color='red')).add_to(route_map)

    return route_map

# Set start and end locations using (Long, Lat) order by default
start_location = Coordinate(longitude=-4.4824, latitude=54.1663)
end_location = Coordinate(longitude=-4.4938, latitude=54.1562)

# Fetch the route data using the specified start and end points
route_data = fetch_osrm_route(start_location, end_location)

# Plot the fetched route on a folium map
map_with_route = plot_route_on_map(route_data, start_location, end_location)

# Save the generated map visualization to an HTML file
map_with_route.save("route_map.html")
