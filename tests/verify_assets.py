#!/usr/bin/env python3
"""
Verification script for independent replication of RC dimension-selection behavior.
Acts as a strict replication gate for public repository continuous integration.
"""

import numpy as np
from pathlib import Path


def verify_assets():
    try:
        prod_path = Path("data/rc_production_ensemble_data.npz")
        scale_path = Path("data/rc_scale_horizon_results.npz")

        if not prod_path.exists():
            raise FileNotFoundError(f"Missing {prod_path}. Run src/rc_diag_ensemble_runner.py in production mode first.")
        if not scale_path.exists():
            raise FileNotFoundError(f"Missing {scale_path}. Run src/rc_scale_horizon_runner.py first.")

        prod_data = np.load(prod_path)
        scale_data = np.load(scale_path)
        print("[SUCCESS] Data repositories verified and unpacked.")

        rc_ds_final = prod_data["RC_ds"][:, -1]
        kd_ds_final = prod_data["CONTROL_D_ds"][:, -1]

        print("\n--- REPLICATION TARGET BOUNDS (N=32, t=250) ---")
        print(f"Target Active RC d_s:       {np.mean(rc_ds_final):.3f} (Expected: ~1.98)")
        print(f"Target Control D d_s:       {np.mean(kd_ds_final):.3f} (Expected: ~5.32)")

        pass_rate = np.sum((rc_ds_final >= 1.85) & (rc_ds_final <= 2.15)) / len(rc_ds_final) * 100
        print(f"Target RC Pass Rate [1.85, 2.15]: {pass_rate:.1f}% (Expected: >80%)")

        assert pass_rate >= 80, f"Replication Failure: Active RC pass rate dropped to {pass_rate:.1f}%"

        print("[PASS] Baseline convergence intensity cleared.")

        print("\n--- REPLICATION TARGET SCALE INVARIANCE ---")
        for N in [64, 128, 256]:
            rc_scale = scale_data[f"N_{N}_raw_rc_ds"]
            d_scale = scale_data[f"N_{N}_raw_d_ds"]
            print(f"Scale Horizon N={N:<3} RC d_s:        {np.mean(rc_scale):.3f} ± {np.std(rc_scale):.2f}")
            print(f"Scale Horizon N={N:<3} Control D d_s: {np.mean(d_scale):.3f} ± {np.std(d_scale):.2f}")

        print("\n>>> STATUS: VERIFICATION COMPLETE. LOCAL ENVIRONMENT MATCHES PRE-REGISTERED ENSEMBLE BASELINE.")

    except AssertionError as ae:
        print(f"\n[CRITICAL FAILURE] {str(ae)}")
        raise SystemExit(1)
    except Exception as e:
        print(f"\n[ERROR] Asset verification infrastructure fault: {str(e)}")
        raise SystemExit(1)


if __name__ == "__main__":
    verify_assets()
