import os
import uuid
import json
import requests
import folium
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import contextily as ctx
from collections import namedtuple
import math
import random
import geopandas as gpd
from shapely.geometry import Point
from slope_analysis import calculate_slopes, slope_to_color

BASEMAPS = {
    "OpenStreetMap": ctx.providers.OpenStreetMap.Mapnik,
    "GoogleSatellite": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
}

Coordinate = namedtuple('Coordinate', ['longitude', 'latitude'])


class Route:
    def __init__(self, start: Coordinate, end: Coordinate, parent_routeset=None):
        self.start = start
        self.end = end
        self.parent_routeset = parent_routeset
        self.route_data = self.fetch_osrm_route(self.start, self.end)
        self.route_coords = [(Coordinate(longitude=coord[0], latitude=coord[1])) for coord in self.route_data['routes'][0]['geometry']['coordinates']]
        self.route_segments = [(self.route_coords[i], self.route_coords[i + 1]) for i in range(len(self.route_coords) - 1)]

        self.segment_attributes = {
            'slope': calculate_slopes(self.route_segments)
        }

        self.duration_seconds = self.route_data['routes'][0]['duration']
        self.length_meters = self.route_data['routes'][0]['distance']
        self.uuid = str(uuid.uuid4())[:8]
        self.route_number = len(self.parent_routeset.routes) + 1
        self.directory = None

    @staticmethod
    def fetch_osrm_route(start: Coordinate, end: Coordinate, osrm_url: str = 'http://localhost:5000') -> dict:
        coordinates = f"{start.longitude},{start.latitude};{end.longitude},{end.latitude}"
        route_url = f"{osrm_url}/route/v1/walking/{coordinates}?overview=full&geometries=geojson"
        response = requests.get(route_url)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch the route from OSRM. HTTP Status Code: {response.status_code}.")
        return response.json()

    def save_geojson(self, parent_directory: str):
        self.directory = os.path.join(parent_directory, f"route_{self.uuid}")
        os.makedirs(self.directory, exist_ok=True)
        with open(os.path.join(self.directory, f"{self.uuid}_routeinfo.geojson"), 'w') as f:
            json.dump(self.route_data, f)

    def visualize_route(self):
        if self.parent_routeset:
            self.plot_route_on_map(self.parent_routeset.map)
        else:
            self.plot_route_on_individual_map()

    @staticmethod
    def to_lat_long(coord: Coordinate) -> tuple:
        return (coord.latitude, coord.longitude)

    def plot_route_on_individual_map(self):
        route_map = folium.Map(location=Route.to_lat_long(self.start), zoom_start=14)
        self.plot_route_on_map(route_map)
        route_map.save(os.path.join(self.directory, f"{self.uuid}_webmap.html"))

    def plot_route_on_individual_map(self):
        route_map = folium.Map(location=Route.to_lat_long(self.start), zoom_start=14)
        self.plot_route_on_map(route_map)
        route_map.save(os.path.join(self.directory, f"{self.uuid}_webmap.html"))

    def plot_route_on_map(self, existing_map):
        # Iterate over the segments and their corresponding slopes to plot them
        for segment, slope in zip(self.route_segments, self.segment_attributes['slope']):
            color_for_slope = slope_to_color(slope)  # Convert slope to its corresponding color

            # Ensure each segment is a list of (lat, lon) pairs
            segment_coords = [Route.to_lat_long(point) for point in segment]

            folium.PolyLine(segment_coords, color=color_for_slope, weight=5, opacity=0.7).add_to(existing_map)

        # Add start marker
        folium.Marker(location=Route.to_lat_long(self.start), popup='Start', icon=folium.Icon(color='green')).add_to(
            existing_map)

        # Update popup_content for the end marker
        popup_content = f"Route UUID: {self.uuid}<br>" \
                        f"Route Number: {self.route_number}<br>" \
                        f"Route Length: {self.length_meters} meters<br>" \
                        f"Route Duration: {int(self.duration_seconds // 60)}m {int(self.duration_seconds % 60)}s"
        popup_obj = folium.Popup(popup_content, max_width=300)

        # Add end marker with updated popup
        folium.Marker(location=Route.to_lat_long(self.end), popup=popup_obj, icon=folium.Icon(color='red')).add_to(
            existing_map)

    def generate_route_image(self):
        fig, ax = plt.subplots(figsize=(8, 8))

        # Extract the x and y coordinates
        x = [coord[0] for coord in self.route_data['routes'][0]['geometry']['coordinates']]
        y = [coord[1] for coord in self.route_data['routes'][0]['geometry']['coordinates']]

        # Create a list of lines and colors
        lines = []
        colors = []

        for i in range(len(self.route_segments)):
            segment = self.route_segments[i]
            lines.append(segment)

            slope = self.segment_attributes['slope'][i]
            color = slope_to_color(slope)
            colors.append(color)

        # Create a LineCollection
        lc = LineCollection(lines, colors=colors, linewidths=6)
        ax.add_collection(lc)

        ax.scatter(self.start.longitude, self.start.latitude, color='green', label='Start')
        ax.scatter(self.end.longitude, self.end.latitude, color='red', label='End')

        # The rest of your function remains the same...
        ax.axis('off')
        buffer = 0.001

        x_range = max(x) - min(x)
        y_range = max(y) - min(y)

        if x_range > y_range:
            y_center = (max(y) + min(y)) / 2
            ax.set_xlim(min(x) - buffer, max(x) + buffer)
            ax.set_ylim(y_center - x_range / 2 - buffer, y_center + x_range / 2 + buffer)
        else:
            x_center = (max(x) + min(x)) / 2
            ax.set_ylim(min(y) - buffer, max(y) + buffer)
            ax.set_xlim(x_center - y_range / 2 - buffer, x_center + y_range / 2 + buffer)

        ctx.add_basemap(ax, crs='EPSG:4326', source=BASEMAPS["OpenStreetMap"])
        plt.tight_layout()
        plt.savefig(os.path.join(self.directory, f"{self.uuid}_route_overview.png"), dpi=150)
        plt.show()


class RouteSet:
    def __init__(self, start: Coordinate, distance: float, num_routes: int):
        self.start = start
        self.distance = distance
        self.num_routes = num_routes
        self.routeset_id = f"routeset_{str(uuid.uuid4())[:8]}"
        self.routeset_directory = os.path.join('routesets', self.routeset_id)
        os.makedirs(self.routeset_directory, exist_ok=True)
        self.routes = []
        self.map = folium.Map(location=Route.to_lat_long(self.start), zoom_start=14)
        folium.TileLayer(tiles=BASEMAPS["OpenStreetMap"]).add_to(self.map)

    def generate_end_points(self, polygon_path="data/isle_of_man_polygon.geojson"):
        gdf = gpd.read_file(polygon_path)
        isle_of_man_polygon = gdf.iloc[0].geometry

        points_generated = 0
        while True:
            points_generated += 1
            delta_lat = self.distance / 111.0
            delta_long = self.distance / (111.0 * math.cos(math.radians(self.start.latitude)))
            angle = 2 * math.pi * random.random()
            d_lat = delta_lat * math.sin(angle)
            d_long = delta_long * math.cos(angle)
            new_lat = self.start.latitude + d_lat
            new_long = self.start.longitude + d_long

            # If the generated coordinate is on land, return it
            if Point(new_long, new_lat).within(isle_of_man_polygon):
                return Coordinate(longitude=new_long, latitude=new_lat)

    def generate_routes(self):
        for _ in range(self.num_routes):
            end = self.generate_end_points()
            route_instance = Route(self.start, end, parent_routeset=self)
            route_instance.save_geojson(self.routeset_directory)
            route_instance.visualize_route()
            self.routes.append(route_instance)
        self.save_routeset_map()

    def save_routeset_map(self):
        self.map.save(os.path.join(self.routeset_directory, f"{self.routeset_id}_routeset_summary.html"))



if __name__ == "__main__":
    start_location = Coordinate(longitude=-4.4824, latitude=54.1663)
    route_set = RouteSet(start=start_location, distance=2.0, num_routes=2)
    route_set.generate_routes()
    #route_set.routes[0].generate_route_image()
