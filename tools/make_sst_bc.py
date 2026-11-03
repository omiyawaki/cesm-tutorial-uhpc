#!/usr/bin/env python3
"""Make a prescribed SST and sea-ice boundary-condition file for CESM2/CAM.

This script turns ERA5 monthly sea surface temperature (SST) and sea-ice
concentration into a 12-month climatology file on the CESM2 f19 (1.9x2.5)
grid, in the same format as the stock CAM file
``sst_HadOIBl_bc_1.9x2.5_2000climo_c180511.nc``. It can then add an idealized
SST anomaly inside a latitude-longitude box.

Steps (one sub-command each):

  download  get ERA5 monthly SST + sea-ice cover from the Copernicus Climate
            Data Store (needs a free CDS account and ~/.cdsapirc)
  build     ERA5 -> CESM: monthly climatology, K -> deg C, ice as fraction,
            -1.8 C floor, fill land, conservative regrid to the template
            grid, "diddle" for linear time interpolation, write NetCDF
  anomaly   add a flat or Gaussian-tapered SST anomaly in a box (open water
            only), keep the file consistent
  check     compare a file with the template (grid, time axis, names, units)
  plot      quick map of SST, ice and (optionally) the difference from
            another file

Needs: numpy, netCDF4, xarray (build), matplotlib (plot), cdsapi (download).
Part of the Union HPC edition of the CESM tutorial (MIT License).
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import warnings

import numpy as np
import netCDF4 as nc

warnings.filterwarnings("ignore", category=DeprecationWarning)  # harmless netCDF4/numpy notices

FREEZE_C = -1.8          # sea-water freezing point used for the SST floor (deg C)
OPEN_WATER = 0.01        # ice fraction below which a point counts as open water
DAYS = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31], float)  # 365-day calendar
DEFAULT_TEMPLATE = ("/usr/local/research/miyawaki/cesm/inputdata/atm/cam/sst/"
                    "sst_HadOIBl_bc_1.9x2.5_2000climo_c180511.nc")


# ---------------------------------------------------------------- helpers
def read_template(path):
    with nc.Dataset(path) as ds:
        t = {k: np.array(ds.variables[k][:]) for k in ("time", "lat", "lon", "date", "datesec")}
        t["attrs"] = {v: {a: ds.variables[v].getncattr(a) for a in ds.variables[v].ncattrs()}
                      for v in ds.variables}
    return t


def interp_matrix(mid_days):
    """W[m, k]: mean over calendar month m of the weight that linear-in-time
    interpolation between the 12 mid-month values (cyclic) gives to value k.
    CESM's data ocean (docn) and prescribed ice interpolate linearly in time,
    so monthly means of the model's SST equal W @ (values in the file)."""
    edges = np.concatenate([[0.0], np.cumsum(DAYS)])
    tt = np.concatenate([mid_days - 365.0, mid_days, mid_days + 365.0])
    W = np.zeros((12, 12))
    step = 0.01
    for m in range(12):
        days = np.arange(edges[m] + step / 2, edges[m + 1], step)
        j = np.searchsorted(tt, days) - 1          # left neighbour index in tt
        f = (days - tt[j]) / (tt[j + 1] - tt[j])  # fraction toward right neighbour
        np.add.at(W[m], j % 12, 1 - f)
        np.add.at(W[m], (j + 1) % 12, f)
        W[m] /= len(days)
    return W


def diddle(means, W):
    """Values to put in the file so the model's monthly means equal `means`
    (the idea of Taylor et al. 2000, used by CESM's bcgen tool; simplified:
    no bounds are enforced, as in the stock files)."""
    shp = means.shape
    return np.linalg.solve(W, means.reshape(12, -1)).reshape(shp)


def fill_land(field):
    """Fill NaNs (land) with the average of neighbouring values, repeated
    until nothing is missing. Lon wraps around; lat does not."""
    f = field.copy()
    for _ in range(2000):
        bad = np.isnan(f)
        if not bad.any():
            return f
        stack = []
        for shift, axis in ((1, -1), (-1, -1), (1, -2), (-1, -2)):
            g = np.roll(f, shift, axis=axis)
            if axis == -2:  # no wrap across the poles
                if shift == 1:
                    g[..., 0, :] = np.nan
                else:
                    g[..., -1, :] = np.nan
            stack.append(g)
        stack = np.array(stack)
        cnt = np.sum(~np.isnan(stack), axis=0)
        avg = np.nansum(stack, axis=0) / np.maximum(cnt, 1)
        f = np.where(bad & (cnt > 0), avg, f)
    raise RuntimeError("fill_land did not converge")


def cell_edges(centers, lo, hi):
    e = np.concatenate([[lo], 0.5 * (centers[1:] + centers[:-1]), [hi]])
    return np.clip(e, lo, hi)


def overlap_weights_lat(src_c, dst_c):
    """Area overlap weights in latitude (uses sin(lat), so cell area is right)."""
    se = np.sin(np.deg2rad(cell_edges(src_c, -90, 90)))
    de = np.sin(np.deg2rad(cell_edges(dst_c, -90, 90)))
    W = np.maximum(0, np.minimum(de[1:, None], se[None, 1:]) - np.maximum(de[:-1, None], se[None, :-1]))
    return W / W.sum(axis=1, keepdims=True)


def overlap_weights_lon(src_c, dst_c):
    """Overlap weights in longitude on a circle (cells may cross 0/360)."""
    sw = np.diff(src_c).mean()
    dw = np.diff(dst_c).mean()
    s0, s1 = src_c - sw / 2, src_c + sw / 2
    d0, d1 = dst_c - dw / 2, dst_c + dw / 2
    W = np.zeros((dst_c.size, src_c.size))
    for shift in (-360.0, 0.0, 360.0):
        W += np.maximum(0, np.minimum(d1[:, None], s1[None, :] + shift) - np.maximum(d0[:, None], s0[None, :] + shift))
    return W / W.sum(axis=1, keepdims=True)


def regrid_conservative(field, src_lat, src_lon, dst_lat, dst_lon):
    """First-order conservative regridding between two regular lat-lon grids."""
    Wy = overlap_weights_lat(src_lat, dst_lat)
    Wx = overlap_weights_lon(src_lon, dst_lon)
    return np.einsum("ij,tjk,lk->til", Wy, field, Wx)


def write_bc(path, tmpl, sst, sst_pre, ice, ice_pre, history):
    """Write a file laid out exactly like the stock CAM SST/ice file."""
    with nc.Dataset(path, "w", format="NETCDF3_CLASSIC") as ds:
        ds.createDimension("time", None)
        ds.createDimension("lat", tmpl["lat"].size)
        ds.createDimension("lon", tmpl["lon"].size)
        spec = [("time", "f8", ("time",)), ("lat", "f8", ("lat",)), ("lon", "f8", ("lon",)),
                ("date", "i4", ("time",)), ("datesec", "i4", ("time",)),
                ("ice_cov", "f4", ("time", "lat", "lon")), ("ice_cov_prediddle", "f4", ("time", "lat", "lon")),
                ("SST_cpl", "f4", ("time", "lat", "lon")), ("SST_cpl_prediddle", "f4", ("time", "lat", "lon"))]
        data = {"time": tmpl["time"], "lat": tmpl["lat"], "lon": tmpl["lon"], "date": tmpl["date"],
                "datesec": tmpl["datesec"], "ice_cov": ice, "ice_cov_prediddle": ice_pre,
                "SST_cpl": sst, "SST_cpl_prediddle": sst_pre}
        for name, typ, dims in spec:
            v = ds.createVariable(name, typ, dims)
            for a, val in tmpl["attrs"].get(name, {}).items():
                v.setncattr(a, val)
            v[:] = data[name]
        ds.setncattr("data_summary", "Climatological SST and ICE boundary dataset for CAM")
        ds.setncattr("history", history)


# ---------------------------------------------------------------- commands
def cmd_download(a):
    import cdsapi
    years = [str(y) for y in range(a.first_year, a.last_year + 1)]
    req = {
        "product_type": ["monthly_averaged_reanalysis"],
        "variable": ["sea_surface_temperature", "sea_ice_cover"],
        "year": years,
        "month": [f"{m:02d}" for m in range(1, 13)],
        "time": ["00:00"],
        "grid": [1.0, 1.0],
        "data_format": "netcdf",
        "download_format": "unarchived",
    }
    print(f"Requesting ERA5 monthly SST and sea-ice cover {years[0]}-{years[-1]} on a 1-degree grid ...")
    cdsapi.Client().retrieve("reanalysis-era5-single-levels-monthly-means", req, a.out)
    print("Wrote", a.out)


def cmd_build(a):
    import xarray as xr
    tmpl = read_template(a.template)
    ds = xr.open_dataset(a.era5)
    tname = "valid_time" if "valid_time" in ds.coords else "time"
    ds = ds.sortby("latitude")                          # ERA5 runs north to south; make it south to north
    yrs = ds[tname].dt.year
    ds = ds.sel({tname: (yrs >= a.first_year) & (yrs <= a.last_year)})
    nyears = len(np.unique(ds[tname].dt.year))
    print(f"Using {ds.sizes[tname]} months ({nyears} years) of ERA5")
    clim = ds.groupby(f"{tname}.month").mean()          # 12 calendar-month averages
    sst = clim["sst"].values.astype(float) - 273.15     # K -> deg C
    ice = clim["siconc"].values.astype(float)            # already a fraction 0-1
    land = np.isnan(sst)                                 # ERA5 has no SST over land
    print(f"Land/missing points on ERA5 grid: {land[0].mean():.0%}")
    ice = np.where(land, np.nan, np.nan_to_num(ice, nan=0.0))
    sst = np.maximum(sst, FREEZE_C)                      # no water colder than freezing
    ice = np.clip(ice, 0.0, 1.0)
    sst, ice = fill_land(sst), fill_land(ice)            # CESM files have values everywhere
    lat, lon = ds["latitude"].values, np.mod(ds["longitude"].values, 360.0)
    order = np.argsort(lon)
    sst, ice, lon = sst[..., order], ice[..., order], lon[order]
    sst_pre = regrid_conservative(sst, lat, lon, tmpl["lat"], tmpl["lon"])
    ice_pre = np.clip(regrid_conservative(ice, lat, lon, tmpl["lat"], tmpl["lon"]), 0, 1)
    sst_pre = np.maximum(sst_pre, FREEZE_C)
    W = interp_matrix(tmpl["time"])
    write_bc(a.out, tmpl, diddle(sst_pre, W), sst_pre, diddle(ice_pre, W), ice_pre,
             f"make_sst_bc.py build: ERA5 monthly SST/siconc {a.first_year}-{a.last_year} "
             f"climatology, deg C, floor {FREEZE_C} C, land filled, conservative regrid to "
             f"template grid, time-diddled for linear interpolation")
    print("Wrote", a.out)


def gaussian_box(lat2d, lon2d, a):
    lon2d = np.mod(lon2d, 360.0)
    inbox = ((lat2d >= a.lat_min) & (lat2d <= a.lat_max) &
             (lon2d >= a.lon_min) & (lon2d <= a.lon_max))
    if a.shape == "flat":
        return np.where(inbox, a.amp, 0.0)
    lat0, lon0 = (a.lat_min + a.lat_max) / 2, (a.lon_min + a.lon_max) / 2
    sy, sx = (a.lat_max - a.lat_min) / 6, (a.lon_max - a.lon_min) / 6   # edges at 3 sigma
    bump = np.exp(-0.5 * (((lat2d - lat0) / sy) ** 2 + ((lon2d - lon0) / sx) ** 2))
    return np.where(inbox, a.amp * bump, 0.0)


def cmd_anomaly(a):
    if not (a.lon_min < a.lon_max and a.lat_min < a.lat_max):
        sys.exit("Need lat-min < lat-max and lon-min < lon-max (longitudes 0-360 E).")
    shutil.copyfile(a.input, a.out)
    with nc.Dataset(a.out, "r+") as ds:
        lat, lon = ds["lat"][:], ds["lon"][:]
        lon2d, lat2d = np.meshgrid(lon, lat)
        dsst = gaussian_box(lat2d, lon2d, a)
        pre_old = np.array(ds["SST_cpl_prediddle"][:], float)
        ice_pre = np.array(ds["ice_cov_prediddle"][:], float)
        open_water = ice_pre < OPEN_WATER                      # leave ice-covered points alone
        pre_new = np.where(open_water, pre_old + dsst[None], pre_old)
        pre_new = np.maximum(pre_new, FREEZE_C)                # still no water below freezing
        change = pre_new - pre_old
        W = interp_matrix(np.array(ds["time"][:]))
        ds["SST_cpl_prediddle"][:] = pre_new
        ds["SST_cpl"][:] = np.array(ds["SST_cpl"][:], float) + diddle(change, W)
        old = ds.getncattr("history") if "history" in ds.ncattrs() else ""
        ds.setncattr("history", (old + "; " if old else "") +
                     f"make_sst_bc.py anomaly: {a.shape} {a.amp:+g} K in "
                     f"{a.lat_min}..{a.lat_max}N, {a.lon_min}..{a.lon_max}E, open water only")
        w = np.cos(np.deg2rad(lat2d))
        m = (np.abs(dsst) > 0) & open_water[7]
        print(f"Box points changed: {int(m.sum())}; largest change {np.abs(change).max():.2f} K; "
              f"area-mean change in box (August) {np.sum(change[7][m] * w[m]) / max(np.sum(w[m]), 1e-9):+.2f} K")
    print("Wrote", a.out)


def cmd_check(a):
    tmpl = read_template(a.template)
    ok = True
    with nc.Dataset(a.file) as ds:
        need = ["time", "lat", "lon", "date", "datesec", "SST_cpl", "SST_cpl_prediddle", "ice_cov", "ice_cov_prediddle"]
        miss = [v for v in need if v not in ds.variables]
        if miss:
            print("FAIL missing variables:", miss); return 1
        for k in ("lat", "lon", "time", "date", "datesec"):
            same = np.array_equal(np.array(ds[k][:]), tmpl[k])
            ok &= same
            print(f"{'ok  ' if same else 'FAIL'} {k} matches template")
        for v in ("SST_cpl", "ice_cov"):
            u = ds[v].getncattr("units")
            good = u == tmpl["attrs"][v]["units"]
            ok &= good
            print(f"{'ok  ' if good else 'FAIL'} {v} units = {u}")
        print(f"ok   time units = {ds['time'].units}, calendar = {ds['time'].calendar}")
        s, i = np.array(ds["SST_cpl_prediddle"][:]), np.array(ds["ice_cov_prediddle"][:])
        print(f"     SST (monthly means) {s.min():.2f} to {s.max():.2f} deg C; ice {i.min():.2f} to {i.max():.2f}")
        good = s.min() >= FREEZE_C - 1e-4 and 0 <= i.min() and i.max() <= 1 and s.max() < 40
        ok &= good
        print(f"{'ok  ' if good else 'FAIL'} values are physical (SST >= {FREEZE_C} C, ice 0-1)")
        W = interp_matrix(np.array(ds["time"][:]))
        back = np.einsum("mk,kij->mij", W, np.array(ds["SST_cpl"][:], float))
        close = float(np.mean(np.abs(back - s) < 0.05))
        good = close >= 0.99
        ok &= good
        print(f"{'ok  ' if good else 'FAIL'} model monthly means match SST_cpl_prediddle at {close:.1%} of points "
              f"(need 99%; the stock file gives 99.4%)")
    print("ALL CHECKS PASSED" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


def cmd_plot(a):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    m = a.month - 1
    with nc.Dataset(a.file) as ds:
        lat, lon = ds["lat"][:], ds["lon"][:]
        sst, ice = ds["SST_cpl_prediddle"][m], ds["ice_cov_prediddle"][m]
    panels = [(sst, "SST (deg C)", "RdYlBu_r", None), (ice, "Sea-ice fraction", "Blues", (0, 1))]
    if a.compare:
        with nc.Dataset(a.compare) as ds:
            diff = sst - ds["SST_cpl_prediddle"][m]
        lim = max(float(np.abs(diff).max()), 0.1)
        panels.append((diff, f"SST difference from {Path(a.compare).name} (K)", "RdBu_r", (-lim, lim)))
    fig, axes = plt.subplots(len(panels), 1, figsize=(8, 3.6 * len(panels)), constrained_layout=True)
    for ax, (f, title, cmap, lims) in zip(np.atleast_1d(axes), panels):
        kw = {} if lims is None else {"vmin": lims[0], "vmax": lims[1]}
        pc = ax.pcolormesh(lon, lat, f, cmap=cmap, shading="auto", **kw)
        ax.set_title(f"{title}, month {a.month}")
        ax.set_xlabel("longitude (deg E)"); ax.set_ylabel("latitude (deg N)")
        fig.colorbar(pc, ax=ax)
    fig.savefig(a.out, dpi=110)
    print("Wrote", a.out)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("download", help="get ERA5 monthly SST and sea ice from the CDS")
    d.add_argument("--first-year", type=int, default=1995)
    d.add_argument("--last-year", type=int, default=2005)
    d.add_argument("--out", default="era5_sst_ice_monthly.nc")
    d.set_defaults(func=cmd_download)

    b = sub.add_parser("build", help="ERA5 -> CESM SST/ice climatology file")
    b.add_argument("--era5", default="era5_sst_ice_monthly.nc")
    b.add_argument("--first-year", type=int, default=1995)
    b.add_argument("--last-year", type=int, default=2005)
    b.add_argument("--template", default=DEFAULT_TEMPLATE)
    b.add_argument("--out", default="sst_era5_f19_clim.nc")
    b.set_defaults(func=cmd_build)

    n = sub.add_parser("anomaly", help="add an SST anomaly in a lat-lon box")
    n.add_argument("--input", default="sst_era5_f19_clim.nc")
    n.add_argument("--out", required=True)
    n.add_argument("--shape", choices=["gaussian", "flat"], default="gaussian")
    n.add_argument("--amp", type=float, required=True, help="anomaly in K (peak value for gaussian)")
    n.add_argument("--lat-min", type=float, required=True)
    n.add_argument("--lat-max", type=float, required=True)
    n.add_argument("--lon-min", type=float, required=True, help="degrees east, 0-360")
    n.add_argument("--lon-max", type=float, required=True, help="degrees east, 0-360")
    n.set_defaults(func=cmd_anomaly)

    c = sub.add_parser("check", help="compare a file with the template")
    c.add_argument("file")
    c.add_argument("--template", default=DEFAULT_TEMPLATE)
    c.set_defaults(func=cmd_check)

    q = sub.add_parser("plot", help="quick map check")
    q.add_argument("file")
    q.add_argument("--month", type=int, default=1)
    q.add_argument("--compare", default=None)
    q.add_argument("--out", default="sst_check.png")
    q.set_defaults(func=cmd_plot)

    a = p.parse_args(argv)
    return a.func(a) or 0


if __name__ == "__main__":
    sys.exit(main())
