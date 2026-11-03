# UHPC quickstart: your first CESM2 run on Union HPC

This page takes you from a new Union HPC (UHPC) account to a short CESM2 run whose output you can look at. Follow it from top to bottom. The rest of this tutorial explains each step in more detail. It was written by NCAR for its own computers and has been adapted here for UHPC.

```{admonition} Read this first
:class: warning
- UHPC runs **CESM2.1.5**. The NCAR tutorial was written for CESM2.1.4, a very small step away.
- The per-user folders below (`/usr/local/research/miyawaki/users/<your-username>`) are **planned, not yet created**. Lines marked **TODO** are not yet confirmed on UHPC.
- Do not submit jobs until Osamu says your account is ready.
```

## 0. One-time first login (already done)

You already logged in once from the Mac Terminal app with `ssh <your-username>@hpcc.union.edu` and set a new password. From now on you use the website instead.

## 1. Open OnDemand and start a shell

1. Connect to campus Wi-Fi or the Union VPN.
2. Go to <https://ondemand.hpc.union.edu> and log in (**TODO:** confirm it takes the same username and password).
3. Open the **Shell** app and start tmux, so your work survives the tab closing:

```bash
tmux new -s cesm
```

If you have not used a command line before, read [Open OnDemand and shell basics](ondemand_basics.md) now. It explains tmux, `cd`, `ls`, `nano`, Tab completion and Ctrl-C, which this page uses. Next time, reconnect with `tmux attach -t cesm`.

## 2. Set up your environment

Type these lines (or paste them with Cmd-V):

```bash
source /usr/local/research/miyawaki/opt/cesm-deps/ENV.sh
export CESMROOT=/usr/local/research/miyawaki/cesm/cesm2
export MYROOT=/usr/local/research/miyawaki/users/$USER
mkdir -p $MYROOT/cases $MYROOT/scratch $MYROOT/archive
ls $MYROOT
```

- `source .../ENV.sh` loads the compiler, MPI and NetCDF libraries that CESM needs (it runs `module load openmpi/5.0.10` for you).
- `CESMROOT` is the shared CESM2 code. Everyone uses the same copy, so you do not download CESM.
- `MYROOT` is your own folder for cases, runs and output. `ls $MYROOT` should list `archive  cases  scratch`.

These settings are forgotten when the shell closes. Add the four lines (all except `mkdir` and `ls`) to the end of `~/.bashrc` so they are set every time:

```bash
nano ~/.bashrc
```

Paste the lines at the bottom, save with **Ctrl-O** then **Enter**, and quit with **Ctrl-X**. Then run `source ~/.bashrc` once.

## 3. Create a small case

The test case is atmosphere-only (`F2000climo`: year-2000 conditions with prescribed sea surface temperatures) at about 2-degree resolution (`f19_f19_mg17`). This setup has already run on UHPC.

```bash
cd $CESMROOT/cime/scripts
./create_newcase --case $MYROOT/cases/f2000.test \
                 --compset F2000climo --res f19_f19_mg17 \
                 --output-root $MYROOT/scratch --run-unsupported
```

`./create_newcase` runs the program `create_newcase` in this folder. The `\` at the end of a line continues the command on the next line. You should see many lines of messages, including `Creating Case directory` followed by your case path. If you see `ERROR`, read that line first.

- `--output-root` puts the build and run folders in your space. Without it, they would go to a default location you cannot write to.
- `--run-unsupported` is needed because NCAR has not officially tested this compset and grid combination. It is the same command used for the earlier UHPC runs.
- UHPC's machine (`union_hpcc`) is detected automatically.

## 4. Configure, set up and build

```bash
cd $MYROOT/cases/f2000.test
./xmlchange NTASKS=8
./xmlchange STOP_OPTION=ndays,STOP_N=5
./xmlchange JOB_QUEUE=hpcc,JOB_WALLCLOCK_TIME=02:00:00
./xmlchange DOUT_S_ROOT=$MYROOT/archive/f2000.test
./xmlchange HIST_OPTION=never,REST_OPTION=ndays,REST_N=5
./xmlchange CLM_FORCE_COLDSTART=on
```

Each `./xmlchange` line changes one or more case settings and prints nothing if it worked. Check any setting with `./xmlquery`, for example `./xmlquery STOP_N`.

- `NTASKS=8`: use 8 processors on one node, as in earlier UHPC runs.
- `STOP_N=5`: run 5 model days.
- `DOUT_S_ROOT`: where finished output is copied. You must set this, because the default points to a folder you cannot write to.
- `HIST_OPTION=never`: stops the coupler from writing extra files during short tests.
- `CLM_FORCE_COLDSTART=on`: start the land model from a simple state. Earlier UHPC test runs needed this. **TODO:** check whether it is still needed.

Next, add the sea-ice settings used in the earlier UHPC runs:

```bash
nano user_nl_cice
```

Go to the bottom of the file and add these four lines:

```
ktherm = 1
tr_pond_lvl = .false.
shortwave = "default"
highfreq = .false.
```

Save with **Ctrl-O**, **Enter**, then quit with **Ctrl-X**. Then:

```bash
./case.setup
./xmlchange GMAKE_J=4
./case.build
```

`./case.setup` takes under a minute and ends with `If an old case build already exists, might want to run 'case.build --clean' before building`. That message is normal. `./case.build` compiles the model and takes a while (**TODO:** how long on UHPC). It ends with `MODEL BUILD HAS FINISHED SUCCESSFULLY`. Stay inside tmux while it runs, so closing the tab does not stop it.

- The build runs on the login computer. The cluster allows this, with up to 4 parallel compile processes, which is what `GMAKE_J=4` sets. Builds are the only heavy work allowed there. Model runs go through `./case.submit`, and Jupyter runs on a compute node.
- Do not build inside Jupyter: Jupyter sessions end after at most 4 hours.
- The shared input data (`DIN_LOC_ROOT=/usr/local/research/miyawaki/cesm/inputdata`) has only the files for this 2-degree setup. If the build or submit reports missing input files, ask Osamu. Do not download them yourself.

## 5. Submit with Slurm

First look at what will be submitted:

```bash
./preview_run
```

Then submit. CPU jobs must stay off the GPU nodes (hpcc03 and hpcc04), and the UHPC settings do not do this for you yet, so always add the exclude:

```bash
./case.submit -a "--exclude=hpcc03,hpcc04"
```

You should see messages that include a job id number for `case.run` (the model) and one for `case.st_archive` (copying the output afterwards). Note the numbers.

- Your jobs use your default Slurm account, `general`, which works for CESM. Once Osamu adds you to the research group, you will add `--account=res-miyawaki` inside the quotes, for example `-a "--exclude=hpcc03,hpcc04 --account=res-miyawaki"`. Until he tells you it is ready (**TODO:** not done yet; it starts working about an hour after he adds you), leave it out, because jobs with it will be rejected.
- A 5-day run takes about half an hour on 8 processors. The maximum job length is 3 days.

## 6. Check on the job

```bash
squeue -u $USER          # your waiting (PD) and running (R) jobs
cat CaseStatus           # CESM's own record of each step
sacct -j <jobid>         # how a finished job ended
scancel <jobid>          # cancel a job
```

When `squeue` shows nothing, the jobs are done. The last lines of `cat CaseStatus` should include `case.run success` and `st_archive success`. If they say `error`, see [Troubleshooting](../troubleshooting/troubleshooting.ipynb).

## 7. Find the output

```bash
ls $MYROOT/scratch/f2000.test/run              # run folder: logs while running
ls $MYROOT/archive/f2000.test/logs             # compressed log files after the run
ls $MYROOT/archive/f2000.test/atm/hist         # atmosphere history files
ls $MYROOT/cases/f2000.test/timing             # speed and cost of the run
```

With `HIST_OPTION=never` and only 5 days, `atm/hist` may contain just one small file, or none. That is fine for a first test. You will turn on monthly output in later chapters. You can also browse these folders in the OnDemand **Files** app.

Keep output in your own folder (`$MYROOT`). Your home folder is limited to 20 GB, and `/scratch` is wiped on each compute node.

The finished archive of a 3-month (92-day) `F2000climo` run with monthly output (history files plus restarts) is about 4 GB. The run folder in `scratch` adds more (**TODO:** not yet measured). The planned 300 GB per student therefore fits dozens of runs, but it is still good practice to tidy up. Now and then, check your usage with `du -sh $MYROOT/*`. Once a run has finished and its archive is in place, delete its run folder with `rm -r $MYROOT/scratch/<casename>` (the build folder in it is only needed if you will run that case again). `rm` deletes for good, with no trash can, so check the path twice. Ask Osamu before deleting or compressing anything in `archive`.

## Where next

- [Open OnDemand and shell basics](ondemand_basics.md): the shell commands and tools used throughout.
- [Differences from the NCAR tutorial](differences.md): what changes on UHPC throughout the rest of this tutorial.
- The [CESM Basics](../basics/basics_overview.ipynb) chapter explains each step above.
- [Making your own SST boundary conditions](../sst_bc/sst_bc.md): how to make your own SST files.
