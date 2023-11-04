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


class RouteSet:

    def __init__(self, start: Coordinate, distance: float, num_routes: int):
        self.start = start
        self.distance = distance
        self.num_routes = num_routes
        self.routeset_id = f"routeset_{str(uuid.uuid4())[:8]}"
        self.routeset_directory = os.path.join('routesets', self.routeset_id)
        os.makedirs(self.routeset_directory, exist_ok=True)

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
            route = self.fetch_osrm_route(self.start, end)
            route_id = self.save_route(route)
            self.visualize_route(route, end, route_id)

    @staticmethod
    def to_lat_long(coord: Coordinate) -> tuple:
        return (coord.latitude, coord.longitude)

    @staticmethod
    def fetch_osrm_route(start: Coordinate, end: Coordinate, osrm_url: str = 'http://localhost:5000') -> dict:
        coordinates = f"{start.longitude},{start.latitude};{end.longitude},{end.latitude}"
        route_url = f"{osrm_url}/route/v1/walking/{coordinates}?overview=full&geometries=geojson"
        response = requests.get(route_url)
        if response.status_code != 200:
            raise ConnectionError(f"Failed to fetch the route from OSRM. HTTP Status Code: {response.status_code}.")
        return response.json()

    def save_route(self, route: dict) -> str:
        route_uuid = str(uuid.uuid4())[:8]
        route_directory = os.path.join(self.routeset_directory, f"route_{route_uuid}")
        os.makedirs(route_directory, exist_ok=True)
        with open(os.path.join(route_directory, 'route.geojson'), 'w') as f:
            json.dump(route, f)
        return route_uuid

    def visualize_route(self, route: dict, end: Coordinate, route_id: str):
        self.plot_route_on_map(route, self.start, end, route_id)
        selected_basemap = BASEMAPS["OpenStreetMap"]
        self.plot_route_on_map_mpl(route, self.start, end, selected_basemap, route_id)

    def plot_route_on_map(self, route: dict, start: Coordinate, end: Coordinate, route_id: str) -> folium.Map:
        route_coords = [RouteSet.to_lat_long(Coordinate(longitude=coord[0], latitude=coord[1]))
                        for coord in route['routes'][0]['geometry']['coordinates']]
        route_map = folium.Map(location=RouteSet.to_lat_long(start), zoom_start=14)
        folium.TileLayer(tiles=BASEMAPS["OpenStreetMap"]).add_to(route_map)
        folium.PolyLine(route_coords, color='blue', weight=5, opacity=0.7).add_to(route_map)
        folium.Marker(location=RouteSet.to_lat_long(start), popup='Start', icon=folium.Icon(color='green')).add_to(route_map)
        folium.Marker(location=RouteSet.to_lat_long(end), popup='End', icon=folium.Icon(color='red')).add_to(route_map)
        route_directory = os.path.join(self.routeset_directory, f"route_{route_id}")
        route_map.save(os.path.join(route_directory, "route_map.html"))
        return route_map

    def plot_route_on_map_mpl(self, route: dict, start: Coordinate, end: Coordinate, basemap_style: str, route_id: str) -> None:
        fig, ax = plt.subplots(figsize=(8, 8))
        x = [coord[0] for coord in route['routes'][0]['geometry']['coordinates']]
        y = [coord[1] for coord in route['routes'][0]['geometry']['coordinates']]
        ax.plot(x, y, color='blue', linewidth=2)
        ax.scatter(start.longitude, start.latitude, color='green', label='Start')
        ax.scatter(end.longitude, end.latitude, color='red', label='End')
        ax.axis('off')
        buffer = 0.001
        ax.set_xlim(min(x) - buffer, max(x) + buffer)
        ax.set_ylim(min(y) - buffer, max(y) + buffer)
        ctx.add_basemap(ax, crs='EPSG:4326', source=basemap_style)
        plt.tight_layout()
        route_directory = os.path.join(self.routeset_directory, f"route_{route_id}")
        plt.savefig(os.path.join(route_directory, 'route_map_mpl.png'), dpi=150)
        plt.show()


if __name__ == "__main__":
    start_location = Coordinate(longitude=-4.4824, latitude=54.1663)
    route_set = RouteSet(start=start_location, distance=5.0, num_routes=3)
    route_set.generate_routes()
