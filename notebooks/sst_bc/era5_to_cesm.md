# ERA5 to a CESM SST file

In this step you make your own version of the stock SST/ice file, built from ERA5 instead of the Hadley/OI data. The file you make here is your control, the "normal ocean" that every experiment gets compared against. Later you add an anomaly to a copy of it.

All commands run in the OnDemand Shell, inside `tmux`, in your SST folder:

```bash
cd $MYROOT/sst
```

## 1. Download ERA5 monthly SST and sea ice

```bash
$PY make_sst_bc.py download --first-year 1995 --last-year 2005 --out era5_sst_ice_monthly.nc
```

`$PY make_sst_bc.py download` runs the script's `download` step with the Python you chose. This asks the Climate Data Store for ERA5 **monthly averaged** `sea_surface_temperature` and `sea_ice_cover` for 1995-2005, already averaged onto a 1-degree grid. The years match those of the stock file. Your request waits in the CDS queue, sometimes for a while, so don't worry if nothing seems to happen at first. You'll see `status has been updated to accepted`, then `running`, then a download bar, and finally `Wrote era5_sst_ice_monthly.nc` (about 13 MB). Stay inside tmux while you wait, so the download keeps going if the tab closes.

What you downloaded (variable names as ERA5 delivers them):

| Variable | Meaning | Units |
|---|---|---|
| `sst` | sea surface temperature, missing (NaN) over land | K (kelvin) |
| `siconc` | sea-ice concentration | fraction 0-1 |
| `valid_time`, `latitude`, `longitude` | first day of each month; latitude from 90 down to -90; longitude 0-359 | |

## 2. Convert it to the CESM format

```bash
$PY make_sst_bc.py build --era5 era5_sst_ice_monthly.nc --first-year 1995 --last-year 2005 --out sst_era5_f19_clim.nc
```

This is the step that does the real work. It prints `Using 132 months (11 years) of ERA5`, the fraction of land points (34%), then `Wrote sst_era5_f19_clim.nc`. The `build` step does the following.

1. **Average by calendar month.** All Januaries are averaged, then all Februaries, and so on. The result is 12 maps (a climatology).
2. **Convert units.** SST goes from kelvin to degrees Celsius (subtract 273.15), because the CAM file uses `deg_C`. Sea ice is already a fraction from 0 to 1, as CAM expects.
3. **Keep the ocean physical.** No SST colder than -1.8 °C, the freezing point of sea water. Ice is kept between 0 and 1, and missing ice over the ocean is set to 0.
4. **Fill land.** ERA5 has no SST over land, but the CESM file needs a value at every point. Land points are filled with the average of their neighbours, repeated until no gaps are left. The model ignores land, but the filling keeps coastlines from pulling in missing values when the model interpolates.
5. **Regrid to the CESM2 1.9x2.5 grid.** Each CESM grid box gets the area-weighted average of the ERA5 boxes that overlap it (first-order conservative regridding), so averages are preserved. The target `lat`, `lon` and time axis are copied from the stock file on UHPC (the "template").
6. **Adjust for time interpolation.** The monthly means are stored as `SST_cpl_prediddle` and `ice_cov_prediddle`. The adjusted ("diddled") values that CESM reads are stored as `SST_cpl` and `ice_cov` (see [How CESM reads SST and sea ice](how_cesm_reads_sst.md)).
7. **Write the NetCDF file** with the same variable names, units, time axis (`days since 0000-01-01`, `365_day` calendar) and format as the stock file.

## 3. Check the file

```bash
$PY make_sst_bc.py check sst_era5_f19_clim.nc
```

You should see a list of `ok` lines and then `ALL CHECKS PASSED`:

```
ok   lat matches template
ok   lon matches template
ok   time matches template
ok   date matches template
ok   datesec matches template
ok   SST_cpl units = deg_C
ok   ice_cov units = fraction
ok   time units = days since 0000-01-01 00:00:00, calendar = 365_day
     SST (monthly means) -1.80 to 34.40 deg C; ice 0.00 to 1.00
ok   values are physical (SST >= -1.8 C, ice 0-1)
ok   model monthly means match SST_cpl_prediddle at 100.0% of points (need 99%; the stock file gives 99.4%)
ALL CHECKS PASSED
```

If any line is `FAIL`, don't use the file. See [When something goes wrong](../uhpc/when_things_go_wrong.md).

## 4. Look at it

```bash
$PY make_sst_bc.py plot sst_era5_f19_clim.nc --month 8 --compare /usr/local/research/miyawaki/cesm/inputdata/atm/cam/sst/sst_HadOIBl_bc_1.9x2.5_2000climo_c180511.nc --out era5_vs_stock_aug.png
```

This writes a picture with three maps for August: your SST, your sea ice, and your SST minus the stock file's SST. To view it, open the OnDemand **Files** app, click **Change directory**, type `/usr/local/research/miyawaki/users/<your-username>/sst` with your username in place of `<your-username>` (`whoami` in the Shell tab prints it), click **OK**, and click the `.png` file.

What to expect: over the open ocean the two products agree to within about half a degree on average. The root-mean-square difference in August is about 0.3 K over grid boxes that are entirely ocean. Larger differences show up near coasts and sea-ice edges. Over land the maps look blocky and strange. That looks wrong but doesn't matter, because land is filled and the model never uses it.

```{dropdown} If you want to know how the script differs from NCAR's official tool
`make_sst_bc.py` simplifies the official CESM tool (`bcgen`) in two ways. It does not merge several observational products, and it does not apply bcgen's extra limits near the ice edge. For comparison: on the stock file, the script's time-interpolation check reproduces bcgen's monthly means at 99.4% of points, and the remaining 0.6% are the ice-edge points where bcgen applies those limits.
```
