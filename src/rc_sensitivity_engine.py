#!/usr/bin/env python3
"""
RUN ID: RC-SENSITIVITY-001
Purpose: Ablation and measurement-dependence profiling for Active RC.
"""

import numpy as np
import scipy.stats as stats
from pathlib import Path

N = 128
N_SEEDS_SENS = 30
TOTAL_STEPS_SENS = 300
PERTURBATION_STEP_SENS = 75

DT = 0.01
ALPHA = 0.15
LAMBDA = 0.05
T_NOISE = 0.02
D_DISS = 0.005


def compute_spectral_dimension_dynamic(W, percentile_thresh, max_tau=12):
    N_local = W.shape[0]
    w_nonzero = W[W > 0]
    if len(w_nonzero) == 0:
        return 0.0
    thresh = np.percentile(w_nonzero, percentile_thresh)
    W_eff = np.where(W >= thresh, W, 0.0)

    deg = np.sum(W_eff, axis=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        D_inv = np.diag(np.where(deg > 0, 1.0 / deg, 0.0))

    T = np.dot(D_inv, W_eff)
    T_pow = np.eye(N_local)
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


def initialize_system(rng, N_local):
    theta = rng.uniform(-np.pi, np.pi, N_local)
    omega = rng.normal(0, 0.1, N_local)
    W = rng.uniform(0.01, 0.05, (N_local, N_local))
    W = 0.5 * (W + W.T)
    np.fill_diagonal(W, 0)
    return theta, omega, W


def run_simulation_step_ablat(variant, theta, omega, W, step, rng, perturb_frac):
    N_local = W.shape[0]

    if step == PERTURBATION_STEP_SENS:
        num_perturbed = max(2, int(N_local * perturb_frac))
        theta[0:num_perturbed] += np.pi

    theta_diff = theta[np.newaxis, :] - theta[:, np.newaxis]
    rho = np.cos(theta_diff)

    if variant == "RC-full":
        H_row = np.zeros_like(W)
        for i in range(N_local):
            row = W[i]
            p = row / (np.sum(row) + 1e-12)
            H_row[i, :] = -np.sum(p * np.log(p + 1e-12))
        W_next = W + DT * ALPHA * (rho - LAMBDA * H_row)
        W_next = np.clip(W_next, 0.0, 1.0)

    elif variant == "RC-no-entropy":
        W_next = np.clip(W + DT * ALPHA * rho, 0.0, 1.0)

    elif variant == "RC-no-adaptation":
        W_next = W.copy()

    else:
        raise ValueError(f"Unknown variant: {variant}")

    W_next = 0.5 * (W_next + W_next.T)
    np.fill_diagonal(W_next, 0)

    d_theta = omega + (1.0 / N_local) * np.sum(W_next * np.sin(theta_diff), axis=1)
    if variant != "RC-no-adaptation":
        d_theta -= D_DISS * theta

    theta_next = theta + DT * d_theta + np.sqrt(DT) * rng.normal(0, T_NOISE, N_local)
    theta_next = np.mod(theta_next + np.pi, 2 * np.pi) - np.pi
    return theta_next, W_next


def main():
    ablation_modes = ["RC-full", "RC-no-entropy", "RC-no-adaptation"]
    threshold_sweeps = [50, 60, 75, 90]
    perturb_sweeps = [0.05, 0.125, 0.25]
    results_log = {}

    print("Running sensitivity and ablation matrix")

    for seed_idx in range(N_SEEDS_SENS):
        seed = 883102 + seed_idx
        init_rng = np.random.default_rng(seed)
        theta0, omega0, W0 = initialize_system(init_rng, N)

        for mode in ablation_modes:
            theta, omega, W = theta0.copy(), omega0.copy(), W0.copy()
            model_rng = np.random.default_rng(seed + 20000)

            for t in range(TOTAL_STEPS_SENS):
                theta, W = run_simulation_step_ablat(mode, theta, omega, W, t, model_rng, 0.125)

            d_s_75 = compute_spectral_dimension_dynamic(W, 75)
            results_log.setdefault(mode, []).append(d_s_75)

            if mode == "RC-full":
                for thresh in threshold_sweeps:
                    if thresh != 75:
                        d_s_v = compute_spectral_dimension_dynamic(W, thresh)
                        results_log.setdefault(f"RC-thresh-{thresh}", []).append(d_s_v)

        for p_frac in perturb_sweeps:
            if p_frac != 0.125:
                theta, omega, W = theta0.copy(), omega0.copy(), W0.copy()
                model_rng = np.random.default_rng(seed + 20000)

                for t in range(TOTAL_STEPS_SENS):
                    theta, W = run_simulation_step_ablat("RC-full", theta, omega, W, t, model_rng, p_frac)

                d_s_p = compute_spectral_dimension_dynamic(W, 75)
                results_log.setdefault(f"RC-perturb-{p_frac*100}%", []).append(d_s_p)

    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)

    print("\nSensitivity Results:")
    for key, values in results_log.items():
        arr = np.array(values)
        print(f"{key}: {np.mean(arr):.3f} ± {np.std(arr):.2f}")

    np.savez(out_dir / "rc_sensitivity_results.npz", **{k: np.array(v) for k, v in results_log.items()})
    print("[SUCCESS] Sensitivity results saved to data/rc_sensitivity_results.npz")


if __name__ == "__main__":
    main()
