from pathlib import Path
import geopandas as gpd

# Load OSM land cover
landcover = gpd.read_file("data/raw/osm_landcover.geojson")

# Ensure geographic CRS
landcover = landcover.to_crs(epsg=4326)

# Keep only high-value natural habitats
core_candidates = landcover[
    (landcover["landuse"].isin(["forest"])) |
    (landcover["natural"].isin(["wood", "wetland", "grassland"]))
]

print("Core habitat candidates:", len(core_candidates))

# Save intermediate result
out_path = Path("data/interim/core_candidates.geojson")
out_path.parent.mkdir(parents=True, exist_ok=True)
core_candidates.to_file(out_path, driver="GeoJSON")

print("Saved core candidates to:", out_path.resolve())

# Reproject to metric CRS (France)
core_candidates_2154 = core_candidates.to_crs(epsg=2154)

out_path = Path("data/interim/core_candidates_2154.geojson")
core_candidates_2154.to_file(out_path, driver="GeoJSON")

print("Reprojected core habitats saved to:", out_path.resolve())

# Dissolve all core habitat polygons into contiguous cores
core_habitats = core_candidates_2154.dissolve()

out_path = Path("data/processed/core_habitats.geojson")
out_path.parent.mkdir(parents=True, exist_ok=True)
core_habitats.to_file(out_path, driver="GeoJSON")

print("Final core habitats saved to:", out_path.resolve())