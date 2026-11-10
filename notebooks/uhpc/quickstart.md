# UHPC quickstart: your first CESM2 run on Union HPC

This page takes you from your Union HPC (UHPC) account to a short CESM2 run whose output you can look at. Follow it from top to bottom. Read [Open OnDemand and shell basics](ondemand_basics.md) before you start, because this page uses the tools explained there. The rest of this tutorial explains each step in more detail. It was written by NCAR for its own computers and has been adapted here for UHPC, which runs CESM version 2.1.5.

## 0. What you already have

You already have a UHPC account. Your username is the first part of your Union email address (for example `tompkinc`), and your password is the cluster password you used when you first logged in. You do not need the Mac Terminal app for anything in this tutorial.

## 1. Open OnDemand and start a shell

1. Connect to the Union VPN with the **Cisco Secure Client** app (see [Over break: what to do, in order](over_break.md) for the one-time setup). The cluster's website does not load from off campus without it.
2. In Safari or Chrome, go to <https://ondemand.hpc.union.edu>. A small sign-in box appears. Type your cluster username and password.
3. In the top menu, click **Clusters** → **HPC Cluster Shell Access**. A black command-line window opens in a new browser tab.
4. Start tmux, so your work keeps running when the tab closes:

```bash
tmux new -s cesm
```

The next time you come back, type `tmux attach -t cesm` instead.

## 2. Check that your account is ready

```bash
id
```

`id` prints your username and the groups you belong to. The list must include `res-miyawaki`, the research group that owns the CESM files. If it does not, see "Permission denied" in [When something goes wrong](when_things_go_wrong.md).

## 3. Set up your environment

Type these lines, or copy them from this page and paste them into the Shell tab with **Cmd-V**. Press **Enter** after each line.

```bash
source /usr/local/research/miyawaki/opt/cesm-deps/ENV.sh
export CESMROOT=/usr/local/research/miyawaki/cesm/cesm2
export MYROOT=/usr/local/research/miyawaki/users/$USER
mkdir -p $MYROOT/cases $MYROOT/scratch $MYROOT/archive
ls $MYROOT
```

- `source .../ENV.sh` runs the commands in the file `ENV.sh`, which load the compiler, MPI and NetCDF libraries that CESM needs.
- `export CESMROOT=...` saves the location of the shared CESM2 code under the short name `CESMROOT`. Everyone uses the same copy, so you do not download CESM.
- `export MYROOT=...` saves the location of your own folder. `$USER` stands for your username, so you can type the line exactly as shown.
- `mkdir -p` makes the three folders inside it, for cases, run files and finished output.
- `ls $MYROOT` lists what is in your folder. You should see `archive  cases  scratch`.

The shell forgets these settings when it closes. To have them set every time you log in, add the first three lines to the end of the file `~/.bashrc`, which the shell runs at every login:

```bash
nano ~/.bashrc
```

`nano` opens the file in a text editor inside the Shell tab. Press the **down arrow** until the cursor is below the last line, paste the three lines with **Cmd-V**, save with **Ctrl-O** then **Enter**, and quit with **Ctrl-X**. Then run `source ~/.bashrc` once.

## 4. Create a small case

A "case" is a folder that holds the settings for one model experiment. The test case is atmosphere-only (`F2000climo`: year-2000 conditions with prescribed sea surface temperatures) at about 2-degree resolution (`f19_f19_mg17`).

```bash
cd $CESMROOT/cime/scripts
./create_newcase --case $MYROOT/cases/f2000.test \
                 --compset F2000climo --res f19_f19_mg17 \
                 --output-root $MYROOT/scratch --run-unsupported
```

`cd` moves you into the folder that holds CESM's scripts. `./create_newcase` runs the program `create_newcase` in this folder. The `\` at the end of a line continues the command on the next line. You should see many lines of messages, ending with `Creating Case directory /usr/local/research/miyawaki/users/<your-username>/cases/f2000.test` and `Machine is union_hpcc`.

- `--case` is the name and location of the new case folder.
- `--compset` and `--res` choose the model configuration and the grid.
- `--output-root` puts the build and run folders in your own space.
- `--run-unsupported` is needed because NCAR has not officially tested this configuration and grid together.

## 5. Configure, set up and build

```bash
cd $MYROOT/cases/f2000.test
./xmlchange NTASKS=8
./xmlchange STOP_OPTION=ndays,STOP_N=5
./xmlchange JOB_QUEUE=hpcc,JOB_WALLCLOCK_TIME=02:00:00
./xmlchange DOUT_S_ROOT=$MYROOT/archive/f2000.test
./xmlchange HIST_OPTION=never,REST_OPTION=ndays,REST_N=5
```

Each `./xmlchange` line changes one or more case settings and prints nothing if it worked. To read a setting back, use `./xmlquery`, for example `./xmlquery STOP_N`.

- `NTASKS=8`: use 8 processors on one compute node.
- `STOP_OPTION=ndays,STOP_N=5`: run 5 model days.
- `JOB_QUEUE=hpcc,JOB_WALLCLOCK_TIME=02:00:00`: use the cluster's CPU partition and allow the job up to 2 hours.
- `DOUT_S_ROOT`: where finished output is copied. You must set this, because the default points to a folder that is not yours.
- `HIST_OPTION=never,REST_OPTION=ndays,REST_N=5`: no extra coupler output during the test, and one set of restart files at the end.

Next, add four sea-ice settings that every UHPC case uses:

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

Save with **Ctrl-O**, **Enter**, then quit with **Ctrl-X**. Then run these three commands, one at a time:

```bash
./case.setup
./xmlchange GMAKE_J=4
./case.build
```

`./case.setup` takes under a minute and ends with `You can now run './preview_run' to get more info on how your case will be run`. `GMAKE_J=4` tells the build to compile 4 files at a time. `./case.build` compiles the model. It prints many lines and ends with `MODEL BUILD HAS FINISHED SUCCESSFULLY`. It usually takes a few minutes, and can take longer when the cluster is busy. Stay inside tmux while it runs.

The build runs on the shared login computer. The cluster allows builds there, with up to 4 parallel compile processes, which is what `GMAKE_J=4` sets. Model runs never run there: they go to a compute node through `./case.submit`.

## 6. Submit with Slurm

Slurm is the program that shares the cluster's compute nodes among users. First look at what will be submitted:

```bash
./preview_run
```

It prints the `sbatch` commands CESM will use, including `-p hpcc` and `--time 02:00:00`. Then submit:

```bash
./case.submit -a "--exclude=hpcc03,hpcc04"
```

`-a "--exclude=hpcc03,hpcc04"` keeps the job off hpcc03 and hpcc04, the two nodes reserved for GPU work. Always add it when you submit. You should see lines that include `Submitted job id is` followed by a number, once for `case.run` (the model) and once for `case.st_archive` (copying the output afterwards). Write the numbers down.

A 5-day run takes about 45 minutes once it starts. It keeps running if you close OnDemand or shut your Mac.

## 7. Check on the job

```bash
squeue -u $USER
```

`squeue -u $USER` lists your jobs. `PD` in the `ST` column means waiting, and `R` means running. When the list is empty, the jobs are done. Then look at CESM's own record of each step:

```bash
cat CaseStatus
```

`cat` prints a whole file. The last lines should include `case.run success` and `st_archive success`. If they say `error`, see [When something goes wrong](when_things_go_wrong.md).

Two more commands are useful later. `sacct -j <jobid>` shows how a finished job ended (`COMPLETED`, `FAILED` or `TIMEOUT`), and `scancel <jobid>` cancels a job. Replace `<jobid>` with the number you wrote down.

## 8. Find the output

```bash
ls $MYROOT/scratch/f2000.test/run
ls $MYROOT/archive/f2000.test/logs
ls $MYROOT/archive/f2000.test/rest
ls $MYROOT/cases/f2000.test/timing
```

These are the run folder (where the model works), the compressed log files, the restart files, and the speed and cost of the run. A 5-day test with `HIST_OPTION=never` writes no monthly history files, so `atm/hist` stays empty. You turn on monthly output in later chapters. You can also browse these folders in the OnDemand **Files** app.

## 9. Keep an eye on space

Keep all CESM files in your own folder (`$MYROOT`). Your home folder is limited to 20 GB, and the `/scratch` disk on each compute node is wiped regularly.

Your folder has a soft limit of 300 GB. The run folder of a test case is about 1.5 GB, and a 3-month (92-day) run with monthly output adds about 4 GB of archived output, so the limit fits dozens of runs. Check your usage now and then:

```bash
du -sh $MYROOT/*
```

`du -sh` prints how much space each folder uses. The runs in this tutorial use well under the limit, so you do not need to delete anything. Never delete anything in `archive`.

## Where next

Go back to [Over break: what to do, in order](over_break.md) for the next step.
