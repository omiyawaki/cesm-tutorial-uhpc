# Making your own SST boundary conditions

In an `F` compset such as `F2000climo`, the ocean is not simulated. CAM instead reads the sea surface temperature (SST) and sea-ice concentration from a file, month by month. Changing that file is how you run a "what if the ocean were different" experiment.

This chapter is written for UHPC and adds to the NCAR tutorial. It walks you through one path from start to finish:

1. [How CESM reads SST and sea ice](how_cesm_reads_sst.md): what is in the file and which case settings point to it.
2. [Set up Python and an ERA5 account](python_setup.md): a one-time setup.
3. [ERA5 to a CESM SST file](era5_to_cesm.md): download ERA5 monthly SST and sea ice, then turn them into a file on the CESM2 1.9x2.5 grid.
4. [Add an SST anomaly](add_anomaly.md): warm or cool the ocean inside a box.
5. [Use the file in a case](use_in_case.md): point a case at your file and check that CESM picked it up.

All the steps use one script, `make_sst_bc.py`, which is kept in this tutorial's repository under `tools/`. The worked example adds an idealized El Niño-type warm patch to the central and eastern equatorial Pacific. It is a made-up anomaly for practising the method, not a reconstruction of any real El Niño event, and it makes no claim about what such an anomaly does to the climate.

```{admonition} Before you start
:class: warning
- Finish the [UHPC quickstart](../uhpc/quickstart.md) first. You need to be comfortable with the OnDemand Shell, `cd`, `ls` and `nano`.
- Do not submit any runs with your new file until Osamu says your account is ready.
- Lines marked **TODO** have not yet been checked on UHPC.
```
