# When something goes wrong

This page lists the problems that come up most often on UHPC, what each one means, and what to do. Find the message you see, or the step you were on, and follow the fix. If the fix does not work, email me, then go on to the next step you can do while you wait for my answer.

**To email me:** write to miyawako@union.edu from your Union email, with the subject `CESM tutorial: <page>, step <number>`, and paste the command you typed and the first error message it printed into the body as text.

When a command fails, read the **first** error message it printed, not only the last line. To copy a message out of the Shell tab, select it with the mouse and press **Cmd-C**.

## Getting in

### The OnDemand page does not load, or times out

You are not on the campus network. Connect the **Cisco Secure Client** VPN to `unionvpn.union.edu` and reload the page. ITS explains the setup in [How to Use the Cisco VPN Client (Mac/PC)](https://union.teamdynamix.com/TDClient/1831/Portal/KB/Article/56060/How-to-Use-the-Cisco-VPN-Client-Mac-PC). For problems with the VPN itself, contact the ITS Help Desk at helpdesk@union.edu or (518) 388-6400.

### The sign-in box keeps coming back

The username or password is wrong. Use your cluster username (the first part of your Union email address, the part before `@union.edu`) and your cluster password. The cluster password is not your Union (Okta) password: it is the one you chose the first time you logged in to the cluster. For a forgotten cluster password, email the cluster administrators at hpcadmin@union.edu from your Union email address and ask them to reset it.

### The Shell tab says the connection closed

The OnDemand Shell closes after about 5 minutes without typing, and after about 1 hour in any case. Your work inside tmux is safe. Open **Clusters** → **HPC Cluster Shell Access** again and type `tmux attach -t cesm || tmux new -s cesm`.

### `tmux attach` says `no sessions` or `can't find session`

The tmux session ended, for example because the login computer restarted. If you typed `tmux attach -t cesm || tmux new -s cesm`, a new session has already started, with a green bar at the bottom. If you typed only `tmux attach -t cesm`, type `tmux new -s cesm`. Then `cd` back to the folder you were in, for example `cd $MYROOT/cases/f2000.test`. Anything you were building when the session ended has to be started again.

### `duplicate session: cesm`

You typed `tmux new -s cesm` while a session called `cesm` was still running. Type `tmux attach -t cesm` to go back to it.

### `sessions should be nested with care`

You are already inside tmux (there is a green bar at the bottom of the window), so there is nothing to attach to. Keep working where you are.

## Permissions and setup

### `Permission denied` on anything under `/usr/local/research/miyawaki`, or `ENV.sh: Permission denied`

Your account is not yet in the `res-miyawaki` group, or the group was added after you logged in. Type `id`. If `res-miyawaki` is missing from the list, close every OnDemand tab, sign out, wait an hour, and sign in again. Group changes take up to an hour to reach the cluster. If it is still missing the next day, email me with the subject `CESM tutorial: res-miyawaki missing` and paste the output of `id`.

### `cesm-deps/ENV.sh: No such file or directory`, or `$MYROOT` is empty

The settings from `~/.bashrc` were not loaded. Type `echo $MYROOT`. It should print `/usr/local/research/miyawaki/users/<your-username>`. If it prints an empty line, open `nano ~/.bashrc` and check the three lines from step 3 of the [quickstart](quickstart.md) for typing mistakes, then run `source ~/.bashrc`.

### `Disk quota exceeded`

Your home folder (20 GB) is full. Type `du -sh ~/.conda ~/.cache` to see what is using it. The `~/.cache` folder can be emptied with `rm -r ~/.cache/pip`. Keep CESM files in `$MYROOT`, never in your home folder.

## Creating, setting up and building a case

### `create_newcase` says the case directory already exists

You ran `create_newcase` twice with the same case name. Use the case you already have, `cd $MYROOT/cases/f2000.test`, and continue with step 5 of the quickstart.

### `case.setup` or `case.build` fails with `Permission denied` and a path that does not contain your username

The case was created without `--output-root $MYROOT/scratch`, so it points at a folder that is not yours. Make a new case with a new name, for example `f2000.test2`, and type the `create_newcase` command exactly as shown, including `--output-root`.

### `case.build` stops with an error

The build prints the name of a log file next to the error, for example `.../bld/atm.bldlog.<date>`. Open it with `less <path-to-log>` and press **Shift-G** to jump to the end, where the error is. Also check that you ran the `source .../ENV.sh` line in this shell (it is in your `~/.bashrc`). Then run `./case.build` again.

## Jobs

### `squeue` shows `PD` for a long time

`PD` means the job is waiting for free processors. The reason is in the last column: `(Priority)` or `(Resources)` means other jobs are ahead of yours. The cluster is shared and can be busy for many hours. Every Sunday from 12:45 to 5:45 AM (Eastern time) the whole cluster is reserved for weekly performance tests, so a job that would still be running at 12:45 AM on Sunday waits until 5:45 AM. Leave the job in the queue. It starts by itself.

### `CaseStatus` shows `case.run error`, or `sacct` shows `FAILED`

Look at the end of the model's main log, in the run folder:

```bash
cd $MYROOT/scratch/f2000.test/run
ls -t | head
tail -n 30 cesm.log.*
grep -i -m 5 error cesm.log.*
```

`ls -t | head` lists the newest files first. `tail -n 30` shows the last 30 lines of the log, and `grep -i -m 5 error` shows the first 5 lines that contain "error". The log of the component that failed (`atm.log.*`, `lnd.log.*`, `ice.log.*`, `ocn.log.*`) usually says more near its end. Common causes:

- An error that mentions your SST file name: the SST file in `SSTICE_DATA_FILENAME` was moved, renamed or mistyped. Check it with `./xmlquery SSTICE_DATA_FILENAME` and `ls -l <that path>`.
- `ABORT` in `ice.log`: check that the four sea-ice lines from step 5 of the quickstart are in the case, with `cat user_nl_cice`. Add any that are missing with `nano user_nl_cice` and submit again.
- An error about a missing input file: the shared input data does not have a file this case needs. Do not download it yourself. Email me the exact message, and leave this case as it is.

### `sacct` shows `TIMEOUT`

The job ran out of its time limit (`JOB_WALLCLOCK_TIME`). The tests in this tutorial normally finish in under an hour. Give the job more time and submit again:

```bash
./xmlchange JOB_WALLCLOCK_TIME=04:00:00
./case.submit -a "--exclude=hpcc03,hpcc04"
```

### `case.run success` but `st_archive error`

The archive step could not write its output. Check `./xmlquery DOUT_S_ROOT`. It must be `/usr/local/research/miyawaki/users/<your-username>/archive/f2000.test`. Fix it with `./xmlchange DOUT_S_ROOT=$MYROOT/archive/f2000.test` and run `./case.submit -a "--exclude=hpcc03,hpcc04"` again.

## Jupyter

### The session stays at `Queued`

Jupyter sessions are jobs too, so they wait for free processors like any other job. Leave the page open. The session starts by itself, and the button **Connect to Jupyter** appears.

### `ModuleNotFoundError: No module named 'cartopy'`

The `datascience` environment does not have cartopy. Use plain `plt.pcolormesh` maps, as in this tutorial.

## ERA5 and the SST script

### `403 Client Error` or `required licences not accepted`

You have not accepted the ERA5 licence. Open the dataset page "ERA5 monthly averaged data on single levels from 1940 to present" on the Climate Data Store, go to its **Download** tab, accept the **Terms of use**, and run the download again.

### `401 Client Error`, `Unauthorized` or `Missing/incomplete configuration file`

The key file `~/.cdsapirc` is missing or wrong. Open it with `nano ~/.cdsapirc` and compare it with step 5 of [Set up Python and an ERA5 account](../sst_bc/python_setup.md). The key must be your own **Personal Access Token**, with no extra spaces.

### The download waits at `accepted` or `running` for a long time

The Climate Data Store has a queue. Leave it running inside tmux and come back later.

### `ModuleNotFoundError: No module named 'cdsapi'` or `'netCDF4'`

You ran the script with a different Python. Use `$PY make_sst_bc.py ...`, not `python make_sst_bc.py ...`. Check with `echo $PY`. It should print `/usr/local/Dist/anaconda3-latest/envs/datascience/bin/python`.

### `check` says `FAIL`

Do not use that file. Delete it with `rm <file name>` and run the step that made it again, copying the command exactly from the page.
