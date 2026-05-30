# Recursive Coherence Dynamics

## Overview

Recursive Coherence Dynamics (RCD) is a computational research framework exploring the emergence of low-dimensional spectral organization in adaptive, co-evolving graphs.

The model studies whether stable low-dimensional spectral attractors can emerge from simple dual-feedback loops, specifically the interaction between phase-synchronization dynamics and localized entropy regulation, without requiring embedded spatial coordinates or externally imposed geometric constraints.

## Project Status

This repository serves as the official companion to the white paper:

**Recursive Coherence Dynamics: Emergence of Robust Low-Dimensional Spectral Organization in Adaptive Graphs**

The project has transitioned from an exploratory simulation into an empirical study of emergent order parameters in adaptive network topology.

## Key Findings

### Generative Asymmetry

Ablation studies indicate that phase alignment acts as the primary generative mechanism for dimensional reduction, while entropy regulation serves as a stabilizing brake that prevents structural runaway.

### Finite-Size Scaling

Simulations across system sizes from **N = 32** to **N = 512** show that the emergent spectral attractor remains stable under enlargement of system size.

The observed ensemble variance decreases substantially as **N** increases, suggesting convergence toward a well-defined large-system limit.

### Emergent Order Parameter

The spectral dimension **d_s** is interpreted not as a fixed universal constant, but as a macroscopic order parameter describing the collective organization of the adaptive graph.

## Current Results

Finite-size scaling under the standardized weak-coupling initialization regime produced:

| System Size | Measured Spectral Dimension |
| ----------- | --------------------------- |
| N = 32      | 0.972 ± 0.083               |
| N = 64      | 0.965 ± 0.047               |
| N = 128     | 0.972 ± 0.039               |
| N = 256     | 0.982 ± 0.020               |
| N = 512     | 0.994 ± 0.010               |

## Replication & Verification

To reproduce the main diagnostics, clone the repository and install the required dependencies.

```bash
git clone https://github.com/marrowood86-sys/recursive-coherence-dynamics.git
cd recursive-coherence-dynamics
pip install -r requirements.txt
```

Run the available diagnostic scripts:

```bash
python src/rc_diag_ensemble_runner.py
python src/rc_lambda_sweep.py
python src/rc_size_scaling.py/rc_size_scaling.py
```

## Future Research Roadmap

Current work focuses on:

* Completing the full threshold-dependence mapping.
* Systematically exploring the relationship between initial connectivity density and final attractor position.
* Testing scaling behavior beyond **N = 512**.
* Developing a first-principles derivation connecting microscopic update rules to macroscopic attractor coordinates.

## Disclaimer

This repository contains an exploratory computational model. The results should be interpreted as evidence of emergent low-dimensional organization in a simulated adaptive graph system, not as a claim of physical spacetime emergence or a completed theory of quantum gravity.
