from pathlib import Path
import geopandas as gpd
import rasterio
from rasterio import features
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Load resistance polygons (EPSG:2154)
resistance = gpd.read_file(
    PROJECT_ROOT / "data/processed/landcover_resistance.geojson"
)

# Define raster resolution (meters)
resolution = 50  # 50 m grid (reasonable for city scale)

# Raster extent
minx, miny, maxx, maxy = resistance.total_bounds
width = int((maxx - minx) / resolution)
height = int((maxy - miny) / resolution)

transform = rasterio.transform.from_bounds(
    minx, miny, maxx, maxy, width, height
)

# Burn resistance values into raster
shapes = (
    (geom, value)
    for geom, value in zip(resistance.geometry, resistance["resistance"])
)

raster = features.rasterize(
    shapes=shapes,
    out_shape=(height, width),
    fill=20,                # default = high resistance
    transform=transform,
    dtype="float32"
)

# Save raster
out_path = PROJECT_ROOT / "data/processed/resistance.tif"
with rasterio.open(
    out_path,
    "w",
    driver="GTiff",
    height=height,
    width=width,
    count=1,
    dtype=raster.dtype,
    crs="EPSG:2154",
    transform=transform,
) as dst:
    dst.write(raster, 1)

print("Resistance raster saved to:", out_path)
