import rasterio
from rasterio.warp import transform_geom
from shapely.geometry import Point
from pyproj import CRS, Transformer
from collections import namedtuple
import matplotlib.colors as mcolors

Coordinate = namedtuple('Coordinate', ['longitude', 'latitude'])


def calculate_slope(point1, point2, dsm_file="data/isle_of_man_DSM.tif"):
    """
    Calculate the slope between two lat/lon points from a DSM.

    Parameters:
        dsm_file (str): Path to the DSM file.
        point1 (Coordinate): Coordinate of the first point.
        point2 (Coordinate): Coordinate of the second point.

    Returns:
        float: Slope between the two points (rise over run).
    """

    # Load the DSM
    with rasterio.open(dsm_file) as src:
        # Determine the UTM zone for the region
        zone = int((point1.longitude + 180) / 6) + 1
        hemisphere = 'north' if point1.latitude >= 0 else 'south'
        utm_crs = CRS(f"EPSG:326{zone}") if hemisphere == 'north' else CRS(f"EPSG:327{zone}")

        # Transform points to UTM
        transformer = Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True)
        x1_utm, y1_utm = transformer.transform(point1.longitude, point1.latitude)
        x2_utm, y2_utm = transformer.transform(point2.longitude, point2.latitude)

        # Calculate the "run" or horizontal distance in UTM (meters)
        run = Point(x1_utm, y1_utm).distance(Point(x2_utm, y2_utm))

        # Convert lat/lon to raster's CRS to extract elevation
        pt1_geom = transform_geom('EPSG:4326', src.crs, Point(point1.longitude, point1.latitude).__geo_interface__)
        pt2_geom = transform_geom('EPSG:4326', src.crs, Point(point2.longitude, point2.latitude).__geo_interface__)

        x1, y1 = pt1_geom['coordinates']
        x2, y2 = pt2_geom['coordinates']

        # Extract elevation values at the two points
        z1 = next(src.sample([(x1, y1)]))[0]
        z2 = next(src.sample([(x2, y2)]))[0]

        # Calculate the slope
        rise = z2 - z1
        slope = rise / run

    return slope * 100 # in percent



def slope_to_color(slope, slope_min=-1, slope_max=1):
    """
    Convert a slope value to a continuous color between green (low slope) and red (high slope).
    """
    # Define a colormap that transitions from green to yellow to red
    cmap = mcolors.LinearSegmentedColormap.from_list("RdYlGn_r", ["green", "yellow", "red"], N=256)

    # Normalize the slope value to a value between 0 and 1
    norm_slope = (slope - slope_min) / (slope_max - slope_min)
    rgba_color = cmap(norm_slope)  # This returns a tuple (R, G, B, A)

    # Convert the rgba values into a hex color string
    hex_color = mcolors.rgb2hex(rgba_color)
    return hex_color

if __name__ == '__main__':
    # Example usage
    point1 = Coordinate(longitude=-4.4824, latitude=54.1663)
    point2 = Coordinate(longitude=-4.4664, latitude=54.2103)
    slope = calculate_slope(point1, point2)
    print(f"Slope between points: {slope}")