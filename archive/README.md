# Archived pages

These pages are from the NCAR CESM Tutorial (`tutorial_2023`) and were removed
from the Union HPC edition's table of contents because they are not needed for
atmosphere-only, prescribed-SST (`F` compset) CAM experiments on UHPC. They
are kept here, unchanged apart from earlier UHPC path edits, so they can be
restored by moving them back under `notebooks/` and adding them to `_toc.yml`.
They are not built into the book.

What was moved and why:

- Fully coupled `B1850` exercises (basics first/second run, history files,
  run-type and timestep exercises, CAM tuning exercise): they need the full
  ocean and sea-ice model. The kept exercises were converted to `F2000climo`.
- Hybrid/branch run types: coupled-model workflow, not needed for short F runs.
- Ocean (POP), sea-ice (CICE), land-ice (CISM), biogeochemistry, CAM-chem/WACCM
  and CLM challenge exercises and diagnostics, CVDP and CESM2 Large Ensemble
  pages: other components, or data that exist only on NCAR's GLADE system.
- CAM challenge exercises 2-3 (FHIST from 1850 spin-up) and 6 (source code
  change): need forcing data or code changes that are not set up on UHPC.
- Source-code modification chapter (SourceMods): not needed; output can be
  changed with namelists.
- POP and CICE namelist output pages.
- NCAR shell profile, Fortran, GitHub and porting resource pages.

The upstream originals are at https://github.com/NCAR/CESM-Tutorial (tag
`tutorial_2023`), MIT License (see `LICENSE`).
