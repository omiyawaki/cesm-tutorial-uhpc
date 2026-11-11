# Open OnDemand and shell basics

You'll do almost everything on UHPC through **Open OnDemand**, a website in your Mac's web browser that gives you the cluster's files, a command line and Jupyter notebooks. It's the same cluster you'd reach with `ssh`, but you don't have to set anything up on your Mac.

## Logging in

You already have a cluster account and have logged in once. From now on you'll use the website, so you won't need the Mac Terminal app.

1. Connect to the Union VPN with the **Cisco Secure Client** app. The cluster's websites only load on the campus network or through the VPN. The one-time VPN setup is in [Getting started on Union HPC](start_here.md).
2. In Safari or Chrome, go to <https://ondemand.hpc.union.edu>.
3. A small sign-in box appears. Type your cluster username (the first part of your Union email address) and your cluster password. Remember that the cluster password is not your Union (Okta) password (see step 0 of the [quickstart](quickstart.md)). The OnDemand dashboard opens.

## The apps you will use

| App | Where in OnDemand | Use it for |
|---|---|---|
| **Files** | top menu, **Files** → **Files App** (or **Home Directory**) | browsing folders, opening and editing text files, viewing pictures, uploading and downloading files to and from your Mac |
| **Shell** | top menu, **Clusters** → **HPC Cluster Shell Access** | typing commands, for example CESM's `./create_newcase` and `./case.submit` |
| **Jupyter** | top menu, **Interactive Apps** → **Servers** → **Jupyter Notebook** | Python notebooks for plotting model output. They run on a compute node for 1 to 4 hours (see {ref}`uhpc-jupyter` below) |
| **Active Jobs** | top menu, **Jobs** → **Active Jobs** | a web view of your waiting and running batch jobs, the same as the command `squeue -u $USER` (`$USER` stands for your username) |

The Shell app opens a command line on the cluster's login computer in a new browser tab. I call it the **OnDemand Shell tab** throughout, and every command in this tutorial goes there. Don't use `ssh` from the Mac Terminal app.

In the Files app, you can jump straight to a folder: click **Change directory** near the top, type a path such as `/usr/local/research/miyawaki/users/<your-username>`, and click **OK**. Type your username in place of `<your-username>`, because this box doesn't understand `$USER` or `$MYROOT`. If you're not sure of your username, type `whoami` in the OnDemand Shell tab and it'll print it.

(uhpc-editing)=
## Editing text files

You'll edit text files a lot, mostly settings files for CESM. Do it in OnDemand's file editor, in your web browser. It works like any Mac text app: click where you want to type, and copy and paste with **Cmd-C** and **Cmd-V**.

1. In the OnDemand dashboard tab, click **Files** → **Home Directory** in the top menu. For a file in your CESM folder, click **Change directory**, type the folder's full path, for example `/usr/local/research/miyawaki/users/<your-username>/cases/f2000.test`, and click **OK**.
2. Names that start with a dot, such as `.bashrc`, are hidden at first. To see them, tick **Show Dotfiles** above the file list.
3. Click the **⋮** button next to the file's name, then click **Edit**. The editor opens in a new browser tab.
4. To add lines at the end of a file, click just after the last character of the last line and press **Enter** to start a new line. Then type or paste your lines.
5. Click **Save** at the top left, then close the editor tab.

The saved file is on the cluster right away, so the OnDemand Shell tab sees the change. One catch: after you change `~/.bashrc`, type `source ~/.bashrc` in the Shell tab, because the shell only reads that file when it starts.

## Always work inside tmux

The Shell tab closes after about 5 minutes without typing, and after about 1 hour no matter what. When it closes, anything running in it stops, which is a problem for a build or a long download. `tmux` keeps your command line running on the cluster even when the tab closes, so you can reconnect and find it as you left it.

Every time you open the Shell app, type this line:

```bash
tmux attach -t cesm || tmux new -s cesm
```

`tmux attach -t cesm` goes back to your tmux session called `cesm`, with the same folder and earlier output. If no such session exists, it prints `no sessions` or `can't find session`. That message looks like an error, but it's fine: `||` then runs the second command, `tmux new -s cesm`, which starts a new session with that name. A new session clears the screen and shows a green bar at the bottom. If you already see that bar, you're already inside tmux, so don't type the line again.

A new session doesn't remember the folder you were in. Type `pwd` to see where you are, then `cd` back, for example `cd $MYROOT/cases/f2000.test`.

To leave tmux on purpose and keep it running, press **Ctrl-B**, let go, then press **D**. To end the session completely, type `exit` inside it.

(uhpc-jupyter)=
## Jupyter

Jupyter is where you'll look at model output and make plots. If you've used Google Colab, it's the same idea, but it runs on the cluster, right next to your output files.

1. Go to **Interactive Apps** → **Servers** → **Jupyter Notebook**.
2. Fill in the form:
   - **Hours**: how long the session lasts, 1 to 4 (default 4). It stops at the end, so save your notebook before then.
   - **CPU cores**: 1 to 8. Use 2 for plotting.
   - **Conda environment**: leave it as `datascience` (the Python packages already on the cluster).
   - **Partition**: leave it as `hpcc` (the CPU queue).
   - **GPUs**: 0.
3. Click **Launch**. The session waits in the queue for a bit, then shows **Running**. Click **Connect to Jupyter**.
4. JupyterLab opens in a new tab with the **Launcher**. Click **Python 3 (ipykernel)** under **Notebook** to make a new notebook in your home folder. The file browser on the left only shows your home folder, so to open model output, type its full path in your code, for example `xarray.open_dataset('/usr/local/research/miyawaki/users/<your-username>/...')`, with your username in place of `<your-username>`, because Python doesn't understand `$USER` or `$MYROOT`.
5. In the first cell, type `import xarray, netCDF4, matplotlib.pyplot as plt` and press **Shift-Enter**. If no error message appears, it worked.
6. When you're done, save your notebook with **Cmd-S**, then stop the session so it isn't holding a compute node someone else could use: switch to the OnDemand dashboard tab (not the JupyterLab tab and not the Shell tab), click **My Interactive Sessions** in the top menu, and click **Delete** on the Jupyter session.

The `datascience` environment has xarray, netCDF4 and matplotlib, but **not cartopy** (map projections and coastlines). Plain maps with `plt.pcolormesh(lon, lat, field)` work without it, and you won't need cartopy for this tutorial. Use `datascience` for everything in the getting-started steps.

Jupyter runs on a compute node, which is why we start it from the Jupyter app. Never start Jupyter or other heavy calculations from the Shell, which runs on the login computer that everyone shares.

## Shell basics

If you haven't used a command line before, this is the part to practise. Type a command and press **Enter**. Most commands print nothing when they succeed, which feels odd at first, but silence means it worked. In the table, words inside `< >` are placeholders: replace them with a real folder or file name, and don't type the `<` or `>` characters. Where a path shows `<your-username>`, type the first part of your Union email instead.

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

## Useful keys

- **Tab** completes a file or folder name. Type the first few letters and press Tab. If nothing happens, press Tab twice to see the choices. I use this constantly, because it saves typing and avoids typos in long paths.
- **Up arrow** brings back your previous command, so you can fix a typo and run it again.
- **Ctrl-C** stops the command that's running now and gives you back the prompt. It doesn't cancel batch jobs that are already submitted. Use `scancel` for those.
- To paste into the Shell tab, use **Cmd-V**, as on any Mac web page. To copy text from the Shell tab, select it with the mouse and press **Cmd-C**. You can't click to move the cursor inside a command, so use the arrow keys for that.

## Paths, variables, modules and permissions

- **Paths.** `/` separates folders. A path starting with `/` is a full path. `~` means your home folder. `.` means "this folder", and `./case.submit` means "run the program `case.submit` in this folder".
- **Variables.** `export MYROOT=/usr/local/research/miyawaki/users/$USER` saves a path under a short name, and `$MYROOT` then stands for it, which saves you typing that long path over and over. `$USER` is already set to your username, so type it as written. Check a variable with `echo $MYROOT`. Variables are forgotten when the shell closes, unless you add the `export` line to `~/.bashrc` (see {ref}`Editing text files <uhpc-editing>`).
- **`source <file>`** runs the commands in a file in your current shell. CESM needs this to load its compilers and libraries: `source /usr/local/research/miyawaki/opt/cesm-deps/ENV.sh`.
- **Modules.** `module load <name>` makes a software package available, `module list` shows what's loaded, and `module avail` shows what exists. `ENV.sh` loads the modules CESM needs for you, so you won't usually type these.
- **Permissions.** `ls -l` starts each line with something like `-rw-r-----`: the first three letters after the first character are your permissions, the next three are your group's, and the last three are everyone else's (`r` read, `w` write, `x` run). If you see `Permission denied`, you're trying to read or change something your account isn't allowed to. Don't try to work around it. Look it up in [When something goes wrong](when_things_go_wrong.md), and if it isn't covered there, email me.
- **Reading errors.** When something fails, read the **first** error message. The last lines are often just other parts of the program stopping because of the first problem. `grep -i error <logfile>` finds error lines in a log. When you email me, copy the exact message rather than describing it, because the exact wording usually tells me what's wrong.

## Where to keep files

| Place | Size limit | Use it for |
|---|---|---|
| your home folder `/home/<your-username>` (`~`) | 20 GB | settings files such as `~/.bashrc` and `~/.cdsapirc`. Keep CESM output out of this folder |
| `/usr/local/research/miyawaki/users/<your-username>` (`$MYROOT`) | soft limit of 300 GB per student | your CESM cases, runs, output and SST files |
| `/scratch` | a separate disk on each compute node, cleaned after 30 days | do not use for CESM |

A case's run folder is about 1.5 GB, and a 3-month CESM run adds about 4 GB of archived output, so space adds up faster than you might expect. After you set `$MYROOT` in step 3 of the [quickstart](quickstart.md), run `du -sh $MYROOT/*` now and then. `du -sh` prints how much space each folder uses.

## Copying files to and from your Mac

Use the **Files** app: open a folder, then use the **Upload** button to send a file from your Mac, or select a file and use **Download** to save it to your Mac's Downloads folder. This is handy for pictures and small files. Model output files are large, so look at them on UHPC with Jupyter instead of downloading them.

## Running jobs

CESM runs as **batch jobs** on the compute nodes. You submit them with `./case.submit` (see the [quickstart](quickstart.md)), and they keep running after you close OnDemand, so you don't need to keep your laptop open. These commands let you check on them:

| Command | What it does |
|---|---|
| `squeue -u $USER` | list your waiting (`PD`) and running (`R`) jobs. If there is no job row under the header, you have no jobs left |
| `sacct -j <jobid>` | show how a finished job ended (`COMPLETED`, `FAILED`, `TIMEOUT`) |
| `scancel <jobid>` | cancel a job |

`$USER` stands for your username, so you can type these commands exactly as shown.

The Shell runs on the login computer that everyone shares. Short commands such as `./case.setup`, `./xmlchange` and the SST script are fine there, and so is `./case.build` (see the quickstart). Don't run the model or other heavy calculations there, and don't start Jupyter from it, because that slows the cluster down for everyone. Use `./case.submit` and the Jupyter app instead.

## Optional: an environment with cartopy

You don't need this for the getting-started steps, and a failed install can fill your home folder, so leave it until you want it. When you want coastlines on your maps, you can make your own Python environment once. Do this in the OnDemand Shell tab, inside tmux:

```bash
module load python/miniforge
mamba create -n geo -c conda-forge python=3.12 jupyterlab ipykernel cartopy xarray netcdf4 matplotlib
```

It asks `Proceed ([y]/n)?`. Type `y` and press Enter. The install uses about 2-3 GB of your 20 GB home folder (it goes in `~/.conda/envs/geo`). After that, type `geo` instead of `datascience` in the **Conda environment** box of the Jupyter form. `jupyterlab` has to be in the list above, or the Jupyter session won't start.
