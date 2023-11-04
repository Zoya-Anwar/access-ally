import rasterio
from rasterio.warp import transform_geom
from shapely.geometry import Point
from pyproj import CRS, Transformer
from collections import namedtuple
import matplotlib.colors as mcolors

Coordinate = namedtuple('Coordinate', ['longitude', 'latitude'])


def calculate_slopes(point_pairs, dsm_file="data/isle_of_man_DSM.tif"):
    with rasterio.open(dsm_file) as src:
        slopes = []

        # Cache UTM zone and transformer for efficiency
        cached_zone = None
        transformer = None

        for point1, point2 in point_pairs:
            zone = int((point1.longitude + 180) / 6) + 1
            hemisphere = 'north' if point1.latitude >= 0 else 'south'
            utm_crs_code = f"EPSG:326{zone}" if hemisphere == 'north' else f"EPSG:327{zone}"

            if zone != cached_zone:
                transformer = Transformer.from_crs("EPSG:4326", utm_crs_code, always_xy=True)
                cached_zone = zone

            x1_utm, y1_utm = transformer.transform(point1.longitude, point1.latitude)
            x2_utm, y2_utm = transformer.transform(point2.longitude, point2.latitude)

            run = Point(x1_utm, y1_utm).distance(Point(x2_utm, y2_utm))

            pt1_geom = transform_geom('EPSG:4326', src.crs, Point(point1.longitude, point1.latitude).__geo_interface__)
            pt2_geom = transform_geom('EPSG:4326', src.crs, Point(point2.longitude, point2.latitude).__geo_interface__)

            x1, y1 = pt1_geom['coordinates']
            x2, y2 = pt2_geom['coordinates']

            z1 = next(src.sample([(x1, y1)]))[0]
            z2 = next(src.sample([(x2, y2)]))[0]

            rise = z2 - z1
            slope = rise / run

            slopes.append(slope * 100)

        return slopes


import matplotlib.colors as mcolors


def slope_to_color(slope, slope_min=-1, slope_max=1):
    """
    Convert a slope value to a continuous color based on thresholds for easy and medium slopes.
    """
    # Define thresholds for easy, medium, and steep slopes
    easy_slope = 0.03
    medium_slope = 0.05

    # Normalize the slope thresholds to values between 0 and 1
    norm_easy = (easy_slope - slope_min) / (slope_max - slope_min)
    norm_medium = (medium_slope - slope_min) / (slope_max - slope_min)

    # Define the colormap with distinct regions for easy and medium slopes, and a transition for steeper values
    colors = [(0, "green"),
              (norm_easy, "green"),
              (norm_medium, "yellow"),
              (1, "red")]

    cmap = mcolors.LinearSegmentedColormap.from_list("custom_RdYlGn_r", [color for _, color in colors], N=256)

    # Normalize the current slope value to a value between 0 and 1
    norm_slope = (slope - slope_min) / (slope_max - slope_min)
    rgba_color = cmap(norm_slope)  # This returns a tuple (R, G, B, A)

    # Convert the rgba values into a hex color string
    hex_color = mcolors.rgb2hex(rgba_color)
    return hex_color
