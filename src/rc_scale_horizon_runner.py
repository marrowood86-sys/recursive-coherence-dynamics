#!/usr/bin/env python3
"""
RUN ID: RC-SCALE-HORIZON-002
Purpose: Dynamic N-independent vertical scale testing across N = [64, 128, 256].
"""

import numpy as np
import scipy.stats as stats
from pathlib import Path

SCALE_HORIZONS = [64, 128, 256]
N_SEEDS_SCALE = 30
TOTAL_STEPS_SCALE = 300
PERTURBATION_STEP_SCALE = 75

DT = 0.01
ALPHA = 0.15
LAMBDA = 0.05
T_NOISE = 0.02
D_DISS = 0.005
K_KURAMOTO = 0.50


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


def initialize_system(rng, N):
    theta = rng.uniform(-np.pi, np.pi, N)
    omega = rng.normal(0, 0.1, N)
    W = rng.uniform(0.01, 0.05, (N, N))
    W = 0.5 * (W + W.T)
    np.fill_diagonal(W, 0)
    return theta, omega, W


def run_simulation_step(model_type, theta, omega, W, step, rng, perturbation_step):
    N = W.shape[0]

    if step == perturbation_step:
        num_perturbed = max(4, int(N * 0.125))
        theta[0:num_perturbed] += np.pi

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
    scale_summary_data = {}

    print("Launching N-independent horizon test")

    for N in SCALE_HORIZONS:
        print(f"Processing N={N}")
        rc_ds_final_steps = []
        d_ds_final_steps = []

        for s_idx in range(N_SEEDS_SCALE):
            seed = 982145 + s_idx
            init_rng = np.random.default_rng(seed)
            theta0, omega0, W0 = initialize_system(init_rng, N)

            theta, omega, W = theta0.copy(), omega0.copy(), W0.copy()
            model_rng = np.random.default_rng(seed + 100000)
            for t in range(TOTAL_STEPS_SCALE):
                theta, W = run_simulation_step("RC", theta, omega, W, t, model_rng, PERTURBATION_STEP_SCALE)
            rc_ds_final_steps.append(compute_spectral_dimension(W))

            theta, omega, W = theta0.copy(), omega0.copy(), W0.copy()
            model_rng = np.random.default_rng(seed + 400000)
            for t in range(TOTAL_STEPS_SCALE):
                theta, W = run_simulation_step("CONTROL_D", theta, omega, W, t, model_rng, PERTURBATION_STEP_SCALE)
            d_ds_final_steps.append(compute_spectral_dimension(W))

        rc_ds_collection = np.array(rc_ds_final_steps)
        d_ds_collection = np.array(d_ds_final_steps)
        rc_mu, rc_sigma = np.mean(rc_ds_collection), np.std(rc_ds_collection)
        d_mu, d_sigma = np.mean(d_ds_collection), np.std(d_ds_collection)

        pass_rate = np.sum((rc_ds_collection >= 1.85) & (rc_ds_collection <= 2.15)) / N_SEEDS_SCALE * 100

        scale_summary_data[N] = {
            "raw_rc_ds": rc_ds_collection,
            "raw_d_ds": d_ds_collection,
        }

        print(f"N={N}: RC d_s={rc_mu:.3f} ± {rc_sigma:.2f}; Control D d_s={d_mu:.3f} ± {d_sigma:.2f}; pass={pass_rate:.1f}%")

        if pass_rate < 70.0:
            print(f"CRITICAL BREAK: Attractor drifted at N={N}")
            break

    out_dir = Path("data")
    out_dir.mkdir(exist_ok=True)
    export_scale_path = out_dir / "rc_scale_horizon_results.npz"
    np.savez(
        export_scale_path,
        horizons=np.array(list(scale_summary_data.keys())),
        **{f"N_{N}_raw_rc_ds": v["raw_rc_ds"] for N, v in scale_summary_data.items()},
        **{f"N_{N}_raw_d_ds": v["raw_d_ds"] for N, v in scale_summary_data.items()},
    )
    print(f"[SUCCESS] Scale horizon vectors saved to: {export_scale_path}")


if __name__ == "__main__":
    main()
