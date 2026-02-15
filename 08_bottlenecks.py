from pathlib import Path
import geopandas as gpd
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Use the NON-dissolved variable buffers (has buf_m per corridor)
IN_PATH = PROJECT_ROOT / "data/processed/corridors_buffer_variable.gpkg"

OUT_BOTTLENECKS = PROJECT_ROOT / "data/processed/corridor_bottlenecks.gpkg"
OUT_BOTTLENECKS_DISS = PROJECT_ROOT / "data/processed/corridor_bottlenecks_dissolved.gpkg"


def main():
    gdf = gpd.read_file(IN_PATH).to_crs(2154)

    if "buf_m" not in gdf.columns:
        raise ValueError("No 'buf_m' column found. Use corridors_buffer_variable.gpkg (non-dissolved).")

    # Define "narrow" threshold
    # bottom 20% widths
    widths = gdf["buf_m"].astype(float).to_numpy()
    thr = float(np.nanpercentile(widths, 20))  # 20th percentile

    bottlenecks = gdf[gdf["buf_m"] <= thr].copy()

    if bottlenecks.empty:
        raise ValueError("No bottlenecks found with this threshold. Try 30th percentile or check buf_m range.")

    # Clean geometries 
    bottlenecks["geometry"] = bottlenecks.geometry.buffer(0)

    # Save bottlenecks (individual polygons)
    bottlenecks.to_file(OUT_BOTTLENECKS, driver="GPKG")

    # Dissolve into a single bottleneck layer (clusters)
    bottlenecks_diss = bottlenecks.dissolve()
    bottlenecks_diss.to_file(OUT_BOTTLENECKS_DISS, driver="GPKG")

    print("Saved bottleneck layers:")
    print(f"- Individual: {OUT_BOTTLENECKS}")
    print(f"- Dissolved:  {OUT_BOTTLENECKS_DISS}")
    print(f"\nThreshold used: buf_m <= {thr:.1f} m (20th percentile)")
    print("Sample bottlenecks (lowest widths):")
    print(bottlenecks[["from_id", "to_id", "cost", "buf_m"]].sort_values("buf_m").head(10))


if __name__ == "__main__":
    main()
