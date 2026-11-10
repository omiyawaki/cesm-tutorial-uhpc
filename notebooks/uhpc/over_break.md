# Over break: what to do, in order

This page is your plan for working through the tutorial on your own over break. Do the steps in order. Each step links to the page that explains it. Together they take about two working days, spread over as many sessions as you like.

I will be slow to answer email over break, so every common problem has a fix you can do yourself on [When something goes wrong](when_things_go_wrong.md). When a fix does not work, write down the exact message, go on to the next step you can do, and bring the message to our first meeting next term.

## Before you leave campus

Do these at our last meeting, or any time before you leave.

1. **Install the Union VPN.** The cluster's websites only load on the campus network or through the Union VPN, so you need the VPN for everything over break. In your Mac's web browser, go to <https://unionvpn.union.edu>, set **Group** to **STUDENT**, and log in with your Union username (without `@union.edu`) and password. Click **Download** and install **Cisco Secure Client**. When macOS shows "Action Required", open **System Settings** → **Privacy & Security** and allow the Cisco Secure Client VPN service. Open the app, type `unionvpn.union.edu` as the server if it is empty, choose the **STUDENT** group, and sign in through the Union (Okta) login page. ITS describes the same steps in "How to Use the Cisco VPN Client (Mac/PC)" on the ITS knowledge base.
2. **Test the cluster from the VPN.** Connect the VPN, go to <https://ondemand.hpc.union.edu>, and sign in with your cluster username and password. Click **Clusters** → **HPC Cluster Shell Access** and type `id`. The list of groups must include `res-miyawaki`. If it does not, tell me before you leave.
3. **Make a free ERA5 (Copernicus) account.** Do items 1 to 3 of step 5 of [Set up Python and an ERA5 account](../sst_bc/python_setup.md) in your Mac's web browser. You make the key file on the cluster later, when you reach that page.

## Every time you sit down to work

1. Connect the Cisco Secure Client VPN.
2. Go to <https://ondemand.hpc.union.edu> and sign in.
3. Click **Clusters** → **HPC Cluster Shell Access**.
4. Type `tmux attach -t cesm` to get back to where you were. If it says `no sessions`, type `tmux new -s cesm` instead.

When you finish, close the browser tab and disconnect the VPN. Your tmux session and any submitted jobs keep running on the cluster.

## The steps

1. **Learn the tools (about 1 hour).** Read [Open OnDemand and shell basics](ondemand_basics.md) and try each command in the Shell basics table. Start one Jupyter session and run the import test in its step 5, then stop the session from **My Interactive Sessions** with **Delete**.
2. **Make your first run (about 2 hours, most of it waiting).** Follow the [UHPC quickstart](quickstart.md) from top to bottom. You are done when `cat CaseStatus` shows `case.run success` and `st_archive success`.
3. **Understand what you just did (about 2 hours of reading).** Read the [CESM Basics](../basics/basics_overview.ipynb) chapter, from "Workspaces" through "Checking Your Run". It explains each command from the quickstart in more detail. The pages are NCAR's, so read [Differences from the NCAR tutorial](differences.md) first and do not run their commands. You already ran the UHPC versions.
4. **Make your own SST boundary condition (about 3 hours).** Work through the five pages of [Making your own SST boundary conditions](../sst_bc/sst_bc.md) in order. You download ERA5 data, turn it into a CESM SST file, add an idealized El Niño-type warm patch, and run a 5-day test with it. You are done when the ocean log shows `sst_example_enso.nc`.
5. **Write down your questions.** Keep a list of anything that was unclear, any error you could not fix, and anything you would like to try next. Bring it to our first meeting next term.

## Rules for working alone

- Run only the two 5-day tests in this tutorial. Do not submit anything longer.
- Always submit with `./case.submit -a "--exclude=hpcc03,hpcc04"`.
- Keep everything in your own folder, `/usr/local/research/miyawaki/users/<your-username>`. Do not change or delete files anywhere else under `/usr/local/research/miyawaki`.
- Never delete anything in an `archive` folder.
- Never share your cluster password or your ERA5 key.
