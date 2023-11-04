import os
import uuid
import json
import requests
import folium
import matplotlib.pyplot as plt
import contextily as ctx
from collections import namedtuple
import math
import random

BASEMAPS = {
    "OpenStreetMap": ctx.providers.OpenStreetMap.Mapnik,
    "GoogleSatellite": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
}

Coordinate = namedtuple('Coordinate', ['longitude', 'latitude'])

class Route:
    def __init__(self, start: Coordinate, end: Coordinate):
        self.start = start
        self.end = end
        self.data = self.fetch_osrm_route(self.start, self.end)
        self.uuid = str(uuid.uuid4())[:8]
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
        with open(os.path.join(self.directory, f"{self.uuid}_geojson.geojson"), 'w') as f:
            json.dump(self.data, f)

    def visualize_route(self):
        self.plot_route_on_map()
        self.plot_route_on_map_mpl()

    @staticmethod
    def to_lat_long(coord: Coordinate) -> tuple:
        return (coord.latitude, coord.longitude)

    def plot_route_on_map(self):
        route_coords = [Route.to_lat_long(Coordinate(longitude=coord[0], latitude=coord[1])) for coord in self.data['routes'][0]['geometry']['coordinates']]
        route_map = folium.Map(location=Route.to_lat_long(self.start), zoom_start=14)
        folium.TileLayer(tiles=BASEMAPS["OpenStreetMap"]).add_to(route_map)
        folium.PolyLine(route_coords, color='blue', weight=5, opacity=0.7).add_to(route_map)
        folium.Marker(location=Route.to_lat_long(self.start), popup='Start', icon=folium.Icon(color='green')).add_to(route_map)
        folium.Marker(location=Route.to_lat_long(self.end), popup='End', icon=folium.Icon(color='red')).add_to(route_map)
        route_map.save(os.path.join(self.directory, f"{self.uuid}_webmap.html"))

    def plot_route_on_map_mpl(self):
        fig, ax = plt.subplots(figsize=(8, 8))
        x = [coord[0] for coord in self.data['routes'][0]['geometry']['coordinates']]
        y = [coord[1] for coord in self.data['routes'][0]['geometry']['coordinates']]
        ax.plot(x, y, color='blue', linewidth=2)
        ax.scatter(self.start.longitude, self.start.latitude, color='green', label='Start')
        ax.scatter(self.end.longitude, self.end.latitude, color='red', label='End')
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

    def generate_end_points(self):
        delta_lat = self.distance / 111.0
        delta_long = self.distance / (111.0 * math.cos(math.radians(self.start.latitude)))
        angle = 2 * math.pi * random.random()
        d_lat = delta_lat * math.sin(angle)
        d_long = delta_long * math.cos(angle)
        new_lat = self.start.latitude + d_lat
        new_long = self.start.longitude + d_long
        return Coordinate(longitude=new_long, latitude=new_lat)

    def generate_routes(self):
        for _ in range(self.num_routes):
            end = self.generate_end_points()
            route_instance = Route(self.start, end)
            route_instance.save_geojson(self.routeset_directory)
            route_instance.visualize_route()
            self.routes.append(route_instance)


if __name__ == "__main__":
    start_location = Coordinate(longitude=-4.4824, latitude=54.1663)
    route_set = RouteSet(start=start_location, distance=5.0, num_routes=2)
    route_set.generate_routes()
