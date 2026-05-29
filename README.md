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

 Why the Attractor Selects \(d_s \approx 2\)

The Recursive Coherence attractor selects \(d_s \approx 2\) because the update rule balances two opposing geometric flows.

The phase-alignment term \(\rho_{ij}\) acts as a condensing force. It strengthens edges between nodes with similar phases, causing the graph to lose random high-dimensional connectivity and organize into coherent local neighborhoods.

If this term acted alone, the graph would over-condense into chains, cliques, or isolated phase-locked clusters. This would drive the effective spectral dimension toward \(d_s \approx 1\) or lower.

The row-entropy term \(H_i\) acts as a distributing regulator. It penalizes excessive concentration of weights in each node’s neighborhood. This prevents the network from collapsing into a single dominant pathway while still allowing local coherence to form.

The fixed point occurs when the alignment gain and entropy penalty scale together:

\[
\rho_{ij} \sim \lambda H_i
\]

At this balance, each node maintains more than a one-dimensional path-like neighborhood, but not enough independent connections to behave like a three-dimensional random volume. The resulting random-walk return probability follows approximately

\[
P(\tau) \sim \tau^{-d_s/2}
\]

with

\[
d_s \approx 2.
\]

Thus, \(d_s \approx 2\) is selected because it is the stable intermediate geometry between runaway one-dimensional condensation and uncontrolled high-dimensional diffusion.

In this interpretation:

- \(d_s \approx 1\) corresponds to over-condensed chain-like structure.
- \(d_s \approx 3\) corresponds to excessive unconstrained volume-like diffusion.
- \(d_s \approx 2\) corresponds to regulated coherent surface-like propagation.

The RC attractor is therefore not arbitrary. It emerges as the stable point where phase alignment creates coherence while entropy regulation preserves enough branching structure to prevent collapse.
The key distinction between RC and CONTROL_C is expected to appear over larger networks or longer time horizons. CONTROL_C behaves like an unconstrained condensation engine, while Active RC includes the entropy penalty as a stabilizing regulator. Phase alignment lowers dimensionality; entropy regulation prevents runaway over-condensation.

Thus, the working hypothesis is that Recursive Coherence is not entropy-only. It is a regulated condensation process: phase alignment acts as the primary attractive mechanism, while row-entropy acts as the geometric brake.
