# UHPC quickstart: your first CESM2 run on Union HPC

This page gets you from a new Union HPC (UHPC) account to a short CESM2 run whose output you can look at. The rest of this tutorial explains each step in detail. It was written by NCAR for its own machines and has been adapted here for UHPC.

```{admonition} Read this first
:class: warning
- UHPC runs **CESM2.1.5** (`release-cesm2.1.5`: cime5.6.49, CAM `cam_cesm2_1_rel_60`, CLM5.0.37). The NCAR tutorial was written for `release-cesm2.1.4`, which is a very small step away.
- The per-user folder layout below (`/usr/local/research/miyawaki/users/$USER`) and the read-only shared CESM code and input data are **planned, not yet set up**. Lines marked **TODO** are not yet confirmed on UHPC.
- Do not submit jobs until Osamu says your account is ready.
```

## 1. Log in

```bash
ssh <your-username>@<TODO-UHPC-login-host>
```

- **TODO:** login host name.
- **TODO:** whether you must be on the campus network or VPN to connect.
- **TODO:** first-login steps (changing the temporary password you received by email).
- Your account is created by the Union HPC administrators (hpcadmin@union.edu). You also need to be in the `res-miyawaki` group before you can read the shared CESM files. **TODO:** confirm how you can check this (for example with `groups`).

## 2. Set up your environment

CESM2 on UHPC uses gcc/gfortran 11.5.0 and OpenMPI 5.0.10. NetCDF, HDF5 and PnetCDF were built by hand under `/usr/local/research/miyawaki/opt/cesm-deps` and are loaded by an `ENV.sh` script. There are no NCAR (Cheyenne/Derecho) modules on UHPC.

```bash
source <TODO-path-to-ENV.sh>        # loads compilers, MPI, NetCDF/HDF5/PnetCDF

# Locations used throughout this tutorial
export CESMROOT=/usr/local/research/miyawaki/cesm/cesm2      # shared CESM2 code (planned read-only for students)
export MYROOT=/usr/local/research/miyawaki/users/$USER       # your own folder (planned, TODO: not yet created)
mkdir -p $MYROOT/cases $MYROOT/scratch $MYROOT/archive
```

- **TODO:** exact path of `ENV.sh`, and whether it also loads the compiler and MPI or you need a `module load` first.
- Outside network access goes through a proxy at `192.168.1.10:8888`. **TODO:** confirm whether `ENV.sh` sets it. If not, and you need to download something:

```bash
export http_proxy=http://192.168.1.10:8888
export https_proxy=http://192.168.1.10:8888
```

You can add these lines to your `~/.bashrc` so you do not have to type them each time you log in.

## 3. Create a small case

The test case is an atmosphere-only run (`F2000climo`) at about 2-degree resolution (`f19_f19_mg17`). This is the setup that has already been run on UHPC.

```bash
cd $CESMROOT/cime/scripts
./create_newcase --case $MYROOT/cases/f2000.test \
                 --compset F2000climo --res f19_f19_mg17 \
                 --output-root $MYROOT/scratch
```

- **TODO:** whether UHPC needs `--machine <name>` here or is detected automatically.
- If `create_newcase` says this compset and grid combination is not scientifically supported, add `--run-unsupported`. **TODO:** confirm.
- There is no `--project` on UHPC.

## 4. Set up and build

```bash
cd $MYROOT/cases/f2000.test
./xmlchange NTASKS=8                        # 8 MPI tasks on one node, as in earlier UHPC runs
./xmlchange STOP_OPTION=ndays,STOP_N=5      # 5 model days
./xmlchange JOB_QUEUE=hpcc                  # Slurm partition for CPU jobs
./xmlchange JOB_WALLCLOCK_TIME=01:00:00
./xmlchange DOUT_S_ROOT=$MYROOT/archive/f2000.test
./case.setup
./case.build
```

- On NCAR machines the build is wrapped in `qcmd --`. On UHPC you run `./case.build` directly. **TODO:** confirm whether builds should run on the login node or inside a Slurm allocation (`srun`).
- Input data (`DIN_LOC_ROOT`, about 23 GB) is shared. Check its location with `./xmlquery DIN_LOC_ROOT`. If the build reports missing input files, ask Osamu rather than downloading them yourself, since the shared input data is planned to be read-only for students. **TODO:** who downloads missing input data and how.

## 5. Submit with Slurm

First check what will be submitted:

```bash
./preview_run
```

CPU jobs on UHPC **must avoid the GPU nodes hpcc03 and hpcc04**. If the `sbatch` command shown by `preview_run` does not already include `--exclude=hpcc03,hpcc04`, add it when you submit:

```bash
./case.submit -a "--exclude=hpcc03,hpcc04"
```

- **TODO:** confirm whether the UHPC machine configuration already adds the exclude.
- **TODO:** which Slurm account to use (`general` or `res-miyawaki`) and how it is set, since UHPC has no CESM `PROJECT` setting.
- A 5-day run costs about 0.5 node-hours. The maximum job length is 3 days, and the default memory is about 2 GB per CPU.

## 6. Check on the job

```bash
squeue -u $USER          # your queued and running jobs (replaces qstat)
cat CaseStatus           # CESM's own record of what happened
sacct -j <jobid>         # accounting information for a finished job
scancel <jobid>          # cancel a job (replaces qdel)
```

## 7. Find the output

```bash
ls $MYROOT/scratch/f2000.test/run              # run directory: logs while running
ls $MYROOT/archive/f2000.test/atm/hist         # history files after short-term archiving
ls $MYROOT/archive/f2000.test/logs             # compressed log files
ls $MYROOT/cases/f2000.test/timing             # model throughput and cost
```

Keep output inside your own folder. Do not write CESM output to a compute node's local `/scratch` disk.

## Where next

- [Differences from the NCAR tutorial](differences.md) lists what changes on UHPC throughout the rest of this tutorial.
- The [CESM Basics](../basics/basics_overview.ipynb) chapter explains each of the steps above.
