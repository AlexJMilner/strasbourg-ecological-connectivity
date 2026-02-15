from pathlib import Path
import osmnx as ox

# Strasbourg
place_name = "Strasbourg, France"

gdf = ox.geocode_to_gdf(place_name)

print(gdf.crs)
print(gdf.geometry)

out_path = Path("data/raw/strasbourg_boundary.geojson")
out_path.parent.mkdir(parents=True, exist_ok=True)

gdf.to_file(out_path, driver="GeoJSON")
print("Saved to:", out_path.resolve())

