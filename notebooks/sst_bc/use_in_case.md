# Use the file in a case

A case reads its SST file at run time, so you do **not** need to rebuild the model to change it. You change one setting and check it.

In this chapter you reuse the `f2000.test` case from the [quickstart](../uhpc/quickstart.md), which is already set up and built. For your own experiments later, you will make a separate case for each SST file, so the control and perturbed runs stay apart.

Start this page only after your quickstart run has finished. Check it first:

```bash
cd $MYROOT/cases/f2000.test
squeue -u $USER
grep -E "case.run success|st_archive success" CaseStatus
```

`squeue -u $USER` should print only its header line, which means no job of yours is waiting or running. `grep -E` prints the lines of `CaseStatus` that contain either phrase. You should see one line with `case.run success` and one with `st_archive success`. If either is missing, go back to step 7 of the quickstart.

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

Your file must stay where it is, unchanged, for as long as the case runs. If you change the file, the run uses the changed version from that point on. Make a new file with a new name instead.

## 4. Run a 5-day test with your file

First make sure the case starts again from day 1, rather than continuing from the end of the first run:

```bash
./xmlchange CONTINUE_RUN=FALSE
./xmlquery CONTINUE_RUN
```

`CONTINUE_RUN=FALSE` tells CESM to start a fresh run from the case's start date. It is normally already `FALSE` after a single run, so this line makes sure. `./xmlquery CONTINUE_RUN` should print:

```
	CONTINUE_RUN: FALSE
```

Then submit the case again, exactly as in the quickstart:

```bash
./case.submit -a "--exclude=hpcc03,hpcc04"
```

The case starts again from day 1, now with your SST file. Check on it with `squeue -u $USER`. About 45 minutes after it starts, the list is empty and `cat CaseStatus` ends with `case.run success` and `st_archive success`. Then look for your file name in the data-ocean log:

```bash
zgrep "readstrm) open" $MYROOT/archive/f2000.test/logs/ocn.log.*
```

`zgrep` searches inside compressed (`.gz`) files, like `grep` does for plain files. Each run left one ocean log, so you see one line per run. The last line belongs to the run you just made and should end with `.../sst/sst_example_enso.nc`. The line before it, from the quickstart run, shows the stock HadOIBl file.

Keep a note of which SST file each case used. Open the case's notes file with `nano README.case`, add a line at the bottom such as `SST file: sst_example_enso.nc (idealized El Nino warm patch)`, and save it.

## Where next

This is the end of the worked example and of step 4 of [Over break: what to do, in order](../uhpc/over_break.md). Step 5 is to write down your questions. The **Next** button takes you to [When something goes wrong](../uhpc/when_things_go_wrong.md), the list of fixes for common problems. Everything after that page in the menu is for next term.
