# Open OnDemand and shell basics

You will use UHPC mostly through **Open OnDemand**, a website that gives you the cluster's files, a command line and Jupyter notebooks in your Mac's web browser. This page explains the parts you need and the few shell commands used throughout this tutorial. It is not a full Linux course.

## Logging in

You already have a cluster account and have logged in once. From now on you use the website, not the Mac Terminal app.

1. Connect to the Union VPN with the **Cisco Secure Client** app. The cluster's websites only load on the campus network or through the VPN. The one-time VPN setup is in [Over break: what to do, in order](over_break.md).
2. In Safari or Chrome, go to <https://ondemand.hpc.union.edu>.
3. A small sign-in box appears. Type your cluster username (the first part of your Union email address) and your cluster password. The OnDemand dashboard opens.

## The apps you will use

| App | Where in OnDemand | Use it for |
|---|---|---|
| **Files** | top menu, **Files** → **Files App** (or **Home Directory**) | browsing folders, opening and editing text files, viewing pictures, uploading and downloading files to and from your Mac |
| **Shell** | top menu, **Clusters** → **HPC Cluster Shell Access** | typing commands, for example CESM's `./create_newcase` and `./case.submit` |
| **Jupyter** | top menu, **Interactive Apps** → **Servers** → **Jupyter Notebook** | Python notebooks for plotting model output. They run on a compute node for 1 to 4 hours (see {ref}`uhpc-jupyter` below) |
| **Active Jobs** | top menu, **Jobs** → **Active Jobs** | a web view of your waiting and running batch jobs, the same as `squeue -u $USER` |

The Shell app opens a command line on the same login computer you reached with `ssh`, with the same home folder and the same `/usr/local/research` files.

In the Files app, click **Change directory** near the top, type a path such as `/usr/local/research/miyawaki/users/<your-username>`, and click **OK** to jump to it.

(uhpc-jupyter)=
## Jupyter

Use Jupyter for looking at model output and making plots, like Google Colab but on the cluster.

1. Go to **Interactive Apps** → **Servers** → **Jupyter Notebook**.
2. Fill in the form:
   - **Hours**: how long the session lasts, 1 to 4 (default 4). It stops at the end, so save your notebook before then.
   - **CPU cores**: 1 to 8. Use 2 for plotting.
   - **Conda environment**: leave it as `datascience`.
   - **Partition**: leave it as `hpcc`.
   - **GPUs**: 0.
3. Click **Launch**. The session waits in the queue, then shows **Running**. Click **Connect to Jupyter**.
4. JupyterLab opens in a new tab with the **Launcher**. Click **Python 3 (ipykernel)** under **Notebook** to make a new notebook in your home folder. The file browser on the left only shows your home folder, so to open model output, type its full path in your code, for example `xarray.open_dataset('/usr/local/research/miyawaki/users/<your-username>/...')`.
5. In the first cell, type `import xarray, netCDF4, matplotlib.pyplot as plt` and press **Shift-Enter**. No error message means it worked.

The `datascience` environment has xarray, netCDF4 and matplotlib, but **not cartopy** (map projections and coastlines). Plain maps with `plt.pcolormesh(lon, lat, field)` work without it, and this tutorial does not need cartopy.

### Later: an environment with cartopy

When you want coastlines on your maps, make your own Python environment once. Do this in the **Shell** app, inside tmux:

```bash
module load python/miniforge
mamba create -n geo -c conda-forge python=3.12 jupyterlab ipykernel cartopy xarray netcdf4 matplotlib
```

It asks `Proceed ([y]/n)?`. Type `y` and press Enter. Installing takes several minutes and uses about 2-3 GB of your 20 GB home folder (it goes in `~/.conda/envs/geo`). After that, type `geo` instead of `datascience` in the **Conda environment** box of the Jupyter form. `jupyterlab` has to be in the list above, or the Jupyter session will not start.

Jupyter runs on a compute node. Never start Jupyter or other heavy calculations from the Shell, which runs on the shared login computer.

## Always work inside tmux

The Shell tab closes after about 5 minutes without typing, and after about 1 hour in any case. Anything running in it would stop. `tmux` keeps your command line running on the cluster even when the tab closes, so you can reconnect to it.

The first time you open the Shell app each day, type:

```bash
tmux new -s cesm
```

Your screen clears and a green bar appears at the bottom. You are now inside a tmux session called `cesm`. Work as usual.

When the tab closes, or you come back later, open the Shell app again and type:

```bash
tmux attach -t cesm
```

You are back where you left off, with the same folder and earlier output. If it says `no sessions` or `can't find session`, the session has ended (for example after the login computer restarted). Start a new one with `tmux new -s cesm`.

To leave tmux on purpose and keep it running, press **Ctrl-B**, let go, then press **D**. To end the session completely, type `exit` inside it.

## Shell basics

Type a command and press **Enter**. Most commands print nothing when they succeed.

| Command | What it does | What you should see |
|---|---|---|
| `pwd` | print the folder you are in ("working directory") | a path such as `/home/<your-username>` |
| `ls` | list the files in this folder | file and folder names |
| `ls -l` | list with sizes, dates and permissions | one line per file |
| `cd <folder>` | move into a folder | nothing. Check with `pwd` |
| `cd ..` | move up one folder | nothing |
| `cd` | go back to your home folder | nothing |
| `mkdir -p <folder>` | make a folder (and any missing parent folders) | nothing |
| `cp <from> <to>` | copy a file | nothing |
| `mv <from> <to>` | move or rename a file | nothing |
| `less <file>` | read a long text file one page at a time. **Space** goes forward, **B** goes back, **/word** searches, **Q** quits | the file's text |
| `tail -n 30 <file>` | show the last 30 lines of a file (where errors usually are) | the last lines |
| `grep <word> <file>` | show the lines that contain a word | matching lines |
| `nano <file>` | edit a text file. **Ctrl-O** then **Enter** saves, **Ctrl-X** quits | an editor fills the screen |

Useful keys:

- **Tab** completes a file or folder name. Type the first few letters and press Tab. If nothing happens, press Tab twice to see the choices. This saves typing and avoids typos.
- **Up arrow** brings back your previous command, so you can edit and rerun it.
- **Ctrl-C** stops the command that is running now and gives you back the prompt. It does not cancel batch jobs that are already submitted. Use `scancel` for those.
- To paste into the Shell tab, use **Cmd-V**, as on any Mac web page. To copy text from the Shell tab, select it with the mouse and press **Cmd-C**.

A few ideas you will meet in the CESM pages:

- **Paths.** `/` separates folders. A path starting with `/` is a full path. `~` means your home folder. `.` means "this folder", and `./case.submit` means "run the program `case.submit` in this folder".
- **Variables.** `export MYROOT=/usr/local/research/miyawaki/users/$USER` saves a path under a short name, and `$MYROOT` then stands for it. `$USER` is already set to your username. Check a variable with `echo $MYROOT`. Variables are forgotten when the shell closes, unless you add the `export` line to `~/.bashrc` (open it with `nano ~/.bashrc`).
- **`source <file>`** runs the commands in a file in your current shell. CESM uses this to load compilers and libraries: `source /usr/local/research/miyawaki/opt/cesm-deps/ENV.sh`.
- **Modules.** `module load <name>` makes a software package available, `module list` shows what is loaded, and `module avail` shows what exists. `ENV.sh` loads the modules CESM needs for you.
- **Permissions.** `ls -l` starts each line with something like `-rw-r-----`: the first three letters after the first character are your permissions, the next three are your group's, and the last three are everyone else's (`r` read, `w` write, `x` run). If you see `Permission denied`, you are trying to read or change something you are not allowed to. Do not try to work around it. See [When something goes wrong](when_things_go_wrong.md).
- **Reading errors.** When something fails, read the **first** error message, not the last line. `grep -i error <logfile>` finds error lines in a log. Copy the exact message when you ask for help.

## Where to keep files

| Place | Size limit | Use it for |
|---|---|---|
| your home folder `/home/<your-username>` (`~`) | 20 GB | settings files such as `~/.bashrc` and `~/.cdsapirc`. Not CESM output |
| `/usr/local/research/miyawaki/users/<your-username>` (`$MYROOT`) | soft limit of 300 GB per student | your CESM cases, runs, output and SST files |
| `/scratch` | a separate disk on each compute node, cleaned after 30 days | do not use for CESM |

A case's run folder is about 1.5 GB, and a 3-month CESM run adds about 4 GB of archived output. Run `du -sh $MYROOT/*` now and then to see how much space each folder uses.

## Copying files to and from your Mac

Use the **Files** app: open a folder, then use the **Upload** button to send a file from your Mac, or select a file and use **Download** to save it to your Mac's Downloads folder. Use this for pictures and small files. Model output files are large, so look at them on UHPC with Jupyter instead of downloading them.

## Running jobs

CESM runs as **batch jobs** on the compute nodes. You submit them with `./case.submit` (see the [quickstart](quickstart.md)), and they keep running after you close OnDemand. These commands check on them:

| Command | What it does |
|---|---|
| `squeue -u $USER` | list your waiting (`PD`) and running (`R`) jobs. An empty list means none are left |
| `sacct -j <jobid>` | show how a finished job ended (`COMPLETED`, `FAILED`, `TIMEOUT`) |
| `scancel <jobid>` | cancel a job |

The Shell runs on the shared login computer. Short commands such as `./case.setup`, `./xmlchange` and the SST script are fine there, and so is `./case.build` (see the quickstart). Do not run the model or other heavy calculations there, and do not start Jupyter from it. Use `./case.submit` and the Jupyter app instead.
