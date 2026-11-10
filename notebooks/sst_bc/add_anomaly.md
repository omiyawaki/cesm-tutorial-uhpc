# Add an SST anomaly

Now you change the ocean. You start from your control file `sst_era5_f19_clim.nc` and add an SST anomaly inside a latitude-longitude box. You get a new file, and the control file stays as it was. The difference between a run with the new file and a run with the control file shows the atmosphere's response to that anomaly.

The worked example is an **idealized El Niño-type warm patch** in the central and eastern equatorial Pacific. During El Niño, this part of the ocean is warmer than usual. Forecasters track it with the average SST anomaly in the **Niño 3.4 region** (5°S-5°N, 170°W-120°W), which is about +1 to +2 K in a moderate to strong event.

The example's anomaly peaks at +1.5 K on the equator at 145°W and fades smoothly to almost zero at the edges of a wider box, 10°S-10°N, 170°E-100°W, so it covers the whole Niño 3.4 region. A real El Niño has a more complicated shape that changes from month to month. This one has a fixed shape and is the same in every month. It is only practice for the method.

## 1. Make the file

Type this exact command. It is the anomaly for this tutorial, and the next pages expect the file it makes, `sst_example_enso.nc`.

```bash
cd $MYROOT/sst
$PY make_sst_bc.py anomaly --input sst_era5_f19_clim.nc --out sst_example_enso.nc \
    --shape gaussian --amp 1.5 --lat-min -10 --lat-max 10 --lon-min 170 --lon-max 260
```

The `\` at the end of the first line means "this command continues on the next line". You can also type the whole command on one line without it. You should see something like:

```
Box points changed: 370; largest change 1.44 K; area-mean change in box (August) +0.27 K
Wrote sst_example_enso.nc
```

## 2. What the options mean

| Option | Meaning |
|---|---|
| `--amp 1.5` | size of the anomaly in K. Positive warms, negative cools. For the Gaussian shape this is the peak value at the centre of the box |
| `--lat-min`, `--lat-max` | southern and northern edges of the box, in degrees north (south is negative) |
| `--lon-min`, `--lon-max` | western and eastern edges, in **degrees east from 0 to 360**. To convert a west longitude, subtract it from 360: 100°W = 260°E. So 170 to 260 means 170°E across the date line to 100°W |
| `--shape gaussian` | a smooth bump. It peaks at the box centre and falls to almost zero (about 1% of the peak) at the box edges, so there is no sharp step at the edge |

The Gaussian shape is used because a sudden jump in SST at a box edge creates strong, unrealistic temperature gradients. A smooth bump is gentler on the atmosphere. Because the bump is small near the edges, its **average** over the box is much smaller than its peak: +0.27 K over the whole box here, and about +0.67 K over the Niño 3.4 region. The largest change is 1.44 K, not 1.5 K, because no grid point sits exactly on the equator. Keep this in mind when you compare it with observed anomalies, such as the Niño 3.4 index, which are box averages. To make the Niño 3.4 average larger, raise `--amp`.

```{note}
**After the break.** Over break, use only the command in step 1. The script has one other shape, `--shape flat`, which adds the same `--amp` everywhere in the box (the box average then equals `--amp`). NCAR's CAM challenge exercise 5 uses a flat box like this. The script's code (function `gaussian_box`) is short. To try other shapes, such as a map of observed anomalies, you would change that function. Make a copy of the script under a new name before you change it, so the tutorial steps keep working.
```

## 3. How the file stays consistent

The `anomaly` step does more than add a number:

- **Sea ice is left alone.** The anomaly is added only where the monthly ice fraction is below 0.01 (open water). Ice-covered points keep their SST, so the file never has warm water under sea ice.
- **The freezing floor still applies.** If a cooling anomaly would push SST below -1.8 °C, SST stops at -1.8 °C. The ice is not changed, so a cooling anomaly in this file does not create new sea ice.
- **Both versions of the field are updated.** The anomaly is added to the monthly means (`SST_cpl_prediddle`), and the matching adjustment is added to `SST_cpl`, which the model reads.
- **The file's `history` attribute records what you did.** To see it, run `ncdump -h sst_example_enso.nc | grep history`. `ncdump` is in `/usr/local/research/miyawaki/opt/cesm-deps/bin` and is on your path once you have run the `ENV.sh` line from the quickstart.

Land points inside the box are changed too, but the model ignores land, so this has no effect.

## 4. Check and look at it

```bash
$PY make_sst_bc.py check sst_example_enso.nc
$PY make_sst_bc.py plot sst_example_enso.nc --month 12 --compare sst_era5_f19_clim.nc --out example_anomaly_dec.png
```

The check should end with `ALL CHECKS PASSED`. Open `example_anomaly_dec.png` in the OnDemand **Files** app. December is shown because El Niño events usually peak around then, but this anomaly is the same in every month. The bottom map (difference from the control file) should show one red patch stretched east-west along the equator, centred near 215°E (145°W), and white everywhere else. If the patch is in the wrong place, check the signs of your latitudes and that your longitudes are in degrees east.

```{figure} ../../images/sst_bc/example_anomaly_dec.png
:width: 600px
:alt: Three world maps for December. Top, SST from about -2 °C near the poles to about 30 °C in the tropics. Middle, sea-ice fraction, near 1 around Antarctica and in the Arctic. Bottom, SST difference from the control file, white everywhere except one red oval on the equator centred near 215 degrees east, peaking at about 1.4 K.
Example output of the `plot` command above: December SST and sea ice in `sst_example_enso.nc`, and its difference from the control file `sst_era5_f19_clim.nc`. Your picture should look the same.
```
