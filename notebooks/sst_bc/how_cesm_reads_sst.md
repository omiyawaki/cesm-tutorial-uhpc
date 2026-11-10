# How CESM reads SST and sea ice

## The data ocean and prescribed ice

In an `F` compset the ocean component is **DOCN**, the "data ocean". In SST mode (`DOCN_MODE=prescribed`, namelist `datamode = "SSTDATA"`) it reads SST from a file and hands it to the atmosphere. The sea-ice component (CICE in prescribed mode) reads the ice concentration from **the same file**. You change one file, and both SST and ice change.

Your case's compset name shows this. For `F2000climo` it contains `DOCN%DOM` (data ocean) and `CICE%PRES` (prescribed ice).

## What is inside the file

The stock file on UHPC is

```
/usr/local/research/miyawaki/cesm/inputdata/atm/cam/sst/sst_HadOIBl_bc_1.9x2.5_2000climo_c180511.nc
```

It is a 12-month climatology (average of 1995-2005) of the merged Hadley/OI SST and sea-ice data. Its layout:

| Item | Value |
|---|---|
| File format | NetCDF3 classic |
| Dimensions | `time` = 12 (unlimited), `lat` = 96, `lon` = 144 |
| `lat` | -90 to 90 degrees north, 96 points (1.9 degree spacing), south to north |
| `lon` | 0 to 357.5 degrees east, 144 points (2.5 degree spacing) |
| `time` | mid-month days 15.5, 45, 74.5, ... 349.5; units `days since 0000-01-01 00:00:00`; calendar `365_day` |
| `date`, `datesec` | the same times as YYYYMMDD integers (116 = Jan 16) and seconds |
| `SST_cpl` | SST in `deg_C` (degrees Celsius, not kelvin) |
| `ice_cov` | sea-ice concentration as a `fraction` (0 to 1, not percent) |
| `SST_cpl_prediddle`, `ice_cov_prediddle` | the true monthly means (see below) |

There are values everywhere, even over land. The model ignores land points, because a separate ocean mask decides where the ocean is.

## Two versions of each field

Each field comes in two versions: `SST_cpl` and `ice_cov`, which the model reads, and `SST_cpl_prediddle` and `ice_cov_prediddle`, the true monthly means. `make_sst_bc.py` writes both for you, and its `check` command confirms they fit together. You do not need to know more to finish this chapter.

```{dropdown} If you want to know why there are two versions ("diddling")
CESM does not use a month's value for the whole month. It **interpolates linearly in time** between the mid-month values. A straight line between monthly means smooths out the seasonal cycle, so the model's actual monthly average would come out a little too weak at the peaks.

To fix this, the values in `SST_cpl` and `ice_cov` are adjusted ("diddled") so that, after the model interpolates, each month's average comes out equal to the real monthly mean. The real monthly means are kept in the `_prediddle` variables. The model reads only `SST_cpl` and `ice_cov`. The diddled values can fall slightly outside the physical range, for example ice below 0 or SST below the freezing point. That is expected.

`make_sst_bc.py` does this adjustment for you. Its `check` command confirms that, after interpolation, the monthly means in your file match its `_prediddle` values. That check gives the same result on the stock file.
```

## The case settings that point to the file

These settings are in `env_run.xml` in your case directory. You can view them with `./xmlquery` (see [the quickstart](../uhpc/quickstart.md)):

| Setting | What it means | Value in UHPC `F2000climo` cases |
|---|---|---|
| `SSTICE_DATA_FILENAME` | full path of the SST/ice file | the stock HadOIBl file above |
| `SSTICE_GRID_FILENAME` | the grid ("domain") file that describes the data's lat/lon | `.../inputdata/atm/cam/ocnfrac/domain.camocn.1.9x2.5_gx1v6_090403.nc` |
| `SSTICE_YEAR_ALIGN` | model year that lines up with `SSTICE_YEAR_START` | `1` |
| `SSTICE_YEAR_START`, `SSTICE_YEAR_END` | first and last data year to use | `0` and `0` (a climatology repeats one year) |

With a 12-month climatology you only change `SSTICE_DATA_FILENAME`. The grid file stays the same, because your file uses the same 96 x 144 grid: the grid file's `xc`/`yc` match the SST file's `lon`/`lat`. The year settings also stay the same. The year settings matter only for multi-year files, such as a real 1979-2015 SST history, which this tutorial does not make.

When the case is set up, CESM writes these settings into "stream" files. Here is the data-ocean one, `CaseDocs/docn.streams.txt.prescribed`, from a UHPC case using the stock file (shortened):

```xml
<domainInfo>
  <filePath> /usr/local/research/miyawaki/cesm/inputdata/atm/cam/ocnfrac </filePath>
  <fileNames> domain.camocn.1.9x2.5_gx1v6_090403.nc </fileNames>
</domainInfo>
<fieldInfo>
  <variableNames> SST_cpl t </variableNames>
  <filePath> /usr/local/research/miyawaki/cesm/inputdata/atm/cam/sst </filePath>
  <fileNames> sst_HadOIBl_bc_1.9x2.5_2000climo_c180511.nc </fileNames>
</fieldInfo>
```

The data-ocean namelist (`CaseDocs/docn_in`) also shows `datamode = "SSTDATA"`, `taxmode = "cycle"` (repeat the 12 months every year), `tintalgo = "linear"` (linear in time) and `mapalgo = "bilinear"`. The ice namelist (`CaseDocs/ice_in`) has `stream_fldfilename` set to the same file and `stream_fldvarname = "ice_cov"`.

You do not edit these files by hand. Do not use `user_nl_docn` for this either. Change `SSTICE_DATA_FILENAME`, and CESM rewrites the streams when you run `./preview_namelists` or submit.
