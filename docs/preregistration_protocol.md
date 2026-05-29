# Pre-Registration Protocol

## Primary Question

Does the Active RC model produce stable spectral-dimension convergence near d_s ≈ 2 while controls fail to reproduce this behavior?

## Main Controls

- Control A: Random rewiring
- Control B: Static weights, dynamic phases
- Control C: No entropy filter
- Control D: Pure Kuramoto baseline

## Acceptance Criteria

- RC d_s pass rate in [1.85, 2.15] must be >= 80%.
- RC must separate from Control D on spectral dimension.
- Scaling tests must show stable d_s near 2 across N = 64, 128, 256.
- Sensitivity tests must show stability across sparsification thresholds and perturbation fractions.
