from pathlib import Path
import geopandas as gpd
import osmnx as ox

# Load Strasbourg boundary
boundary = gpd.read_file("data/raw/strasbourg_boundary.geojson")

# Ensure OSMnx uses same CRS
boundary = boundary.to_crs(epsg=4326)

# Tags defining green / natural areas
tags = {
    "landuse": ["forest", "grass", "meadow", "recreation_ground", "village_green"],
    "natural": ["wood", "grassland", "wetland"],
    "leisure": ["park"]
}

# Download land cover polygons
landcover = ox.features_from_polygon(
    boundary.geometry.iloc[0],
    tags=tags
)

# Keep only polygons
landcover = landcover[landcover.geometry.type.isin(["Polygon", "MultiPolygon"])]

# Save
out_path = Path("data/raw/osm_landcover.geojson")
out_path.parent.mkdir(parents=True, exist_ok=True)
landcover.to_file(out_path, driver="GeoJSON")

print("Land cover saved:", out_path)