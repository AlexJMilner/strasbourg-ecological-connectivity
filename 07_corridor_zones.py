from pathlib import Path
import geopandas as gpd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

LCP_PATH = PROJECT_ROOT / "data/processed/least_cost_corridors.gpkg"
OUT_BUFFER = PROJECT_ROOT / "data/processed/corridors_buffer_200m.gpkg"
OUT_FINAL = PROJECT_ROOT / "data/processed/corridors_final.gpkg"


def main():
    # 1) Load least-cost paths
    corridors = gpd.read_file(LCP_PATH).to_crs(2154)

    # Safety check
    if corridors.geometry.iloc[0].geom_type != "LineString":
        raise ValueError("Input layer is not a line layer.")

    # 2) Buffer paths -> corridor zones
    # 200 m a standard urban ecological corridor width
    corridors_buffer = corridors.copy()
    corridors_buffer["geometry"] = corridors_buffer.geometry.buffer(
        distance=200,
        resolution=20
    )

    corridors_buffer.to_file(OUT_BUFFER, driver="GPKG")

    # 3) Dissolve overlapping corridors
    corridors_final = corridors_buffer.dissolve()

    corridors_final.to_file(OUT_FINAL, driver="GPKG")

    print("Corridor zones created:")
    print(f"- Buffered corridors: {OUT_BUFFER}")
    print(f"- Dissolved corridors: {OUT_FINAL}")


if __name__ == "__main__":
    main()

