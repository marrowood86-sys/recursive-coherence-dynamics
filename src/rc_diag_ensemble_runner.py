#!/usr/bin/env python3
"""
RUN ID: RC-DIAG-002_through_101_ENSEMBLE_PRODUCTION
Purpose: Rigorous complex-systems validation of Recursive Coherence against Controls A-D.
"""

import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
from pathlib import Path

# DEBUG MODE: set these small first. Change to 100/250/51 after testing.
N_SEEDS = 5
TOTAL_STEPS = 50
PERTURBATION_STEP = 15

# PRODUCTION SETTINGS:
# N_SEEDS = 100
# TOTAL_STEPS = 250
# PERTURBATION_STEP = 51

N_NODES = 32
DT = 0.01
ALPHA = 0.15
LAMBDA = 0.05
T_NOISE = 0.02
D_DISS = 0.005
K_KURAMOTO = 0.50

MODELS = ["RC", "CONTROL_A", "CONTROL_B", "CONTROL_C", "CONTROL_D"]


def compute_structural_entropy(W):
    W_sum = np.sum(W)
    if W_sum == 0:
        return 0.0
    P = W / W_sum
    P = P[P > 1e-12]
    return float(-np.sum(P * np.log(P)))


def compute_spectral_dimension(W, max_tau=12):
    N = W.shape[0]
    w_nonzero = W[W > 0]
    if len(w_nonzero) == 0:
        return 0.0

    thresh = np.percentile(w_nonzero, 75)
    W_eff = np.where(W >= thresh, W, 0.0)

    deg = np.sum(W_eff, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        D_inv = np.diag(np.where(deg > 0, 1.0 / deg, 0.0))

    T = np.dot(D_inv, W_eff)
    T_pow = np.eye(N)
    return_probs = []

    taus = np.arange(2, max_tau + 1, 2)
    for tau in range(1, max_tau + 1):
        T_pow = np.dot(T_pow, T)
        if tau in taus:
            return_probs.append(np.mean(np.diag(T_pow)))

    return_probs = np.array(return_probs)
    valid = return_probs > 1e-12
    if np.sum(valid) < 2:
        return 0.0

    slope, _, _, _, _ = stats.linregress(np.log(taus[valid]), np.log(return_probs[valid]))
    return float(np.clip(-2.0 * slope, 0.0, 10.0))


def compute_curvature_proxy_bounds(W):
    deg = np.sum(W, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        D_inv = np.where(deg > 0, 1.0 / deg, 0.0)

    M = W * D_inv[:, np.newaxis]
    proxies = []
    N = W.shape[0]

    for i in range(N):
        for j in range(i + 1, N):
            if W[i, j] > 0.01:
                emd_proxy = np.sum(np.abs(M[i] - M[j]))
                d_ij = 1.0 / (W[i, j] + 1e-6)
                kappa_proxy = 1.0 - (emd_proxy / d_ij)
                proxies.append(kappa_proxy)

    if not proxies:
        return 0.0, 0.0
    return float(np.min(proxies)), float(np.max(proxies))


def initialize_system(rng, N=N_NODES):
    theta = rng.uniform(-np.pi, np.pi, N)
    omega = rng.normal(0, 0.1, N)
    W = rng.uniform(0.01, 0.05, (N, N))
    W = 0.5 * (W + W.T)
    np.fill_diagonal(W, 0)
    return theta, omega, W


def run_simulation_step(model_type, theta, omega, W, step, rng):
    N = W.shape[0]

    if step == PERTURBATION_STEP:
        theta[0:4] += np.pi

    theta_diff = theta[np.newaxis, :] - theta[:, np.newaxis]
    rho = np.cos(theta_diff)

    if model_type == "RC":
        H_row = np.zeros_like(W)
        for i in range(N):
            row = W[i]
            if np.sum(row) > 0:
                p = row / np.sum(row)
                H_row[i, :] = -np.sum(p * np.log(p + 1e-12))
        W_next = W + DT * ALPHA * (rho - LAMBDA * H_row)
        W_next = np.clip(W_next, 0.0, 1.0)

    elif model_type == "CONTROL_A":
        W_next = rng.uniform(0.01, 1.0, (N, N))

    elif model_type == "CONTROL_B":
        W_next = W.copy()

    elif model_type == "CONTROL_C":
        W_next = np.clip(W + DT * ALPHA * rho, 0.0, 1.0)

    elif model_type == "CONTROL_D":
        W_next = np.ones((N, N)) * (K_KURAMOTO / N)

    else:
        raise ValueError(f"Unknown model type: {model_type}")

    W_next = 0.5 * (W_next + W_next.T)
    np.fill_diagonal(W_next, 0)

    d_theta = omega + (1.0 / N) * np.sum(W_next * np.sin(theta_diff), axis=1)
    if model_type != "CONTROL_D":
        d_theta -= D_DISS * theta

    theta_next = theta + DT * d_theta + np.sqrt(DT) * rng.normal(0, T_NOISE, N)
    theta_next = np.mod(theta_next + np.pi, 2 * np.pi) - np.pi

    return theta_next, W_next


def main():
    data_store = {
        m: {
            "entropy": np.zeros((N_SEEDS, TOTAL_STEPS)),
            "ds": np.zeros((N_SEEDS, TOTAL_STEPS)),
            "r_param": np.zeros((N_SEEDS, TOTAL_STEPS)),
            "k_var": np.zeros((N_SEEDS, TOTAL_STEPS)),
        }
        for m in MODELS
    }

    base_seeds = np.arange(421973, 421973 + N_SEEDS)

    print(f"Executing simulation loop: {N_SEEDS} seeds, {TOTAL_STEPS} steps")

    for s_idx, seed in enumerate(base_seeds):
        init_rng = np.random.default_rng(seed)
        theta0, omega0, W0 = initialize_system(init_rng)

        for model_idx, model in enumerate(MODELS):
            model_rng = np.random.default_rng(seed + 100000 * (model_idx + 1))
            theta = theta0.copy()
            omega = omega0.copy()
            W = W0.copy()

            for t in range(TOTAL_STEPS):
                theta, W = run_simulation_step(model, theta, omega, W, t, model_rng)

                if np.isnan(W).any() or np.isnan(theta).any():
                    raise ValueError(f"NaN anomaly: {model}, seed={seed}, step={t}")
                if not np.allclose(W, W.T, atol=1e-12):
                    raise ValueError(f"Symmetry violation: {model}, step={t}")

                data_store[model]["entropy"][s_idx, t] = compute_structural_entropy(W)
                data_store[model]["ds"][s_idx, t] = compute_spectral_dimension(W)
                data_store[model]["r_param"][s_idx, t] = np.abs(np.mean(np.exp(1j * theta)))
                k_min, k_max = compute_curvature_proxy_bounds(W)
                data_store[model]["k_var"][s_idx, t] = np.var([k_min, k_max])

        print(f"Completed seed {s_idx + 1}/{N_SEEDS}")

    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    export_path = out_dir / ("rc_debug_ensemble_data.npz" if N_SEEDS <= 5 else "rc_production_ensemble_data.npz")
    np.savez(export_path, **{f"{m}_{k}": v for m, d in data_store.items() for k, v in d.items()})
    print(f"[SUCCESS] Data arrays stored to: {export_path}")

    for model in MODELS:
        print(
            model,
            "R_final=", np.mean(data_store[model]["r_param"][:, -1]),
            "ds_final=", np.mean(data_store[model]["ds"][:, -1]),
            "H_final=", np.mean(data_store[model]["entropy"][:, -1]),
        )


if __name__ == "__main__":
    main()
