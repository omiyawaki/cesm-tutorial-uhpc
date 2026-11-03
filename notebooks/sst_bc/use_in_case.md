# Use the file in a case

A case reads its SST file at run time, so you do **not** need to rebuild the model to change it. You change one setting and check it.

You need a case that is already set up and built, for example the `f2000.test` case from the [quickstart](../uhpc/quickstart.md). For a real experiment you make a new case (or a clone, see [create_clone](../basics/cesm_workflow/create_clone.ipynb)) for each SST file, so the control and perturbed runs stay separate.

## 1. Look at the current settings

```bash
cd $MYROOT/cases/f2000.test
./xmlquery SSTICE_DATA_FILENAME,SSTICE_GRID_FILENAME,SSTICE_YEAR_ALIGN,SSTICE_YEAR_START,SSTICE_YEAR_END
```

You should see the stock HadOIBl file, the `domain.camocn.1.9x2.5_gx1v6_090403.nc` grid file, and the year settings `1`, `0`, `0`. **TODO:** confirm these are the defaults for a new `F2000climo` case created by a student. They are the values in the existing UHPC cases.

## 2. Point the case at your file

```bash
./xmlchange SSTICE_DATA_FILENAME=$MYROOT/sst/sst_example_indian_ocean.nc
```

Use the **full path**: `$MYROOT/...` is expanded into a full path when you press Enter. Leave `SSTICE_GRID_FILENAME` and the `SSTICE_YEAR_*` settings unchanged. Your file is on the same grid and is a 12-month climatology, like the stock file.

## 3. Check that CESM picked it up

```bash
./preview_namelists
grep -A2 "<fileNames>" CaseDocs/docn.streams.txt.prescribed
grep stream_fldfilename CaseDocs/ice_in
```

`preview_namelists` rewrites the files in `CaseDocs/`. The first `grep` should show `sst_example_indian_ocean.nc` under the SST `<fileNames>` (the line before it is the grid file). The second should show the full path to your file for the sea ice. If you still see the stock file name, `xmlchange` did not work: run the `xmlquery` line again and look for typing mistakes.

Your file must stay where it is, unchanged, for as long as the case runs. If you change the file, the run uses the changed version from that point on. Make a new file with a new name instead.

## 4. Before submitting

- Run a short test first (5 days, as in the quickstart). In `$MYROOT/scratch/f2000.test/run`, look in the ocean log (`ocn.log.*`) for your file name (**TODO:** confirm which log line shows it).
- Do not submit until Osamu says your account is ready, and ask him before running anything longer than a test.
- Keep a note of which SST file each case used, for example in the case's `README.case` (open it with `nano`).
