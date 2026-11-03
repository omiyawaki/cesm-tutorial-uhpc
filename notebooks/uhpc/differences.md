# Differences from the NCAR tutorial

The NCAR tutorial was written for NCAR's Cheyenne supercomputer and Casper analysis cluster, which use the PBS scheduler and the GLADE file system. This edition has been edited so the commands match Union HPC (UHPC). This page lists what changed, so you can translate anything that was missed. Items marked **TODO** are not yet confirmed on UHPC.

## Logging in

NCAR users log in to Cheyenne with `ssh` and a two-factor token. On UHPC you use **Open OnDemand** at <https://ondemand.hpc.union.edu> (campus network or VPN) in your web browser. Its Shell app replaces the NCAR terminal login, its Files app lets you browse and transfer files, and its Jupyter app replaces NCAR's JupyterHub. The shell is `bash`. See [Open OnDemand and shell basics](ondemand_basics.md). Wherever an NCAR page says to `ssh` to Cheyenne or Casper, open the OnDemand Shell instead.

## Scheduler: PBS to Slurm

| Task | NCAR (PBS) | UHPC (Slurm) |
|---|---|---|
| Submit a batch script | `qsub script` | `sbatch script` |
| Run a command on a compute node | `qcmd -- command` | `srun ...` (**TODO:** confirm how to request an interactive allocation) |
| List your jobs | `qstat -u $USER` | `squeue -u $USER` |
| Cancel a job | `qdel <jobid>` | `scancel <jobid>` |
| Finished job information | `qhist` | `sacct -j <jobid>` |

CESM's own commands (`./case.submit`, `./case.build`) are the same. CESM translates `./case.submit` into `sbatch` for you.

- **Building:** on NCAR machines you build with `qcmd -- ./case.build`. On UHPC you run `./case.build` in the OnDemand Shell inside tmux. Do not build in Jupyter, which has a 4-hour limit. **TODO:** confirm a login-node build is acceptable, or write a batch build job.
- **Partitions:** `hpcc` (nodes hpcc01-04) and `gpu` (hpcc03 and hpcc04). CESM runs on CPUs, so set `JOB_QUEUE=hpcc`.
- **GPU nodes:** CPU jobs must use `--exclude=hpcc03,hpcc04`, for example `./case.submit -a "--exclude=hpcc03,hpcc04"`. The UHPC machine configuration does **not** add this (checked), so always pass it.
- **Limits:** maximum job length 3 days (Cheyenne's regular queue was 12 hours), about 2 GB of memory per CPU by default, QOS `normal`.
- **Accounts:** Slurm accounts are `general` and `res-miyawaki`. There is no CESM `PROJECT` setting on UHPC, so ignore `--project`, `PROJECT=` and the tutorial project numbers (`UESM0011`, `UESM0012`, `P93300642`). New student accounts start with only the `general` account. Once you are added to the research group (**TODO**), add `--account=res-miyawaki` inside the `-a "..."` quotes of `./case.submit`. Osamu will tell you when.
- **Queue names:** wherever the NCAR text says `JOB_QUEUE=regular`, use `JOB_QUEUE=hpcc`. The daily tutorial reservations do not exist on UHPC.

## File system paths

| What | NCAR path | UHPC path |
|---|---|---|
| CESM code (`SRCROOT`) | `/glade/work/$USER/code/my_cesm_code` | `/usr/local/research/miyawaki/cesm/cesm2` (shared; planned read-only for students) |
| Tutorial copy of the code | `/glade/p/cesm/tutorial/cesm2.1_tutorial2022` | same shared tree as above |
| Your cases (`CASEROOT`) | `/glade/work/$USER/cases` or `/glade/u/home/$USER/cases` | `/usr/local/research/miyawaki/users/$USER/cases` (planned) |
| Build and run directories | `/glade/scratch/$USER/$CASE` | `/usr/local/research/miyawaki/users/$USER/scratch/$CASE` (planned) |
| Short-term archive (`DOUT_S_ROOT`) | `/glade/scratch/$USER/archive/$CASE` | `/usr/local/research/miyawaki/users/$USER/archive/$CASE` (planned) |
| Input data (`DIN_LOC_ROOT`) | `/glade/p/cesmdata/cseg/inputdata` | `/usr/local/research/miyawaki/cesm/inputdata` (shared, about 23 GB, only the files for the 2-degree CESM2 setup) |
| Home directory | `/glade/u/home/$USER` | your UHPC home directory (`~`). Keep CESM files out of it |

The UHPC machine configuration points output at Osamu's folders, so always pass `--output-root /usr/local/research/miyawaki/users/$USER/scratch` to `create_newcase` and set `./xmlchange DOUT_S_ROOT=/usr/local/research/miyawaki/users/$USER/archive/$CASE` (with your case name in place of `$CASE`). Otherwise the build, run and archive folders go to the machine default, which you cannot write to.

In this edition, commands that used `/glade/...` paths were changed to the UHPC paths above. Where a page uses `$DIN_LOC_ROOT`, replace it with the input data path, or set it once with `export DIN_LOC_ROOT=<path>`.

The per-user folders (`/usr/local/research/miyawaki/users/$USER`) are a **plan**. **TODO:** create them and set permissions. The group's space is limited to 4.9 TB in total, and a soft limit of about 300 GB per student is planned but not yet decided. Your home folder (`~`) has a 20 GB limit, and each compute node's `/scratch` is local to that node and wiped after 30 days, so do not use either for CESM output.

Some pages use data that exists only on NCAR's GLADE file system, such as tutorial archives under `/glade/p/cesm/tutorial`, the CESM2 Large Ensemble under `/glade/campaign`, chemistry emissions under `/glade/p/acom`, and forcing files in staff home directories. Those pages carry a note at the top. **TODO:** copy or download the files you need, or skip those exercises.

The example outputs printed in the pages, such as build logs and `case.submit` messages, are from Cheyenne. On UHPC you will see Slurm job IDs and `sbatch` instead of PBS, but the CESM messages are the same.

## Modules and software

- The NCAR (Cheyenne/Derecho) modules do not exist on UHPC, so `module load` lines from the NCAR pages will not work as written. The compilers (gcc/gfortran 11.5.0) and MPI (OpenMPI 5.0.10) are installed, and NetCDF, HDF5 and PnetCDF were built by hand under `/usr/local/research/miyawaki/opt/cesm-deps`. `source /usr/local/research/miyawaki/opt/cesm-deps/ENV.sh` loads them, including `module load openmpi/5.0.10`. It does not set the web proxy.
- NCO (`ncdiff`, `ncra`, `ncks`, ...), CDO, NCL and `ncview` are **not installed** on UHPC. Use Python (xarray) for the same tasks. `ncdump` is in `/usr/local/research/miyawaki/opt/cesm-deps/bin` and works after `source .../ENV.sh`. The text editors `nano`, `vim` and `emacs` are installed.
- The NCAR tutorial `.profile` and `.tcshrc` files (`/glade/p/cesm/tutorial/...`) do not exist on UHPC. Use the environment lines in the [quickstart](quickstart.md) instead.

## Analysis: Casper and JupyterHub (use Open OnDemand)

NCAR runs its analysis notebooks on the Casper cluster through NCAR's JupyterHub. On UHPC you use the **Jupyter** app in [Open OnDemand](ondemand_basics.md) (<https://ondemand.hpc.union.edu>, campus network or VPN), which runs JupyterLab on a compute node for 1 to 4 hours. Use the read-only `datascience` Python environment (xarray, netCDF4, numpy, scipy, matplotlib, dask, cftime; checked on UHPC). It does **not** have cartopy, so map projections and coastlines from the NCAR notebooks will not work as written. Plain `pcolormesh` maps do work. **TODO:** how to select the `datascience` kernel in OnDemand Jupyter, and how to make a personal environment with cartopy (for example `module load python/miniforge`, then `conda create` through the proxy). Dask examples that start NCAR's PBS cluster do not apply.

## Input data downloads and the proxy

- Outside network access from UHPC goes through a proxy at `192.168.1.10:8888` (set `http_proxy` and `https_proxy`, see the [quickstart](quickstart.md)).
- CESM input data downloads work over **HTTPS with wget**. FTP and svn do not work.
- One NCAR data server (`osdf-data.gdex.ucar.edu`) failed with an expired SSL certificate when this was checked. **TODO:** recheck.
- Because the shared input data is planned to be read-only for students, ask Osamu before running `./check_input_data --download`. **TODO:** agree how missing files get added.

## Downloading the code

The NCAR tutorial has each user clone CESM with git. On UHPC everyone uses the shared, already-configured CESM2.1.5 tree, so you do **not** need to download CESM. You can still follow the download page in your own folder to learn how it works (GitHub access works through the proxy). A personal copy will not have the UHPC machine settings unless you copy them in. You do not need to do this.

## Compute cost and sharing

- UHPC is shared with other users. Earlier runs used `F2000climo` at `f19_f19_mg17` with 8 tasks on one node, and 5 model days cost about 0.5 node-hours.
- The tutorial's fully coupled `B1850` exercises were removed from this edition (see `archive/README.md` in the repository), and the kept exercises were changed to `F2000climo`.
- Start with short tests (5 days), and check `squeue` before submitting so you do not crowd out other users.
