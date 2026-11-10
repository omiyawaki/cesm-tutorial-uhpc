# Over break: what to do, in order

This page is your plan for working through the tutorial on your own over break. Do the steps in order. Each step links to the page that explains it. Together they take about two working days, spread over as many sessions as you like. The pages are also in this order in the menu on the left, so the **Next** button at the bottom of each page takes you along the same path.

Over break you run two 5-day tests. They only prove that the model runs and reads your SST file. The atmosphere's monthly output folder (`atm/hist`) stays empty on purpose, and making maps of the model's output comes next term.

Professor Miyawaki will be slow to answer email over break, so every common problem has a fix you can do yourself on [When something goes wrong](when_things_go_wrong.md). When a fix does not work, email Professor Miyawaki, then go on to the next step you can do while you wait for an answer.

**To email Professor Miyawaki:** write to <a href="mailto:miyawako@union.edu">miyawako@union.edu</a> from your Union email, with the subject `CESM tutorial: <page>, step <number>`, and paste the command you typed and the first error message it printed into the body as text.

## Your first session: check your setup

Do these once, at the start of your first session.

1. **Install the Union VPN.** The cluster's websites only load on the campus network or through the Union VPN, so you need the VPN whenever you are off campus. In your Mac's web browser, go to <https://unionvpn.union.edu>, set **Group** to **STUDENT**, and log in with your Union username (without `@union.edu`) and your Union password. Click **Download** and install **Cisco Secure Client**. When macOS shows "Action Required", open **System Settings** → **Privacy & Security** and allow the Cisco Secure Client VPN service. Open the app, type `unionvpn.union.edu` as the server if it is empty, choose the **STUDENT** group, and sign in through the Union (Okta) login page. ITS describes the same steps in [How to Use the Cisco VPN Client (Mac/PC)](https://union.teamdynamix.com/TDClient/1831/Portal/KB/Article/56060/How-to-Use-the-Cisco-VPN-Client-Mac-PC). For problems with the VPN itself, contact the ITS Help Desk at <a href="mailto:helpdesk@union.edu">helpdesk@union.edu</a> or (518) 388-6400.
2. **Sign in to the cluster.** Connect the VPN, go to <https://ondemand.hpc.union.edu>, and sign in with your cluster username and your cluster password. The cluster password is not your Union password (see step 0 of the [quickstart](quickstart.md)).
3. **Check your group.** Click **Clusters** → **HPC Cluster Shell Access**. A command line opens in a new browser tab, the OnDemand Shell tab. Type `id` and press **Enter**. The list of groups should include `res-miyawaki`, the research group that owns the CESM files.

The cluster administrators are adding you to `res-miyawaki`. If `id` does not list it yet, do step 1 of "The steps" below, which does not need the group, then close every OnDemand tab, sign out, and type `id` again in your next session. Group changes take up to an hour to reach the cluster. If `res-miyawaki` is still missing a day later, email Professor Miyawaki with the subject `CESM tutorial: res-miyawaki missing` and paste the output of `id`.

## Every time you sit down to work

1. Connect the Cisco Secure Client VPN.
2. Go to <https://ondemand.hpc.union.edu> and sign in.
3. Click **Clusters** → **HPC Cluster Shell Access**.
4. Type `tmux attach -t cesm || tmux new -s cesm` and press **Enter**. This goes back to where you were, or starts a new tmux session if there is none ([Open OnDemand and shell basics](ondemand_basics.md) explains it).

When you finish, close the browser tab and disconnect the VPN. Your tmux session and any submitted jobs keep running on the cluster.

## The steps

1. **Learn the tools (about 1 hour).** Read [Open OnDemand and shell basics](ondemand_basics.md) and try each command in the Shell basics table. Start one Jupyter session and run the import test in its step 5, then stop the session: in the top menu click **My Interactive Sessions**, and click **Delete** on the Jupyter session.
2. **Make your first run (about 2 hours, most of it waiting).** Follow the [UHPC quickstart](quickstart.md) from top to bottom. You are done when `cat CaseStatus` shows `case.run success` and `st_archive success`.
3. **Understand what you just did (about 2 hours of reading).** Read [Differences from the NCAR tutorial](differences.md), then read the [CESM Basics](../basics/basics_overview.ipynb) chapter, from its first page through "Checking Your Run". It explains each command from the quickstart in more detail. Only read these pages, and skip their exercises, because you already ran the UHPC versions in the quickstart. Do not paste their commands. The exceptions are the `ls`, `cd` and `pwd` commands on "Workspaces" and "Explore CESM Code", which only look at files, so you can type those. Each page starts with a note that says what to type there, if anything.
4. **Make your own SST boundary condition (about 3 hours).** Work through the five pages of [Making your own SST boundary conditions](../sst_bc/sst_bc.md) in order. You download ERA5 data, turn it into a CESM SST file, add an idealized El Niño-type warm patch, and run a 5-day test with it. You are done when the ocean log shows `sst_example_enso.nc`.
5. **Write down your questions.** Keep a list of anything that was unclear, any error you could not fix, and anything you would like to try next. Bring it to your first meeting with Professor Miyawaki next term. This is the end of the plan for the break. In the menu on the left, everything under "Next term and reference" is for next term.

## Rules for working alone

- Run only the two 5-day tests in this tutorial. Do not submit anything longer.
- Always submit with `./case.submit -a "--exclude=hpcc03,hpcc04"`.
- Every Sunday from 12:45 to 5:45 AM (Eastern time) the whole cluster is reserved for weekly maintenance tests. A job that would still be running at 12:45 AM on Sunday waits in the queue (`PD` in `squeue`) until 5:45 AM. That is normal. Leave it in the queue.
- Keep everything in your own folder, `/usr/local/research/miyawaki/users/<your-username>`. Do not change or delete files anywhere else under `/usr/local/research/miyawaki`.
- Do not delete anything in your folder this term, and never delete anything in an `archive` folder. Your folder has plenty of space for both tests.
- Never share your cluster password or your ERA5 key.
