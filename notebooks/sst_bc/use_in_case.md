# Use the file in a case

A case reads its SST file at run time, so you do **not** need to rebuild the model to change it. You change one setting and check that CESM picked it up.

In this chapter you reuse the `f2000.test` case from the [quickstart](../uhpc/quickstart.md), which is already set up and built. For your own experiments later, you'll make a separate case for each SST file, so the control and perturbed runs stay apart and you can always tell which output came from which file.

Start this page only after your quickstart run has finished. Check it first:

```bash
cd $MYROOT/cases/f2000.test
squeue -u $USER
grep -E "case.run success|st_archive success" CaseStatus
```

`squeue -u $USER` should show no job row under the header, which means no job of yours is waiting or running. `grep -E` prints the lines of `CaseStatus` that contain either phrase. You should see one line with `case.run success` and one with `st_archive success`. If either is missing, go back to step 7 of the quickstart.

## 1. Look at the current settings

```bash
./xmlquery SSTICE_DATA_FILENAME,SSTICE_GRID_FILENAME,SSTICE_YEAR_ALIGN,SSTICE_YEAR_START,SSTICE_YEAR_END
```

You should see the stock HadOIBl file (`.../sst_HadOIBl_bc_1.9x2.5_2000climo_c180511.nc`), the `domain.camocn.1.9x2.5_gx1v6_090403.nc` grid file, and the year settings `1`, `0`, `0`. These are the defaults for every new `F2000climo` case.

## 2. Point the case at your file

```bash
./xmlchange SSTICE_DATA_FILENAME=$MYROOT/sst/sst_example_enso.nc
```

Use the **full path**: `$MYROOT/...` is expanded into a full path when you press Enter. Leave `SSTICE_GRID_FILENAME` and the `SSTICE_YEAR_*` settings unchanged. Your file is on the same grid and is a 12-month climatology, like the stock file.

## 3. Check that CESM picked it up

```bash
./preview_namelists
grep -A2 "<fileNames>" CaseDocs/docn.streams.txt.prescribed
grep stream_fldfilename CaseDocs/ice_in
```

`preview_namelists` rewrites the files in `CaseDocs/`. `grep -A2 "<fileNames>"` prints each line that contains `<fileNames>` and the 2 lines after it (`-A2` means "2 lines after"). The first `grep` should show `sst_example_enso.nc` in the second `<fileNames>` line (the first one is the grid file). The second should show the full path to your file for the sea ice. If you still see the stock file name, `xmlchange` did not work: run the `xmlquery` line again and look for typing mistakes.

This is easy to get wrong later: your file must stay where it is, unchanged, for as long as the case runs. If you change the file, the run uses the changed version from that point on. Make a new file with a new name instead.

## 4. Run a 5-day test with your file

First make sure the case starts again from day 1:

```bash
./xmlchange CONTINUE_RUN=FALSE
./xmlquery CONTINUE_RUN
```

`CONTINUE_RUN=FALSE` tells CESM to start a fresh run from the case's start date. It is normally already `FALSE` after a single run, so this line makes sure. `./xmlquery CONTINUE_RUN` should print:

```
	CONTINUE_RUN: FALSE
```

Before you submit, save a copy of the atmosphere output from your quickstart run. The new run writes a file with the same name, and the archive step would replace the old one, which is the control you'll compare against:

```bash
mkdir -p $MYROOT/analysis
cp $MYROOT/archive/f2000.test/atm/hist/f2000.test.cam.h0.0001-01-01-00000.nc $MYROOT/analysis/control.cam.h0.nc
```

Then submit the case again, exactly as in the quickstart:

```bash
./case.submit -a="--exclude=hpcc03,hpcc04"
```

The case starts again from day 1, now with your SST file. Like before, it may wait in the queue first. Check on it with `squeue -u $USER`. About 45 minutes after it starts, there is no job row under the header and `cat CaseStatus` ends with `case.run success` and `st_archive success`. Then look for your file name in the data-ocean log:

```bash
zgrep "readstrm) open" $MYROOT/archive/f2000.test/logs/ocn.log.*
```

`zgrep` searches inside compressed (`.gz`) files, like `grep` does for plain files. Each run left one ocean log, so you see one line per run. The last line belongs to the run you just made and should end with `.../sst/sst_example_enso.nc`. If it does, CESM ran with an SST file you built yourself, which is what your own experiment will do too. The line before it, from the quickstart run, shows the stock HadOIBl file. If `zgrep` prints nothing, email me the output of `ls $MYROOT/archive/f2000.test/logs`.

Keep a note of which SST file each case used. Months from now, you won't remember. Open the case's notes file, `README.case` in `/usr/local/research/miyawaki/users/<your-username>/cases/f2000.test`, in the file editor ({ref}`Editing text files <uhpc-editing>`). Add a line at the bottom such as `SST file: sst_example_enso.nc (idealized El Nino warm patch)`, and click **Save**.

## 5. Map the response

Now compare the two runs. Both started from the same state on the same day, so the differences between them come from their SST files. Start a Jupyter session as in {ref}`Jupyter <uhpc-jupyter>`, make a new notebook, and type this, with your username in place of `<your-username>` in both paths:

```python
import xarray as xr
import matplotlib.pyplot as plt

ctrl = xr.open_dataset('/usr/local/research/miyawaki/users/<your-username>/analysis/control.cam.h0.nc')
warm = xr.open_dataset('/usr/local/research/miyawaki/users/<your-username>/archive/f2000.test/atm/hist/f2000.test.cam.h0.0001-01-01-00000.nc')

# PRECT is in metres per second; multiply by 1000 * 86400 for mm per day
diff = (warm['PRECT'] - ctrl['PRECT']).mean('time') * 1000 * 86400

plt.figure(figsize=(9, 4))
plt.pcolormesh(ctrl['lon'], ctrl['lat'], diff, cmap='BrBG', vmin=-20, vmax=20)
plt.colorbar(label='Precipitation change (mm/day)')
plt.xlabel('Longitude (degrees east)')
plt.ylabel('Latitude (degrees north)')
plt.title('Warm patch minus control: 5-day mean precipitation')
plt.show()
```

`.mean('time')` averages the five days, and the subtraction gives the warm-patch run minus the control. Green means more rain in the warm-patch run, brown means less.

Look first at the equatorial Pacific between about 180°E and 260°E, where you added the warm water. Warmer water there feeds more rising air and more rain, so you should see a band of green along the equator over the warm patch, often with brown patches just north and south of it where the rain moved away from. Away from the Pacific the map is speckled with green and brown. That's weather: after a few days, the two runs' storms no longer line up, and in 5 days that noise is as large as the signal outside the tropics. Longer runs average it out. To save a run, this tutorial compares against your quickstart run, which used the stock SST file rather than your ERA5 control file, so small differences between the two SST products are mixed in too. The warm patch is much bigger than those differences, so it still stands out. In your own experiments you'll run the ERA5 control file as well, so the only difference between the runs is your anomaly.

```{figure} ../../images/sst_bc/enso_minus_control_prect.png
:width: 650px
:alt: World map of the 5-day mean precipitation difference, warm-patch run minus control. A green band of increased rain lies along the equator in the central and eastern Pacific, with speckled green and brown elsewhere.
Precipitation in the warm-patch run minus the control, averaged over the 5 days, from UHPC test runs. Yours will differ in the speckles but should show the same green band over the warm patch. If you don't see it, email me your map.
```
