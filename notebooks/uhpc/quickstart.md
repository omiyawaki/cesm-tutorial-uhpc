# UHPC quickstart: your first CESM2 run on Union HPC

In this page you'll make, build and run your first CESM case, a 5-day atmosphere-only test. It's small on purpose: if it works, you know your account, the model and the cluster all work, and every experiment you run later starts the same way. Read [Open OnDemand and shell basics](ondemand_basics.md) before you start. UHPC runs CESM version 2.1.5.

## 0. What you already have

You already have a UHPC account. Your username is the first part of your Union email address (the part before `@union.edu`).

Your cluster password is **not** your Union (Okta) password, and mixing the two up is the most common reason a login fails. The cluster administrators emailed you a temporary password when they made your account, and you chose a new cluster password the first time you logged in. (If you haven't logged in yet and aren't sure how to set it, email me and we'll do it together.) Use that cluster password for OnDemand, and your Union password only for the VPN. If you forget the cluster password, email <a href="mailto:hpcadmin@union.edu">hpcadmin@union.edu</a> from your Union email address and ask them to reset it.

You won't need the Mac Terminal app for anything here. Every command goes into the OnDemand Shell tab.

## 1. Open OnDemand and start a shell

1. Connect to the Union VPN with the **Cisco Secure Client** app (see [Getting started on Union HPC](start_here.md) for the one-time setup). The cluster's website won't load from off campus without it.
2. In Safari or Chrome, go to <https://ondemand.hpc.union.edu>. A small sign-in box appears. Type your cluster username and password.
3. In the top menu, click **Clusters** → **HPC Cluster Shell Access**. A black command-line window opens in a new browser tab.
4. Type this line to get into tmux, so your work keeps running if the tab closes:

```bash
tmux attach -t cesm || tmux new -s cesm
```

This line goes back to your tmux session named `cesm` if it exists, and starts a new one with that name if it does not (`||` means "if the first command fails, run the second"). If you see `no sessions` first, that's normal the first time. Use the same line every time you open a Shell tab.

## 2. Check that your account is ready

```bash
id
```

`id` prints your username and the groups you belong to. The list must include `res-miyawaki`, our research group, which owns the CESM files. Without it, the next step fails with `Permission denied`. If it's missing, see "Permission denied" in [When something goes wrong](when_things_go_wrong.md).

## 3. Set up your environment

These lines tell the shell where the compilers, the shared CESM code and your own folder are. Type them, or copy them from this page and paste them into the Shell tab with **Cmd-V**. Press **Enter** after each line.

```bash
source /usr/local/research/miyawaki/opt/cesm-deps/ENV.sh
export CESMROOT=/usr/local/research/miyawaki/cesm/cesm2
export MYROOT=/usr/local/research/miyawaki/users/$USER
mkdir -p $MYROOT/cases $MYROOT/scratch $MYROOT/archive
ls $MYROOT
```

- `source .../ENV.sh` runs the commands in the file `ENV.sh`, which load the compiler, MPI and NetCDF libraries that CESM needs.
- `export CESMROOT=...` saves the location of the shared CESM2 code under the short name `CESMROOT`. We all use the same copy, which I've already set up for the cluster, so you don't download CESM.
- `export MYROOT=...` saves the location of your own folder. `$USER` stands for your username, so you can type the line exactly as shown.
- `mkdir -p` makes the three folders inside it: one for cases (your settings), one for run files and one for finished output.
- `ls $MYROOT` lists what is in your folder. You should see `archive  cases  scratch`.

The shell forgets these settings when it closes, and retyping them every session is tedious. To have them set every time you log in, add them to the end of the file `~/.bashrc`, which the shell runs at every login. Open it in the OnDemand file editor, as described in {ref}`Editing text files <uhpc-editing>`: in the dashboard tab click **Files** → **Home Directory**, tick **Show Dotfiles**, click **⋮** next to `.bashrc`, and click **Edit**. Click just after the last character of the last line and press **Enter** to start a new line. Copy this block from this page and paste it with **Cmd-V**:

```bash
source /usr/local/research/miyawaki/opt/cesm-deps/ENV.sh
export CESMROOT=/usr/local/research/miyawaki/cesm/cesm2
export MYROOT=/usr/local/research/miyawaki/users/$USER
```

Click **Save** and close the editor tab. Back in the OnDemand Shell tab, load the file and check it:

```bash
source ~/.bashrc
echo $MYROOT
```

`echo $MYROOT` should print `/usr/local/research/miyawaki/users/` followed by your username. If it prints an empty line, something in the block didn't paste right; see "`$MYROOT` is empty" in [When something goes wrong](when_things_go_wrong.md).

## 4. Create a small case

A "case" is a folder that holds the settings for one model experiment. Your thesis runs will each be a case like this one, just with different settings. This test case is atmosphere-only (`F2000climo`: year-2000 conditions with prescribed sea surface temperatures) at about 2-degree resolution (`f19_f19_mg17`).

```bash
cd $CESMROOT/cime/scripts
./create_newcase --case $MYROOT/cases/f2000.test \
                 --compset F2000climo --res f19_f19_mg17 \
                 --output-root $MYROOT/scratch --run-unsupported
```

`cd` moves you into the folder that holds CESM's scripts. `./create_newcase` runs the program `create_newcase` in this folder. The `\` at the end of a line continues the command on the next line, so paste all four lines together. You'll see many lines of messages scroll by. That's normal, and what matters is the end, which should be `Creating Case directory /usr/local/research/miyawaki/users/<your-username>/cases/f2000.test` and `Machine is union_hpcc`.

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

Now you tell the case how big to run and for how long. Each `./xmlchange` line changes one or more case settings and prints nothing if it worked. To read a setting back, use `./xmlquery`, for example `./xmlquery STOP_N`.

- `NTASKS=8`: use 8 processors on one compute node.
- `STOP_OPTION=ndays,STOP_N=5`: run 5 model days.
- `JOB_QUEUE=hpcc,JOB_WALLCLOCK_TIME=02:00:00`: use the cluster's CPU partition and allow the job up to 2 hours.
- `DOUT_S_ROOT`: where finished output is copied. You have to set this, because the default points to a folder that isn't yours, and the archive step at the end would fail.
- `HIST_OPTION=never,REST_OPTION=ndays,REST_N=5`: no extra coupler output during the test, and one set of restart files at the end. The atmosphere's own output is set separately, in `user_nl_cam` below. The [CAM output](../namelist/output/output_cam.ipynb) section of the namelist chapter explains the output settings in more detail.

Next, set up the case, which writes the scripts and settings files the build and the run will use:

```bash
./case.setup
```

`./case.setup` ends with `You can now run './preview_run' to get more info on how your case will be run`. It also makes the files `user_nl_cam`, `user_nl_cice` and others, where you write model settings.

Now add four sea-ice settings that every UHPC case needs. Without them the sea-ice model doesn't work with the input files on UHPC and the run stops. Open `user_nl_cice` in the file editor: in the dashboard tab click **Files** → **Home Directory**, click **Change directory**, type `/usr/local/research/miyawaki/users/<your-username>/cases/f2000.test` with your username in place of `<your-username>`, and click **OK**. Then click **⋮** next to `user_nl_cice` and click **Edit**. The file has a few lines starting with `!`, which are comments, so leave them as they are. Click at the end of the last line, press **Enter**, and type or paste these four lines exactly, including the `=` signs, the dots around `.false.` and the double quotes around `"default"`:

```
ktherm = 1
tr_pond_lvl = .false.
shortwave = "default"
highfreq = .false.
```

Click **Save** and close the editor tab.

Next, ask the atmosphere for daily output, so you'll have maps to look at when the run finishes. By default CAM only writes monthly averages, and a 5-day run ends before the first month is over, so without this line you'd get no atmosphere output at all. In the same folder in the Files app, click **⋮** next to `user_nl_cam`, click **Edit**, click at the end of the last line, press **Enter**, and type this line:

```
nhtfrq = -24
```

`nhtfrq = -24` means "write an average every 24 hours". Click **Save** and close the editor tab. Back in the OnDemand Shell tab, check the file and build the model, one command at a time:

```bash
cat user_nl_cice
./xmlchange GMAKE_J=4
./case.build
```

`cat user_nl_cice` prints the file, so you can check that the four lines are at the end. (Type `cat user_nl_cam` too, to check the `nhtfrq` line.) `GMAKE_J=4` tells the build to compile 4 files at a time. `./case.build` compiles the model, turning CESM's Fortran code into a program for your case. It prints a lot of output, and some of it can look alarming, including lines such as `Component mct build complete with 42 warnings`. Those warnings are normal. What matters is the last line, `MODEL BUILD HAS FINISHED SUCCESSFULLY`. On UHPC it takes about 1.5 minutes, and the line `Time spent building:` near the end gives the time in seconds. Stay inside tmux while it runs, so a closed tab doesn't stop it.

The build runs on the shared login computer. The cluster allows builds there, with up to 4 parallel compile processes, which is what `GMAKE_J=4` sets. The model itself never runs there: it goes to a compute node through `./case.submit`.

## 6. Submit with Slurm

Slurm is the program that shares the cluster's compute nodes among users. You hand it your job, and it starts the job when a node is free. First look at what will be submitted:

```bash
./preview_run
```

It prints the `sbatch` commands CESM will use, including `-p hpcc` and `--time 02:00:00`. Then submit:

```bash
./case.submit -a="--exclude=hpcc03,hpcc04"
```

`-a="--exclude=hpcc03,hpcc04"` keeps the job off hpcc03 and hpcc04, the two nodes reserved for GPU work. CESM doesn't add this for you, so always add it when you submit. Type the `=` right after `-a`: without it, `case.submit` mistakes `--exclude` for one of its own options and stops with `expected one argument`. You should see lines that include `Submitted job id is` followed by a number, once for `case.run` (the model) and once for `case.st_archive` (copying the output afterwards). Write the numbers down, since you'll need them if something goes wrong.

A 5-day run takes about 45 minutes once it starts, and it may wait in the queue before that if the cluster is busy. It keeps running if you close OnDemand or shut your Mac, so you don't need to watch it.

## 7. Check on the job

```bash
squeue -u $USER
```

`squeue -u $USER` lists your jobs. `PD` in the `ST` column means waiting, and `R` means running. A long `PD` usually just means the cluster is busy. If there's no job row under the header, the jobs are done, but that alone doesn't tell you whether they worked. Then look at CESM's own record of each step:

```bash
cat CaseStatus
```

`cat` prints a whole file. If you'd rather read it in the browser, open the case folder in the Files app and click `CaseStatus`: the Files app shows a text file or a picture when you click its name. The last lines should include `case.run success` and `st_archive success`. If you see both, your first CESM run worked. If they say `error`, see [When something goes wrong](when_things_go_wrong.md).

Two more commands are useful later. `sacct -j <jobid>` shows how a finished job ended (`COMPLETED`, `FAILED` or `TIMEOUT`), and `scancel <jobid>` cancels a job. Replace `<jobid>` with the number you wrote down.

## 8. Find the output

```bash
ls $MYROOT/scratch/f2000.test/run
ls $MYROOT/archive/f2000.test/logs
ls $MYROOT/archive/f2000.test/rest
ls $MYROOT/cases/f2000.test/timing
```

These are the run folder (where the model works), the compressed log files, the restart files, and the speed and cost of the run. You can also browse these folders in the OnDemand **Files** app.

The atmosphere's output is in `atm/hist`:

```bash
ls $MYROOT/archive/f2000.test/atm/hist
```

You should see one file, `f2000.test.cam.h0.0001-01-01-00000.nc`. It holds 5 daily averages of every atmosphere variable CAM writes by default. The name tells you the case, the component (`cam`), the history stream (`h0`) and the model date the file starts on.

## 9. Look at your output

Printed messages tell you the model finished, but a map tells you whether it made sense. Start a Jupyter session as in {ref}`Jupyter <uhpc-jupyter>` (leave **Conda environment** as `datascience`), make a new notebook, and type this in the first cell, with your username in place of `<your-username>`:

```python
import xarray as xr
import matplotlib.pyplot as plt

ds = xr.open_dataset('/usr/local/research/miyawaki/users/<your-username>/archive/f2000.test/atm/hist/f2000.test.cam.h0.0001-01-01-00000.nc')
ds
```

Press **Shift-Enter**. Jupyter prints a summary of the file. Under **Dimensions** you'll see `time: 5` (the five days), `lat: 96` and `lon: 144` (the 2-degree grid) and `lev: 32` (the model's levels in the atmosphere). Under **Data variables** there's a long list, more than 300 of them, because CAM writes many variables by default. Click the small page icon at the right end of a row to see what a variable is and its units. `TS` is the surface temperature and `PRECT` is the total precipitation rate.

Now make a map of surface temperature on the first day. Type this in the next cell:

```python
ts = ds['TS'].isel(time=0)

plt.figure(figsize=(9, 4))
plt.pcolormesh(ds['lon'], ds['lat'], ts, cmap='RdYlBu_r')
plt.colorbar(label='Surface temperature (K)')
plt.xlabel('Longitude (degrees east)')
plt.ylabel('Latitude (degrees north)')
plt.title('f2000.test: surface temperature, day 1')
plt.show()
```

`isel(time=0)` picks the first of the five days. Your map should look like the one below: warm (about 300 K, red) across the tropics, cold (blue) toward the poles, coldest over Antarctica and high ground such as the Himalayas, with the outlines of the continents showing. If the map is one flat colour, or the warm band isn't at the equator, email me the notebook cell and what you see.

```{figure} ../../images/uhpc/quickstart_ts_day1.png
:width: 650px
:alt: World map of surface temperature on day 1 of the test run. Red and yellow around 300 K across the tropics, blue toward the poles, darkest blue over Antarctica, with continent shapes visible.
Surface temperature on day 1 of a UHPC `f2000.test` run. Yours should look the same.
```

Save the notebook with **Cmd-S** and stop the Jupyter session when you're done (step 6 of {ref}`Jupyter <uhpc-jupyter>`).

## 10. Disk space

Keep all CESM files in your own folder (`$MYROOT`). Your home folder is limited to 20 GB, and the `/scratch` disk on each compute node is wiped regularly, so output left there would disappear.

Your folder has a soft limit of 300 GB, which is plenty for tests but fills up with longer runs. The run folder of a test case is about 1.5 GB, and a 3-month (92-day) run with monthly output adds about 4 GB of archived output. Check your usage now and then:

```bash
du -sh $MYROOT/*
```

`du -sh` prints how much space each folder uses. Don't delete anything in your folder unless I tell you to, and never delete anything in `archive`. If you're running low on space, email me and we'll decide together what can go.
