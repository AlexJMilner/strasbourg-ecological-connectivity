from pathlib import Path
import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# PARAMETERS THAT YOU CAN TUNE

MIN_PATCH_HA = 1.0      # remove tiny habitat fragments before building cores
BREAK_METERS = 30       # breaks narrow "corridor-like" connections (20–60m typical)
MIN_CORE_HA = 20.0      # final cores must be at least this size (10–50 ha typical)

in_path = PROJECT_ROOT / "data" / "interim" / "core_candidates_2154.geojson"
if not in_path.exists():
    raise FileNotFoundError(f"Missing input file: {in_path}")

gdf = gpd.read_file(in_path).to_crs(epsg=2154)

# 1) Clean geometry
gdf["geometry"] = gdf.geometry.buffer(0)

# 2) Remove tiny patches (noise)
gdf["area_ha"] = gdf.geometry.area / 10_000
gdf = gdf[gdf["area_ha"] >= MIN_PATCH_HA].copy()

# 3) Break thin connections:
#    - shrink polygons (negative buffer) to disconnect narrow links
#    - explode into separate parts
#    - expand back (positive buffer) to approximate original size
shrunk = gdf.copy()
shrunk["geometry"] = shrunk.geometry.buffer(-BREAK_METERS)

# Remove parts that vanished when shrinking
shrunk = shrunk[~shrunk.is_empty & shrunk.geometry.notna()].copy()

# Explode into separate connected components
shrunk = shrunk.explode(index_parts=False).reset_index(drop=True)

# Grow back
grown = shrunk.copy()
grown["geometry"] = grown.geometry.buffer(BREAK_METERS)

# 4) Dissolve per-part (so each part becomes one polygon)
grown["part_id"] = range(len(grown))
cores = grown.dissolve(by="part_id").reset_index(drop=True)

# 5) Filter final cores by size
cores["area_ha"] = cores.geometry.area / 10_000
cores = cores[cores["area_ha"] >= MIN_CORE_HA].copy()

# Add a stable ID
cores = cores.reset_index(drop=True)
cores["core_id"] = cores.index + 1

out_dir = PROJECT_ROOT / "data" / "processed"
out_dir.mkdir(parents=True, exist_ok=True)

out_path = out_dir / "core_habitats_2154.geojson"
cores.to_file(out_path, driver="GeoJSON")

print("Input candidates:", len(gdf))
print("Output cores:", len(cores))
print("Saved:", out_path.resolve())
print(cores[["core_id", "area_ha"]].sort_values("area_ha", ascending=False).head(10))



