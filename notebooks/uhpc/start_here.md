# Getting started on Union HPC

This tutorial teaches you to run CESM, NCAR's climate model, on Union's computing cluster, and to change the sea surface temperatures (SSTs) that drive the model's atmosphere. That's how a climate model experiment works: you change one thing, run the model, and compare the result with a run where nothing changed. Once you can do that, you can design and run experiments of your own.

You'll start with two short test runs of 5 days each. The first run checks that the model builds and runs at all. The second checks that it reads an SST file you made yourself, which is the same kind of file you'll change for your own experiment. After each run you'll open the output in a Jupyter notebook and make a map, so you can see for yourself that the model did something sensible.

You'll get error messages along the way. Everyone does with CESM, and most of them have a known fix. Look for yours on [When something goes wrong](when_things_go_wrong.md). If you get stuck, email me (<a href="mailto:miyawako@union.edu">miyawako@union.edu</a>) and paste the command you typed and the error you're seeing, and I'll help. While you wait, go on with whatever you can do without it.

## First session: check your setup

You only need to do these once, at the start of your first session.

1. **Install the Union VPN.** The cluster's websites only load on the campus network or through the Union VPN, so you'll need the VPN whenever you're off campus. In your Mac's web browser, go to <https://unionvpn.union.edu>, set **Group** to **STUDENT**, and log in with your Union username (without `@union.edu`) and your Union password. Click **Download** and install **Cisco Secure Client**. When macOS shows "Action Required", open **System Settings** → **Privacy & Security** and allow the Cisco Secure Client VPN service. Then open the app, type `unionvpn.union.edu` as the server if it's empty, choose the **STUDENT** group, and sign in through the Union (Okta) login page. ITS describes the same steps in [How to Use the Cisco VPN Client (Mac/PC)](https://union.teamdynamix.com/TDClient/1831/Portal/KB/Article/56060/How-to-Use-the-Cisco-VPN-Client-Mac-PC). If the VPN itself gives you trouble, the ITS Help Desk can fix it faster than I can: <a href="mailto:helpdesk@union.edu">helpdesk@union.edu</a> or (518) 388-6400.
2. **Sign in to the cluster.** Connect the VPN, go to <https://ondemand.hpc.union.edu>, and sign in. Your cluster username is the first part of your Union email address (the part before `@union.edu`). The password is where people usually get stuck: your cluster password is not your Union (Okta) password. The cluster administrators emailed you a temporary password when they made your account, and you chose a new cluster password the first time you logged in. That cluster password is the one to use here, and your Union password is only for the VPN. If you haven't logged in to the cluster yet and aren't sure how to set your password, email me and we'll do it together.
3. **Check your group.** Click **Clusters** → **HPC Cluster Shell Access**. A command line opens in a new browser tab, which I'll call the OnDemand Shell tab. Type `id` and press **Enter**. The list of groups should include `res-miyawaki`, our research group, which owns the CESM files. Without it you can't read the model code.

If `id` doesn't list `res-miyawaki`, I haven't added you to the group yet, so just email me and I'll add you. In the meantime you can do step 1 of "The steps" below, which doesn't need the group. Once I've added you, close every OnDemand tab, sign out, and sign in again. Group changes can take up to an hour to reach the cluster, so if it's still missing right away, give it a little time.

## Every time you sit down to work

1. Connect the Cisco Secure Client VPN.
2. Go to <https://ondemand.hpc.union.edu> and sign in.
3. Click **Clusters** → **HPC Cluster Shell Access**.
4. Type `tmux attach -t cesm || tmux new -s cesm` and press **Enter**. This puts you back where you left off, or starts a new tmux session if there isn't one. You'll know you're inside tmux when there's a green bar at the bottom of the window. If that bar is already there, skip this line. [Open OnDemand and shell basics](ondemand_basics.md) explains what tmux is and why we use it.

When you're done for the day, close the browser tab and disconnect the VPN. Your tmux session and any jobs you've submitted keep running on the cluster without you.

## The steps

1. **Learn the tools.** Read [Open OnDemand and shell basics](ondemand_basics.md) and try each command in the Shell basics table, so the commands in the next steps aren't new to you. Then start one Jupyter session and run the import test in its step 5, which is how you'll make plots later. Stop the session when you're done: switch to the OnDemand dashboard tab (not the JupyterLab tab), click **My Interactive Sessions** in the top menu, and click **Delete** on the Jupyter session.
2. **Make your first run.** Follow the [UHPC quickstart](quickstart.md) from top to bottom. You're done when `cat CaseStatus` shows `case.run success` and `st_archive success` and your surface temperature map looks like the example on that page.
3. **Understand what you just did.** The quickstart has you type the commands with only short explanations. Now read [Differences from the NCAR tutorial](differences.md), then the [CESM Basics](../basics/basics_overview.ipynb) chapter, from its first page through "Checking Your Run", to see what each step was doing. Read these pages, but skip their exercises, because you already ran the UHPC versions in the quickstart. Don't paste their commands either, since they're written for NCAR's computers. The exceptions are the `ls`, `cd` and `pwd` commands on "Workspaces" and "Explore CESM Code", which only look at files, so you can type those.
4. **Make your own SST boundary condition.** This is the step closest to what you'll do in your own experiment. Work through the five pages of [Making your own SST boundary conditions](../sst_bc/sst_bc.md). You'll download ERA5 data, turn it into a CESM SST file, add an idealized El Niño-type warm patch, and run a 5-day test with it. You're done when the ocean log shows `sst_example_enso.nc` and you've made the map of how rainfall changed.
5. **Write down your questions.** Keep a list of anything that was unclear, any error you couldn't fix, and anything you'd like to try next. Bring it to our next research meeting and we'll go through it together.

## Sharing the cluster

The cluster is shared with other people on campus, so a few habits matter. Stick to the two 5-day tests here, and check with me before you submit anything longer. Always submit with `./case.submit -a="--exclude=hpcc03,hpcc04"`, which keeps your job off the GPU nodes.

Every Sunday from 12:45 to 5:45 AM (Eastern time) the whole cluster is reserved for weekly maintenance tests, so a job that would still be running at 12:45 AM on Sunday waits in the queue (`PD` in `squeue`) until 5:45 AM. That's expected, so just leave it there.

Keep your work in your own folder, `/usr/local/research/miyawaki/users/<your-username>`, and leave everything else under `/usr/local/research/miyawaki` alone, since that's where my runs and the shared model files live. Please don't delete anything in your folder without checking with me, and never delete anything in an `archive` folder. And keep your cluster password and your ERA5 key to yourself, even from me.
