# Recursive Coherence Dynamics

This repository contains simulation code, controls, ablations, scaling tests, and replication checks for a toy adaptive weighted-graph model that exhibits robust spectral-dimension convergence near d_s ≈ 2.

This project does not claim to prove emergent spacetime or replace established physics.

It tests one narrow complex-systems question:

Does an adaptive recursive-coherence graph update rule produce a reproducible spectral-dimension attractor that is not reproduced by synchronization-only or topology-null controls?

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the main production ensemble:

```bash
python src/rc_diag_ensemble_runner.py
```

Run scale tests:

```bash
python src/rc_scale_horizon_runner.py
```

Run sensitivity tests:

```bash
python src/rc_sensitivity_engine.py
```

Run verification after data files exist:

```bash
python tests/verify_assets.py
```
