# When something goes wrong

Errors are a normal part of running CESM, and I get them too. Most have a known cause, and the common ones are below. Find the message you see, or the step you were on, and follow the fix. If that doesn't fix it, email me (<a href="mailto:miyawako@union.edu">miyawako@union.edu</a>) and paste the command you typed and the error you're seeing. Pasted text is easier for me to work with than a screenshot. While you wait, go on with whatever you can do without it.

When a command fails, read the **first** error message it printed. The last lines are often just other parts of the program stopping because of that first problem, so they can look worse than the real cause. To copy a message out of the Shell tab, select it with the mouse and press **Cmd-C**.

## Getting in

### The OnDemand page does not load, or times out

You're not on the campus network, or the VPN isn't connected. Connect the **Cisco Secure Client** VPN to `unionvpn.union.edu` and reload the page. ITS explains the setup in [How to Use the Cisco VPN Client (Mac/PC)](https://union.teamdynamix.com/TDClient/1831/Portal/KB/Article/56060/How-to-Use-the-Cisco-VPN-Client-Mac-PC). If the VPN itself won't connect, the ITS Help Desk can help at <a href="mailto:helpdesk@union.edu">helpdesk@union.edu</a> or (518) 388-6400.

### The sign-in box keeps coming back

The username or password is wrong, and almost always it's the password. Use your cluster username (the first part of your Union email address, the part before `@union.edu`) and your cluster password. The cluster password is not your Union (Okta) password: it is the one you chose the first time you logged in to the cluster. For a forgotten cluster password, email the cluster administrators at <a href="mailto:hpcadmin@union.edu">hpcadmin@union.edu</a> from your Union email address and ask them to reset it.

### The Shell tab says the connection closed

That's normal. The OnDemand Shell closes after about 5 minutes without typing, and after about 1 hour no matter what. If you were inside tmux, nothing is lost. Open **Clusters** → **HPC Cluster Shell Access** again and type `tmux attach -t cesm || tmux new -s cesm`.

### `tmux attach` says `no sessions` or `can't find session`

The tmux session ended, for example because the login computer restarted. If you typed `tmux attach -t cesm || tmux new -s cesm`, a new session has already started, with a green bar at the bottom. If you typed only `tmux attach -t cesm`, type `tmux new -s cesm`. Then `cd` back to the folder you were in, for example `cd $MYROOT/cases/f2000.test`. Anything you were building when the session ended has to be started again, which is annoying but harmless.

### `duplicate session: cesm`

You typed `tmux new -s cesm` while a session called `cesm` was still running. Nothing is wrong. Type `tmux attach -t cesm` to go back to it.

### `sessions should be nested with care`

You are already inside tmux (there is a green bar at the bottom of the window), so there is nothing to attach to. Keep working where you are.

### The file editor does not open, or **Save** fails

First check the path at the top of the editor tab. You can only save files you are allowed to change, such as the files in your home folder and in `/usr/local/research/miyawaki/users/<your-username>`. If the editor still doesn't work, edit the file in the OnDemand Shell tab with `nano`, a text editor that runs inside the Shell. Type `nano` and the file name, for example `nano ~/.bashrc`. Move with the arrow keys, because clicking doesn't move the cursor in `nano`. Paste with **Cmd-V**. Press **Ctrl-O** (hold the Control key and press O), then **Enter** to save, and **Ctrl-X** to quit.

## Permissions and setup

### `Permission denied` on anything under `/usr/local/research/miyawaki`, or `ENV.sh: Permission denied`

Your account isn't in the `res-miyawaki` group yet, or I added the group after you logged in. Type `id`. If `res-miyawaki` is missing, close every OnDemand tab, sign out, and sign in again, then type `id` again. If it's still missing, email me and I'll add you. After I add you to the group, sign out and sign in again. Group changes can take up to an hour to reach the cluster.

### `cesm-deps/ENV.sh: No such file or directory`

The `source` line in `~/.bashrc` almost certainly has a typing mistake in the path. Open `~/.bashrc` in the file editor ({ref}`Editing text files <uhpc-editing>`) and compare the line with the block in step 3 of the [quickstart](quickstart.md). It must be exactly `source /usr/local/research/miyawaki/opt/cesm-deps/ENV.sh`. Click **Save**, then run `source ~/.bashrc` in the Shell tab. If the path is correct and you still see the message together with `Permission denied`, see the entry above.

### `$MYROOT` is empty

`echo $MYROOT` prints an empty line, so commands such as `cd $MYROOT/cases` go to the wrong place. The `export MYROOT=...` line is missing from `~/.bashrc` or has a typing mistake. Open `~/.bashrc` in the file editor ({ref}`Editing text files <uhpc-editing>`), compare the three lines at the end with the block in step 3 of the [quickstart](quickstart.md), and fix or add them. Click **Save**, then run `source ~/.bashrc` in the Shell tab. Then `echo $MYROOT` should print `/usr/local/research/miyawaki/users/` followed by your username.

### `Disk quota exceeded`

Your home folder (20 GB) is full. Type `du -sh ~/.conda ~/.cache` to see what is using it. The `~/.cache` folder can be emptied with `rm -r ~/.cache/pip`. `rm -r` deletes a folder and everything in it, so be careful with it in general, but this folder only holds copies of downloaded install files, so it's safe to delete. Keep CESM files in `$MYROOT`, never in your home folder. If you can't tell what's filling it, email me the output of the `du` command.

## Creating, setting up and building a case

### `create_newcase` says the case directory already exists

You ran `create_newcase` twice with the same case name. CESM refuses to overwrite a case, which protects your work. Use the case you already have, `cd $MYROOT/cases/f2000.test`, and continue with step 5 of the quickstart.

### `case.setup` or `case.build` fails with `Permission denied` and a path that does not contain your username

The case was created without `--output-root $MYROOT/scratch`, so it points at a folder that isn't yours. It's easier to start over than to repair it: make a new case with a new name, for example `f2000.test2`, and type the `create_newcase` command exactly as shown, including `--output-root`, but with `f2000.test2` in place of `f2000.test`. Use `f2000.test2` wherever the later steps say `f2000.test`.

### `case.build` stops with an error

The build output itself rarely says what went wrong, but it prints the name of a log file next to the error, for example `.../bld/atm.bldlog.<date>`. Open it with `less <path-to-log>` and press **Shift-G** to jump to the end, where the error is. If you'd rather use the mouse, open the `bld` folder in the Files app and click the log's name to read it in the browser. Also check that you ran the `source .../ENV.sh` line in this shell (it is in your `~/.bashrc`). Then run `./case.build` again. If it fails the same way, email me the last 30 lines of that log.

## Jobs

### `case.submit: error: argument -a/--batch-args: expected one argument`

The `=` after `-a` is missing. Type the command exactly as `./case.submit -a="--exclude=hpcc03,hpcc04"`, with no space between `-a` and `=`.

### `squeue` shows `PD` for a long time

This is usually nothing to worry about. `PD` means the job is waiting for free processors. The reason is in the last column: `(Priority)` or `(Resources)` means other jobs are ahead of yours. The cluster is shared and can be busy for many hours. Every Sunday from 12:45 to 5:45 AM (Eastern time) the whole cluster is reserved for weekly performance tests, so a job that would still be running at 12:45 AM on Sunday waits until 5:45 AM. Leave the job in the queue. It starts by itself, so there's no need to cancel and resubmit it, which would only lose its place in the queue.

### `CaseStatus` shows `case.run error`, or `sacct` shows `FAILED`

The run started but stopped partway. To find out why, look at the end of the model's main log, in the run folder:

```bash
cd $MYROOT/scratch/f2000.test/run
ls -t | head
tail -n 30 cesm.log.*
grep -i -m 5 error cesm.log.*
```

`ls -t | head` lists the newest files first. `tail -n 30` shows the last 30 lines of the log, and `grep -i -m 5 error` shows the first 5 lines that contain "error". The log of the component that failed (`atm.log.*`, `lnd.log.*`, `ice.log.*`, `ocn.log.*`) usually says more near its end. These are the causes I'd check first:

- An error that mentions your SST file name: the SST file in `SSTICE_DATA_FILENAME` was moved, renamed or mistyped. Check it with `./xmlquery SSTICE_DATA_FILENAME` and `ls -l <that path>`.
- `ABORT` in `ice.log`: check that the four sea-ice lines from step 5 of the quickstart are in the case, with `cat user_nl_cice`. Add any that are missing in the file editor ({ref}`Editing text files <uhpc-editing>`) and submit again.
- An error about a missing input file: the shared input data does not have a file this case needs. Don't download it yourself. Email me the exact message and leave this case as it is, and I'll add the file.

### `sacct` shows `OUT_OF_MEMORY`

The land model was converting its starting file to the model grid and ran out of memory. Check that the `finidat` line from step 5 of the [quickstart](quickstart.md) is in the case, with `cat user_nl_clm`. Add it in the file editor ({ref}`Editing text files <uhpc-editing>`) if it's missing, and submit again.

### `sacct` shows `TIMEOUT`

The job ran out of its time limit (`JOB_WALLCLOCK_TIME`). The tests in this tutorial normally finish in under an hour, so a timeout means this run was slower than usual. Give the job more time and submit again:

```bash
./xmlchange JOB_WALLCLOCK_TIME=04:00:00
./case.submit -a="--exclude=hpcc03,hpcc04"
```

### `case.run success` but `st_archive error`

The model ran fine, and only the step that copies the output afterwards failed, because it couldn't write to the archive folder. Check `./xmlquery DOUT_S_ROOT`. It must be `/usr/local/research/miyawaki/users/<your-username>/archive/f2000.test`. Fix it with `./xmlchange DOUT_S_ROOT=$MYROOT/archive/f2000.test` and run `./case.submit -a="--exclude=hpcc03,hpcc04"` again.

## Jupyter

### The session stays at `Queued`

Jupyter sessions are jobs too, so they wait for free processors like any other job. It's normal, especially when the cluster is busy. Leave the page open. The session starts by itself, and the button **Connect to Jupyter** appears.

### `ModuleNotFoundError: No module named 'cartopy'`

The `datascience` environment does not have cartopy. Use plain `plt.pcolormesh` maps, as in this tutorial.

## ERA5 and the SST script

### `403 Client Error` or `required licences not accepted`

You have not accepted the ERA5 licence. Open the dataset download page <https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-monthly-means?tab=download>, accept the **Terms of use**, and run the download again.

### `401 Client Error`, `Unauthorized` or `Missing/incomplete configuration file`

The key file `~/.cdsapirc` is missing or wrong. Open it in the file editor ({ref}`Editing text files <uhpc-editing>`) and compare it with step 5 of [Set up Python and an ERA5 account](../sst_bc/python_setup.md). The key must be your own **Personal Access Token**, with no extra spaces.

### The download waits at `accepted` or `running` for a long time

The Climate Data Store has a queue of its own, and a request can wait there for a while before it starts downloading. Leave it running inside tmux and come back later. It hasn't frozen.

### `cdsapi` or `.cdsapirc` is on your Mac

The CDS page has install steps for Windows and macOS. We don't use those steps, because everything runs on the cluster: the tool is installed with `$PY -m pip install --user cdsapi` in step 4 of [Set up Python and an ERA5 account](../sst_bc/python_setup.md), and the key file is `~/.cdsapirc` on the cluster, made in the OnDemand file editor in step 5. A copy on your Mac is unused.

### `ModuleNotFoundError: No module named 'cdsapi'` or `'netCDF4'`

You ran the script with a different Python. Use `$PY make_sst_bc.py ...`, not `python make_sst_bc.py ...`. Check with `echo $PY`. It should print `/usr/local/Dist/anaconda3-latest/envs/datascience/bin/python`.

### `check` says `FAIL`

Don't use that file, because the check found something wrong with it. Rename it so you don't use it by mistake, for example `mv sst_example_enso.nc sst_example_enso.FAILED.nc`, and run the step that made it again, copying the command exactly from the page.
