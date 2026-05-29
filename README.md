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
### Interpretation

The ablation results suggest that spectral-dimension reduction is primarily driven by the phase-alignment reinforcement term.

CONTROL_C closely matches the Active RC model because both contain the same phase-proximity weight update. When nodes enter similar phases, their connecting weights strengthen, causing the network to condense into localized structural pathways. This produces the observed drop in spectral dimension.

CONTROL_A, CONTROL_B, and CONTROL_E fail to reproduce this condensed phase because they lack the phase-alignment reinforcement term. CONTROL_E isolates the entropy term alone, but without phase proximity it has no coordinate mechanism for selective structure formation.

CONTROL_D collapses because pure Kuramoto synchronization produces global phase-lock without an adaptive weighted topology. The result is an over-condensed, nearly singular structure.

The key distinction between RC and CONTROL_C is expected to appear over larger networks or longer time horizons. CONTROL_C behaves like an unconstrained condensation engine, while Active RC includes the entropy penalty as a stabilizing regulator. Phase alignment lowers dimensionality; entropy regulation prevents runaway over-condensation.

Thus, the working hypothesis is that Recursive Coherence is not entropy-only. It is a regulated condensation process: phase alignment acts as the primary attractive mechanism, while row-entropy acts as the geometric brake.
