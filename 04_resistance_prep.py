from pathlib import Path
import geopandas as gpd

# Project root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Load land cover (OSM)
landcover = gpd.read_file(PROJECT_ROOT / "data/raw/osm_landcover.geojson")
landcover = landcover.to_crs(epsg=2154)

# Load core habitats (metric CRS)
core_habitats = gpd.read_file(PROJECT_ROOT / "data/processed/core_habitats.geojson")

# Add resistance column (default = high resistance)
landcover["resistance"] = 20

# Semi-natural green spaces
landcover.loc[
    landcover["leisure"].isin(["park"]) |
    landcover["landuse"].isin(["grass", "meadow", "recreation_ground"]),
    "resistance"
] = 5

# Core habitats = very low resistance
landcover.loc[
    landcover.geometry.intersects(core_habitats.unary_union),
    "resistance"
] = 1

# Save result
out_path = PROJECT_ROOT / "data/processed/landcover_resistance.geojson"
out_path.parent.mkdir(parents=True, exist_ok=True)
landcover.to_file(out_path, driver="GeoJSON")

print("Resistance layer saved to:", out_path)
