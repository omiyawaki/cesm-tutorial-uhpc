# Provenance

This repository is an adaptation of the NCAR CESM Tutorial for running CESM2 on
Union College's high-performance computing cluster (UHPC).

- Upstream repository: https://github.com/NCAR/CESM-Tutorial
- Upstream site: https://ncar.github.io/CESM-Tutorial/
- Starting point: upstream tag `tutorial_2023` (July 2023), commit
  `49f5b2ecd288009e8c96ddd3144e79460c689e40` (`49f5b2e`), which is based on
  `release-cesm2.1.4` and written for NCAR's Cheyenne/Casper systems (PBS).
- License: MIT, see `LICENSE`. The original copyright notice and NCAR/CGD
  attribution are kept unchanged.

The first commit on `main` after the upstream history is this file. Every later
commit is a UHPC adaptation. The upstream remote is kept so that
version-independent fixes from NCAR can be merged or cherry-picked later:

```bash
git remote add upstream https://github.com/NCAR/CESM-Tutorial.git   # if missing
git fetch upstream --tags
```

UHPC runs `release-cesm2.1.5` (cime5.6.49, CAM cam_cesm2_1_rel_60, CLM5.0.37),
a small step from the tutorial's `release-cesm2.1.4`. The CESM model code
itself is distributed under its own license terms; this repository contains
only the tutorial text, notebooks and images.
