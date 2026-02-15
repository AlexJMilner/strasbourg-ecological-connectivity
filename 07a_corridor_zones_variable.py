from pathlib import Path
import geopandas as gpd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]

LCP_PATH = PROJECT_ROOT / "data/processed/least_cost_corridors.gpkg"
OUT_VAR = PROJECT_ROOT / "data/processed/corridors_buffer_variable.gpkg"
OUT_DISS = PROJECT_ROOT / "data/processed/corridors_buffer_variable_dissolved.gpkg"


def main():
    # Load least-cost corridor lines
    gdf = gpd.read_file(LCP_PATH).to_crs(2154)

    if "cost" not in gdf.columns:
        raise ValueError("No 'cost' column found. Your least-cost script must export a 'cost' field.")

    # Convert to numeric
    c = gdf["cost"].astype(float).to_numpy()
    cmin, cmax = np.nanmin(c), np.nanmax(c)
    if cmax == cmin:
        raise ValueError("All costs are identical; cannot create variable widths.")

    # Normalize cost to [0,1]
    norm = (c - cmin) / (cmax - cmin)  # 0=lowest cost, 1=highest cost

    # Buffer width range (meters) — adjust if needed
    min_buf = 80
    max_buf = 350

    # Invert so LOW cost => WIDER corridor
    gdf["buf_m"] = min_buf + (1 - norm) * (max_buf - min_buf)

    # Buffer each corridor with its own width
    gdf["geometry"] = gdf.geometry.buffer(gdf["buf_m"], resolution=20)

    # Save non-dissolved variable corridors
    gdf.to_file(OUT_VAR, driver="GPKG")

    # Dissolve to get one merged corridor belt (optional)
    dissolved = gdf.dissolve()
    dissolved.to_file(OUT_DISS, driver="GPKG")

    print("Saved:")
    print(f"- Variable buffers (individual): {OUT_VAR}")
    print(f"- Variable buffers (dissolved):  {OUT_DISS}")
    print("\nLowest-cost (widest) examples:")
    print(gdf[["from_id", "to_id", "cost", "buf_m"]].sort_values("cost").head(10))


if __name__ == "__main__":
    main()
