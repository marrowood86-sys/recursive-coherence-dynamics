#!/usr/bin/env python3
"""
RC-LAMBDA-SWEEP-001
Purpose: Test whether changing lambda shifts the spectral-dimension attractor.
"""

import numpy as np
import scipy.stats as stats

N = 128
N_SEEDS = 30
TOTAL_STEPS = 300
DT = 0.01
ALPHA = 0.15
T_NOISE = 0.02
D_DISS = 0.005
PERTURBATION_STEP = 75

LAMBDA_VALUES = [0.05, 0.10, 0.20, 0.40]


def compute_spectral_dimension(W, max_tau=12):
    w_nonzero = W[W > 0]
    if len(w_nonzero) == 0:
        return 0.0

    thresh = np.percentile(w_nonzero, 75)
    W_eff = np.where(W >= thresh, W, 0.0)

    deg = np.sum(W_eff, axis=1)
    D_inv = np.diag(np.where(deg > 0, 1.0 / deg, 0.0))
    T = D_inv @ W_eff

    T_pow = np.eye(W.shape[0])
    taus = np.arange(2, max_tau + 1, 2)
    returns = []

    for tau in range(1, max_tau + 1):
        T_pow = T_pow @ T
        if tau in taus:
            returns.append(np.mean(np.diag(T_pow)))

    returns = np.array(returns)
    valid = returns > 1e-12

    if np.sum(valid) < 2:
        return 0.0

    slope, *_ = stats.linregress(np.log(taus[valid]), np.log(returns[valid]))
    return np.clip(-2.0 * slope, 0.0, 10.0)


def initialize_system(rng):
    theta = rng.uniform(-np.pi, np.pi, N)
    omega = rng.normal(0, 0.1, N)
    W = rng.uniform(0.01, 0.05, (N, N))
    W = 0.5 * (W + W.T)
    np.fill_diagonal(W, 0)
    return theta, omega, W


def step_rc(theta, omega, W, step, rng, lam):
    if step == PERTURBATION_STEP:
        theta[: max(4, int(0.125 * N))] += np.pi

    theta_diff = theta[np.newaxis, :] - theta[:, np.newaxis]
    rho = np.cos(theta_diff)

    H_row = np.zeros_like(W)
    for i in range(N):
        row = W[i]
        if np.sum(row) > 0:
            p = row / np.sum(row)
            H_row[i, :] = -np.sum(p * np.log(p + 1e-12))

    W_next = W + DT * ALPHA * (rho - lam * H_row)
    W_next = np.clip(W_next, 0.0, 1.0)
    W_next = 0.5 * (W_next + W_next.T)
    np.fill_diagonal(W_next, 0)

    d_theta = omega + (1.0 / N) * np.sum(W_next * np.sin(theta_diff), axis=1)
    d_theta -= D_DISS * theta

    theta_next = theta + DT * d_theta + np.sqrt(DT) * rng.normal(0, T_NOISE, N)
    theta_next = np.mod(theta_next + np.pi, 2 * np.pi) - np.pi

    return theta_next, W_next


print("============================================")
print("RUNNING LAMBDA SWEEP")
print("============================================")

results = {}

for lam in LAMBDA_VALUES:
    ds_values = []

    for s_idx in range(N_SEEDS):
        seed = 700000 + s_idx
        init_rng = np.random.default_rng(seed)
        theta, omega, W = initialize_system(init_rng)

        run_rng = np.random.default_rng(seed + int(lam * 1000000))

        for t in range(TOTAL_STEPS):
            theta, W = step_rc(theta, omega, W, t, run_rng, lam)

        ds_values.append(compute_spectral_dimension(W))

    ds_values = np.array(ds_values)
    results[lam] = ds_values

    print(f"lambda={lam:.2f}: d_s={np.mean(ds_values):.3f} ± {np.std(ds_values):.3f}")

np.savez(
    "data/rc_lambda_sweep_results.npz",
    **{f"lambda_{str(lam).replace('.', '_')}": vals for lam, vals in results.items()}
)

print("[SUCCESS] Lambda sweep saved to data/rc_lambda_sweep_results.npz")
