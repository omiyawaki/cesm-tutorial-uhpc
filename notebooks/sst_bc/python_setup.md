# Set up Python and an ERA5 account

This is a one-time setup. You will use the **Shell** app in Open OnDemand, inside `tmux` (see [Open OnDemand and shell basics](../uhpc/ondemand_basics.md)).

## 1. Make a folder for your SST work

```bash
export MYROOT=/usr/local/research/miyawaki/users/$USER
mkdir -p $MYROOT/sst
cd $MYROOT/sst
pwd
```

`mkdir -p` makes the folder (and does nothing if it already exists). `cd` moves into it, and `pwd` prints where you are. You should see `/usr/local/research/miyawaki/users/<your username>/sst`.

**TODO:** the per-user folders under `/usr/local/research/miyawaki/users` are planned but not created yet.

## 2. Get the script

The script is `tools/make_sst_bc.py` in this tutorial's repository. Get the file from Osamu (or download it from the repository) and save it on your Mac. Then put it in your `sst` folder:

1. In OnDemand, open the **Files App** and type `/usr/local/research/miyawaki/users/<your-username>/sst` in the path box at the top.
2. Click **Upload** and choose `make_sst_bc.py` from your Mac.
3. Back in the Shell, run `ls`. It should list `make_sst_bc.py`.

**TODO:** a shared copy on UHPC, so this becomes a single `cp` command, has not been placed yet.

## 3. Choose the Python to use

UHPC has a ready-made Python environment called `datascience`, with xarray, netCDF4, numpy, scipy and matplotlib (checked on UHPC). Save its location in a variable so the commands stay short:

```bash
export PY=/usr/local/Dist/anaconda3-latest/envs/datascience/bin/python
$PY -c "import xarray, netCDF4, matplotlib; print('python OK')"
```

You should see `python OK`. The `export` lines only last until you close the shell. Add both `export` lines (for `MYROOT` and `PY`) to the end of your `~/.bashrc` so they are set every time you log in:

```bash
nano ~/.bashrc
```

Use the arrow keys to go to the bottom, paste the two lines, then press **Ctrl-O**, **Enter** to save and **Ctrl-X** to quit.

## 4. Install the ERA5 download tool

The download uses the `cdsapi` package, which is not in `datascience`. Install it into your home folder. The cluster reaches the internet through a proxy, so set that first:

```bash
export http_proxy=http://192.168.1.10:8888
export https_proxy=http://192.168.1.10:8888
$PY -m pip install --user cdsapi
$PY -c "import cdsapi; print('cdsapi OK')"
```

**TODO:** it has been checked that PyPI can be reached through the proxy, but not that `pip install --user` into this environment works for a student account.

## 5. Get a free ERA5 (Copernicus) account

ERA5 comes from the Copernicus Climate Data Store (CDS). Do this part in your Mac's web browser:

1. Go to <https://cds.climate.copernicus.eu> and click **Login - Register** to make a free account.
2. Open the dataset page **"ERA5 monthly averaged data on single levels from 1940 to present"**, go to its **Download** tab, scroll to **Terms of use**, and accept the licence. Downloads fail until you do this once.
3. Click your name (top right) to open your profile, and copy your **Personal Access Token** (API key).

Back in the OnDemand Shell, create the key file:

```bash
nano ~/.cdsapirc
```

Type these two lines, with your own token after `key:`:

```
url: https://cds.climate.copernicus.eu/api
key: <paste-your-token-here>
```

Save with **Ctrl-O**, **Enter**, and quit with **Ctrl-X**. Then make the file private, since the key is like a password:

```bash
chmod 600 ~/.cdsapirc
```

`chmod 600` means only you can read or change the file. Never share this file or put it in a git repository.
