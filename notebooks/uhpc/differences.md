# Differences from the NCAR tutorial

The NCAR tutorial was written for NCAR's Cheyenne supercomputer and Casper analysis cluster, which use the PBS scheduler and the GLADE file system. The pages in this tutorial use Union HPC (UHPC) commands and paths.

## Logging in

NCAR users log in to Cheyenne with `ssh` and a two-factor token. On UHPC you use **Open OnDemand** at <https://ondemand.hpc.union.edu> (campus network or Union VPN) in your web browser. Its Shell app replaces the NCAR terminal login, its Files app lets you browse and transfer files, and its Jupyter app replaces NCAR's JupyterHub. The shell is `bash`. See [Open OnDemand and shell basics](ondemand_basics.md). Wherever an NCAR page says to `ssh` to Cheyenne or Casper, use the OnDemand Shell tab instead. Do not use `ssh` from the Mac Terminal app.

## Scheduler: PBS to Slurm

| Task | NCAR (PBS) | UHPC (Slurm) |
|---|---|---|
| Submit a batch script | `qsub script` | `sbatch script` |
| Run a command on a compute node | `qcmd -- command` | `salloc -p hpcc -n 1 -t 01:00:00 --exclude=hpcc03,hpcc04` opens a shell on a compute node; type `exit` to end it |
| List your jobs | `qstat -u $USER` | `squeue -u $USER` |
| Cancel a job | `qdel <jobid>` | `scancel <jobid>` |
| Finished job information | `qhist` | `sacct -j <jobid>` |

CESM's own commands (`./case.submit`, `./case.build`) are the same. CESM translates `./case.submit` into `sbatch` for you.

- **Building:** on NCAR machines you build with `qcmd -- ./case.build`. On UHPC you run `./case.build` on the login node, in the OnDemand Shell inside tmux. The cluster allows builds there with up to 4 parallel jobs, so set `./xmlchange GMAKE_J=4` first (the UHPC default is 8). Other heavy computing and Jupyter are not allowed on the login node. Do not build in Jupyter, which has a 4-hour limit.
- **Partitions:** `hpcc` (nodes hpcc01-04) and `gpu` (hpcc03 and hpcc04). CESM runs on CPUs, so set `JOB_QUEUE=hpcc`.
- **GPU nodes:** CPU jobs must use `--exclude=hpcc03,hpcc04`, for example `./case.submit -a "--exclude=hpcc03,hpcc04"`. CESM does not add this for you, so always pass it.
- **Limits:** maximum job length 3 days (Cheyenne's regular queue was 12 hours), about 2 GB of memory per CPU by default, QOS `normal`.
- **Accounts:** There is no CESM `PROJECT` setting on UHPC, so ignore `--project`, `PROJECT=` and the tutorial project numbers (`UESM0011`, `UESM0012`, `P93300642`). Your jobs use your default Slurm account, `general`, which works for CESM on `hpcc`, so you do not set an account anywhere.
- **Queue names:** wherever the NCAR text has `JOB_QUEUE=regular`, use `JOB_QUEUE=hpcc`. The daily tutorial reservations do not exist on UHPC.

## File system paths

| What | NCAR path | UHPC path |
|---|---|---|
| CESM code (`SRCROOT`) | `/glade/work/$USER/code/my_cesm_code` | `/usr/local/research/miyawaki/cesm/cesm2` (shared; do not change it) |
| Tutorial copy of the code | `/glade/p/cesm/tutorial/cesm2.1_tutorial2022` | same shared tree as above |
| Your cases (`CASEROOT`) | `/glade/work/$USER/cases` or `/glade/u/home/$USER/cases` | `/usr/local/research/miyawaki/users/$USER/cases` |
| Build and run directories | `/glade/scratch/$USER/$CASE` | `/usr/local/research/miyawaki/users/$USER/scratch/$CASE` |
| Short-term archive (`DOUT_S_ROOT`) | `/glade/scratch/$USER/archive/$CASE` | `/usr/local/research/miyawaki/users/$USER/archive/$CASE` |
| Input data (`DIN_LOC_ROOT`) | `/glade/p/cesmdata/cseg/inputdata` | `/usr/local/research/miyawaki/cesm/inputdata` (shared, about 23 GB, only the files for the 2-degree CESM2 setup) |
| Home directory | `/glade/u/home/$USER` | your UHPC home directory (`~`). Keep CESM files out of it |

The UHPC machine configuration points output at folders you cannot write to, so always pass `--output-root /usr/local/research/miyawaki/users/$USER/scratch` to `create_newcase` and set `./xmlchange DOUT_S_ROOT=/usr/local/research/miyawaki/users/$USER/archive/$CASE` (with your case name in place of `$CASE`). Otherwise the build, run and archive folders go to the machine default, which you cannot write to.

The commands in this tutorial use the UHPC paths above. Where a page uses `$DIN_LOC_ROOT`, replace it with the input data path, or set it once with `export DIN_LOC_ROOT=<path>`.

Your folder (`/usr/local/research/miyawaki/users/$USER`) has a soft limit of 300 GB. A 3-month (92-day) `F2000climo` archive is about 4 GB, and the run folder in `scratch` adds about 1.5 GB. Check your usage now and then with `du -sh $MYROOT/*`. Do not delete anything in your folder unless you are told to, and never delete anything in an `archive` folder. Your home folder (`~`) has a 20 GB limit, and each compute node's `/scratch` is local to that node and wiped after 30 days, so do not use either for CESM output.

Some pages use data that exists only on NCAR's GLADE file system, such as tutorial archives under `/glade/p/cesm/tutorial`, the CESM2 Large Ensemble under `/glade/campaign`, chemistry emissions under `/glade/p/acom`, and forcing files in staff home directories. Those pages have a **Skip on UHPC** note at the top. Read them for the ideas, but skip their commands.

The example outputs on the `create_newcase`, `case.setup` and `case.build` pages are from UHPC. Most other example outputs, such as the `case.submit` messages, are from Cheyenne. On UHPC you will see Slurm job IDs and `sbatch` instead of PBS, but the CESM messages are the same.

## Modules and software

- The NCAR (Cheyenne/Derecho) modules do not exist on UHPC, so `module load` lines from the NCAR pages will not work as written. The compilers (gcc/gfortran 11.5.0) and MPI (OpenMPI 5.0.10) are installed, and NetCDF, HDF5 and PnetCDF are installed under `/usr/local/research/miyawaki/opt/cesm-deps`. `source /usr/local/research/miyawaki/opt/cesm-deps/ENV.sh` loads them, including `module load openmpi/5.0.10`. It does not set the web proxy.
- NCO (`ncdiff`, `ncra`, `ncks`, ...), CDO, NCL and `ncview` are **not installed** on UHPC. Use Python (xarray) for the same tasks. `ncdump` is in `/usr/local/research/miyawaki/opt/cesm-deps/bin` and works after `source .../ENV.sh`. The text editors `nano`, `vim` and `emacs` are installed.
- The NCAR tutorial `.profile` and `.tcshrc` files (`/glade/p/cesm/tutorial/...`) do not exist on UHPC. Use the environment lines in the [quickstart](quickstart.md) instead.

## Analysis: Casper and JupyterHub (use Open OnDemand)

NCAR runs its analysis notebooks on the Casper cluster through NCAR's JupyterHub. On UHPC you use the **Jupyter** app in [Open OnDemand](ondemand_basics.md) (<https://ondemand.hpc.union.edu>, campus network or VPN), which runs JupyterLab on a compute node for 1 to 4 hours. Use the read-only `datascience` Python environment (xarray, netCDF4, numpy, scipy, matplotlib, dask and cftime). It does **not** have cartopy, so map projections and coastlines from the NCAR notebooks will not work as written. Plain `pcolormesh` maps do work. In the Jupyter form, leave **Conda environment** as `datascience`. Its kernel is called **Python 3 (ipykernel)**. To make a personal environment with cartopy, see the last section of [Open OnDemand and shell basics](ondemand_basics.md). Dask examples that start NCAR's PBS cluster do not apply.

## Input data downloads and the proxy

- Outside network access from UHPC goes through a web proxy. The cluster sets `http_proxy` and `https_proxy` for you at login, so downloads with `wget`, `pip` and the ERA5 script work without any setup.
- CESM input data downloads work over **HTTPS with wget**. FTP and svn do not work.
- Downloads from one NCAR data server (`osdf-data.gdex.ucar.edu`) can fail with an SSL certificate error. If a download from it fails, email me the exact message instead of working around it.
- The shared input data already has every file the cases in this tutorial need. Do not run `./check_input_data --download` yourself. If a case you design later needs a file that is missing, email me the exact message (see [Getting started on Union HPC](start_here.md)), and I will add the file to the shared input data.

## Downloading the code

The NCAR tutorial has each user clone CESM with git. On UHPC everyone uses the shared, already-configured CESM2.1.5 tree, so you do **not** download CESM. If you clone a personal copy, it will not have the UHPC machine settings unless you copy them in.

## Compute cost and sharing

- UHPC is shared with other users. An `F2000climo` run at `f19_f19_mg17` with 8 tasks on one node takes about 45 minutes for 5 model days.
- NCAR's tutorial uses the fully coupled `B1850` compset, which is much more expensive. This tutorial uses `F2000climo` throughout.
- Start with short tests (5 days), and check `squeue` before submitting so other users can still run.
