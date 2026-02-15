from pathlib import Path

import geopandas as gpd
import numpy as np
import rasterio
from shapely.geometry import LineString
from scipy.spatial import distance_matrix
from skimage.graph import route_through_array

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CORES_PATH = PROJECT_ROOT / "data/processed/core_habitats_2154.geojson"
RESISTANCE_PATH = PROJECT_ROOT / "data/processed/resistance.tif"
OUT_PATH = PROJECT_ROOT / "data/processed/least_cost_corridors.gpkg"


def point_to_index(point, transform):
    col, row = ~transform * (point.x, point.y)
    return int(row), int(col)


def index_to_xy(row, col, transform):
    x, y = transform * (col, row)
    return (x, y)


def lcp_indices_and_cost(resistance_arr, src_idx, dst_idx):
    indices, cost = route_through_array(
        resistance_arr,
        src_idx,
        dst_idx,
        fully_connected=True
    )
    return indices, cost


def main():
    # 1) Load cores
    cores = gpd.read_file(CORES_PATH).to_crs(2154)
    cores["area_ha"] = cores.geometry.area / 10_000

    # 2) Choose which cores to connect 
    # Keep "significant" cores then connect each to its 3 nearest neighbors
    significant = cores[cores["area_ha"] >= 15].copy()

    if len(significant) < 2:
        raise ValueError("Not enough significant cores selected. Lower the area_ha threshold.")

    significant["centroid"] = significant.geometry.centroid
    core_pts = significant.set_geometry("centroid")

    # 3) Load resistance raster
    with rasterio.open(RESISTANCE_PATH) as src:
        resistance = src.read(1).astype(np.float32)
        transform = src.transform
        raster_crs = src.crs

    if raster_crs is None or raster_crs.to_epsg() != 2154:
        raise ValueError(f"Resistance raster CRS is not EPSG:2154 (got {raster_crs}).")

    # ensure no zeros (can break “free movement”)
    # resistance[resistance <= 0] = 1

    # 4) Build pair list: 3 nearest neighbors per core
    coords = np.array([(p.x, p.y) for p in core_pts.geometry])
    dist = distance_matrix(coords, coords)

    corridors = []

    for i in range(len(core_pts)):
        # 3 nearest excluding itself
        neigh = np.argsort(dist[i])[1:4]

        for j in neigh:
            p_src = core_pts.geometry.iloc[i]
            p_dst = core_pts.geometry.iloc[j]

            src_idx = point_to_index(p_src, transform)
            dst_idx = point_to_index(p_dst, transform)

            # 5) Least-cost path on raster
            path_idx, cost = lcp_indices_and_cost(resistance, src_idx, dst_idx)

            # Convert raster indices to real coords
            path_coords = [index_to_xy(r, c, transform) for r, c in path_idx]
            geom = LineString(path_coords)

            corridors.append({
                "from_id": int(core_pts.index[i]),
                "to_id": int(core_pts.index[j]),
                "cost": float(cost),
                "geometry": geom
            })

    # 6) Export 
    out = gpd.GeoDataFrame(corridors, crs="EPSG:2154")
    out.to_file(OUT_PATH, driver="GPKG")

    print(f"Saved: {OUT_PATH}")
    print(out[["from_id", "to_id", "cost"]].sort_values("cost").head(10))


if __name__ == "__main__":
    main()
