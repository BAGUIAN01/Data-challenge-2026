"""Distance from the population to the nearest school, per province."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "outils"))
import chemins
import argparse

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from affine import Affine
from rasterio.features import rasterize
from rasterio.transform import xy
from rasterio.windows import Window
from sklearn.neighbors import BallTree

EARTH_RADIUS_KM = 6371.0


def block_sum(src, factor):
    H, W = src.height, src.width
    h, w = -(-H // factor), -(-W // factor)
    out = np.zeros((h, w), dtype="float64")
    step = factor * 64
    for r0 in range(0, H, step):
        nrows = min(step, H - r0)
        strip = (src.read(1, window=Window(0, r0, W, nrows), masked=True)
                 .filled(0).astype("float64"))
        strip[strip < 0] = 0
        strip = np.pad(strip, ((0, -(-nrows // factor) * factor - nrows), (0, w * factor - W)))
        notebook = strip.shape[0] // factor
        out[r0 // factor: r0 // factor + notebook] = strip.reshape(notebook, factor, w, factor).sum(axis=(1, 3))
    return out, src.transform * Affine.scale(factor)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schools", required=True)
    ap.add_argument("--provinces", required=True)
    ap.add_argument("--province-field", required=True,
                    help="column of the boundaries file holding the province name")
    ap.add_argument("--worldpop", required=True)
    ap.add_argument("--factor", type=int, default=10,
                    help="aggregation factor: 10 turns 100 m pixels into 1 km cells")
    ap.add_argument("--threshold-km", type=float, default=5.0)
    ap.add_argument("--out", default="eloignement_par_province.csv")
    a = ap.parse_args()

    schools = gpd.read_file(a.schools).to_crs(4326)
    schools["geometry"] = schools.geometry.representative_point()
    tree = BallTree(np.radians(np.c_[schools.geometry.y, schools.geometry.x]),
                    metric="haversine")

    with rasterio.open(a.worldpop) as src:
        pop, transform = block_sum(src, a.factor)
        crs = src.crs

    provinces = gpd.read_file(a.provinces).to_crs(crs).reset_index(drop=True)
    zone = rasterize(((geom, i + 1) for i, geom in enumerate(provinces.geometry)),
                     out_shape=pop.shape, transform=transform, fill=0, dtype="int32")

    rows, cols = np.nonzero((pop > 0) & (zone > 0))
    xs, ys = xy(transform, rows, cols)
    centres = gpd.GeoSeries(gpd.points_from_xy(xs, ys), crs=crs).to_crs(4326)
    dist_km = tree.query(np.radians(np.c_[centres.y, centres.x]), k=1)[0][:, 0] * EARTH_RADIUS_KM

    cells = pd.DataFrame({"zone": zone[rows, cols], "pop": pop[rows, cols], "d": dist_km})
    cells["pop_x_d"] = cells["pop"] * cells["d"]
    cells["pop_far"] = cells["pop"] * (cells["d"] > a.threshold_km)
    g = cells.groupby("zone")[["pop", "pop_x_d", "pop_far"]].sum()

    out = pd.DataFrame({
        "province": provinces.loc[g.index - 1, a.province_field].to_numpy(),
        "population": g["pop"].round().astype(int).to_numpy(),
        "distance_moyenne_km": (g["pop_x_d"] / g["pop"]).round(2).to_numpy(),
        f"part_a_plus_de_{a.threshold_km:g}_km": (g["pop_far"] / g["pop"]).round(3).to_numpy(),
    }).sort_values("distance_moyenne_km", ascending=False)
    out.to_csv(a.out, index=False)
    print(out.to_string(index=False))
    print(f"\n{len(schools)} écoles lues, {len(out)} provinces calculées -> {a.out}")


if __name__ == "__main__":
    main()
