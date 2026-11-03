"""Mechanical NCAR (Cheyenne/PBS/GLADE) -> Union HPC (Slurm) substitutions.

Applied to the source of every markdown and code cell in notebooks/ (not to
stored outputs). Run from the repository root:  python3 tools/uhpc_adapt.py
It is idempotent, so it can be re-run after merging upstream changes.
Prose that needs judgment is edited by hand, not here.
"""
import glob
import re
import sys

sys.path.insert(0, "tools")
import nbedit  # noqa: E402

R = "/usr/local/research/miyawaki"
CODE = R + "/cesm/cesm2"            # shared CESM2.1.5 tree (planned read-only)
USR = R + "/users/$USER"            # planned per-user folder
U = r"\$[Uu][Ss][Ee][Rr]"           # $USER or $user

SUBS = [
    # --- paths -------------------------------------------------------------
    (rf"/glade/work/{U}/code/my_cesm_code", CODE),
    (rf"/glade/work/{U}/code/cesm2\.1\.1", CODE),
    (r"/glade/p/cesm/tutorial/cesm2\.1_tutorial2022", CODE),
    (rf"/glade/(?:work|u/home)/{U}/cases", USR + "/cases"),
    (rf"/glade/scratch/{U}/archive", USR + "/archive"),
    (rf"/glade/scratch/{U}", USR + "/scratch"),
    (r"'/glade/scratch/' \+ User \+ '/archive/", f"'{R}/users/' + User + '/archive/"),
    (r'f"/glade/scratch/\{username\}/archive/', f'f"{R}/users/{{username}}/archive/'),
    (rf"/glade/work/{U}(?![A-Za-z])", USR),
    (r"/glade/p/cesmdata/cseg/inputdata", "$DIN_LOC_ROOT"),
    # --- batch system ------------------------------------------------------
    (r"qcmd -- ", ""),
    (r"\./qstat\b", "squeue"),
    (r"\bqstat -u\b", "squeue -u"),
    (r"JOB_QUEUE=regular,PROJECT=\w+", "JOB_QUEUE=hpcc"),
    (r"(\./xmlchange JOB_QUEUE=)regular\b", r"\1hpcc"),
    (r"to run in the queue (`+)regular\1 and the (?:tutorial )?project number (`+)\w+\2",
     r"to run in the UHPC partition \1hpcc\1 (UHPC has no project number)"),
    (r"\. You should use the project number given for this tutorial\.", "."),
    (r'You may need to add ``--project "\w+"`` when creating a new case\.',
     "UHPC has no project number, so you do not need ``--project`` when creating a new case."),
    (r"(\(\d\) )?Check (?:that )?your archive directory on cheyenne "
     r"\([Tt]he path will be different on ot(?:he|eh)r machines\)",
     r"\1Check that your archive directory on UHPC (planned per-user layout; the path will be different on other machines)"),
]


def adapt(text):
    for pat, rep in SUBS:
        text = re.sub(pat, rep, text)
    return text


def main():
    changed = 0
    for path in sorted(glob.glob("notebooks/**/*.ipynb", recursive=True)):
        nb, fmt = nbedit.load(path)
        dirty = False
        for cell in nb["cells"]:
            if cell["cell_type"] not in ("markdown", "code"):
                continue
            old = nbedit.get_src(cell)
            new = adapt(old)
            if new != old:
                nbedit.set_src(cell, new)
                dirty = True
        if dirty:
            nbedit.save(path, nb, fmt)
            changed += 1
            print("changed", path)
    print(changed, "notebooks changed")


if __name__ == "__main__":
    main()
