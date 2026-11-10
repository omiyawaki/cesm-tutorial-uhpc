# Set up Python and an ERA5 account

This is a one-time setup. You will use the OnDemand Shell tab, inside `tmux` (see [Open OnDemand and shell basics](../uhpc/ondemand_basics.md)), and, for step 5, your Mac's web browser.

## 1. Make a folder for your SST work

```bash
mkdir -p $MYROOT/sst
cd $MYROOT/sst
pwd
```

`mkdir -p` makes the folder (and does nothing if it already exists). `cd` moves into it, and `pwd` prints where you are. You should see `/usr/local/research/miyawaki/users/<your-username>/sst`. `$MYROOT` comes from the line you added to `~/.bashrc` in the quickstart.

## 2. Get the script

A copy of the script is kept on UHPC for everyone in the group. Copy it into your `sst` folder:

```bash
cp /usr/local/research/miyawaki/tutorial/tools/make_sst_bc.py .
ls
```

`cp <from> <to>` copies a file. The `.` at the end means "this folder", so the copy lands in your `sst` folder. `cp` prints nothing when it works, and `ls` should then print exactly one name:

```
make_sst_bc.py
```

If `cp` prints `Permission denied`, your account is not yet in the `res-miyawaki` group: see "Permission denied" in [When something goes wrong](../uhpc/when_things_go_wrong.md). If it prints `No such file or directory`, check the path for typing mistakes (press **Up arrow** to bring the command back). If it still fails, email Professor Miyawaki (see [When something goes wrong](../uhpc/when_things_go_wrong.md)).

## 3. Choose the Python to use

UHPC has a ready-made Python environment called `datascience`, with xarray, netCDF4, numpy, scipy and matplotlib. Save its location in a variable so the commands stay short:

```bash
export PY=/usr/local/Dist/anaconda3-latest/envs/datascience/bin/python
$PY -c "import xarray, netCDF4, matplotlib; print('python OK')"
```

`$PY -c "..."` runs one line of Python with this environment. You should see `python OK`. The `export` line only lasts until you close the shell, so add it to the end of your `~/.bashrc` as well:

```bash
nano ~/.bashrc
```

Use the **down arrow** to go to the bottom, paste the `export PY=...` line, then press **Ctrl-O**, **Enter** to save and **Ctrl-X** to quit.

## 4. Install the ERA5 download tool

The download uses the `cdsapi` package, which is not in `datascience`. Install it into your home folder:

```bash
$PY -m pip install --user cdsapi
$PY -c "import cdsapi; print('cdsapi OK')"
```

`pip install --user` downloads a Python package and installs it in your home folder, where `$PY` finds it. It ends with `Successfully installed cdsapi-...` and a few other package names. The second line should print `cdsapi OK`.

## 5. Get a free ERA5 (Copernicus) account

ERA5 comes from the Copernicus Climate Data Store (CDS). Do items 1 to 3 in your Mac's web browser:

1. Go to <https://cds.climate.copernicus.eu> and click **Login - Register** to make a free account. Confirm it from the email the CDS sends you, then log in.
2. Open the ERA5 dataset's download page, <https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels-monthly-means?tab=download>, while logged in. Scroll to the bottom of the form, to the section **Terms of use**. It lists one licence, the **CC-BY licence**. Click the button there to accept it. If the page says you have already accepted it, go on. Downloads fail with a licence error until you accept it once. You do not need to fill in the rest of the form.
3. Open <https://cds.climate.copernicus.eu/how-to-api> while logged in. The page starts with sections for **Windows users** and **macOS users** that say "Please read How to install and use CDS API on ..." Ignore those sections: you do not install anything on your Mac. Scroll to **Linux users** and its step **1. Setup the CDS Api key**. It shows two lines, starting `url:` and `key:`. If the `key:` line says `<PERSONAL-ACCESS-TOKEN>`, you are not logged in: log in and reload the page. When you are logged in, the `key:` line shows your own **Personal Access Token**, a long string of letters, digits and dashes. Keep this tab open, or copy the two lines into a note on your Mac, so you can paste them in the next step. Ignore the rest of the page (installing the client and the examples), because step 4 above already installed it on the cluster.

Back in the OnDemand Shell tab (not on your Mac), create the key file on the cluster:

```bash
nano ~/.cdsapirc
```

Paste only the two lines `url:` and `key:` from the CDS page with **Cmd-V**, and nothing else. They look like this, with your own token after `key:`:

```
url: https://cds.climate.copernicus.eu/api
key: <paste-your-token-here>
```

Save with **Ctrl-O**, **Enter**, and quit with **Ctrl-X**. Then make the file private, since the key is like a password:

```bash
chmod 600 ~/.cdsapirc
```

`chmod 600` means only you can read or change the file. Never share your token, and never paste it into an email or a chat, including an email to Professor Miyawaki. If you copied it into a note on your Mac, delete the note now.
