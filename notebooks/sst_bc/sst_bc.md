# Making your own SST boundary conditions

In an `F` compset such as `F2000climo`, the ocean is not simulated. CAM instead reads the sea surface temperature (SST) and sea-ice concentration from a file, month by month. Changing that file is how you run a "what if the ocean were different" experiment.

All the steps use one script, `make_sst_bc.py`. You copy it from `/usr/local/research/miyawaki/tutorial/tools/` on UHPC in step 2 of [Set up Python and an ERA5 account](python_setup.md). The worked example adds an idealized El Niño-type warm patch to the central and eastern equatorial Pacific. It is a made-up anomaly for practising the method, not a reconstruction of any real El Niño event, and it makes no claim about what such an anomaly does to the climate.

```{admonition} Before you start
:class: warning
- Finish the [UHPC quickstart](../uhpc/quickstart.md) first. This chapter uses its `f2000.test` case and the `MYROOT` and `CESMROOT` settings in your `~/.bashrc`.
- The only run in this chapter is one 5-day test. Do not submit anything longer.
```
