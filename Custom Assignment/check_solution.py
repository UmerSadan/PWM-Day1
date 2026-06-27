"""
check_solution.py
==================
Self-check / autograder. Run this after filling in starter.py:

    python check_solution.py

It tests your functions against the reference implementation on a small
synthetic scene and on a tiny image-quality check (PSNR against the
reference render). It does NOT just diff against gsplat_core.py (that
would be too easy to cheat) -- it rebuilds equivalent checks from
first-principles values where it can, and uses the reference renderer
only for the final end-to-end image comparison.
"""

import numpy as np
import sys

PASS = "PASS"
FAIL = "FAIL"


def section(name):
    print(f"\n--- {name} ---")


def check(name, ok):
    print(f"[{PASS if ok else FAIL}] {name}")
    return ok


def main():
    try:
        import starter as S
    except Exception as e:
        print(f"Could not import starter.py: {e}")
        sys.exit(1)

    all_ok = True

    # ---- quat_to_rotmat ----
    section("quat_to_rotmat")
    try:
        q_identity = np.array([[1.0, 0.0, 0.0, 0.0]])
        R = S.quat_to_rotmat(q_identity)
        ok = np.allclose(R[0], np.eye(3), atol=1e-6)
        all_ok &= check("identity quaternion -> identity matrix", ok)

        # 90 degree rotation about z: q = (cos45, 0,0,sin45)
        half = np.radians(90) / 2
        q_z90 = np.array([[np.cos(half), 0.0, 0.0, np.sin(half)]])
        R = S.quat_to_rotmat(q_z90)
        v = R[0] @ np.array([1.0, 0.0, 0.0])
        ok = np.allclose(v, [0.0, 1.0, 0.0], atol=1e-6)
        all_ok &= check("90deg about z rotates +x -> +y", ok)

        # orthonormality
        ok = np.allclose(R[0] @ R[0].T, np.eye(3), atol=1e-6)
        all_ok &= check("rotation matrix is orthonormal", ok)
    except Exception as e:
        all_ok &= check(f"quat_to_rotmat raised {e}", False)

    # ---- build_covariance_3d ----
    section("build_covariance_3d")
    try:
        scales = np.array([[1.0, 2.0, 3.0]])
        quats = np.array([[1.0, 0.0, 0.0, 0.0]])
        Sigma = S.build_covariance_3d(scales, quats)
        expected = np.diag([1.0, 4.0, 9.0])
        ok = np.allclose(Sigma[0], expected, atol=1e-6)
        all_ok &= check("axis-aligned scale -> diagonal covariance = scale^2", ok)

        # symmetry + PSD for a random rotated case
        rng = np.random.default_rng(0)
        scales2 = rng.uniform(0.1, 2.0, (5, 3))
        quats2 = rng.normal(size=(5, 4))
        Sigma2 = S.build_covariance_3d(scales2, quats2)
        sym_ok = np.allclose(Sigma2, np.transpose(Sigma2, (0, 2, 1)), atol=1e-6)
        eigmin = np.array([np.linalg.eigvalsh(s).min() for s in Sigma2])
        psd_ok = np.all(eigmin > -1e-8)
        all_ok &= check("covariance is symmetric", sym_ok)
        all_ok &= check("covariance is positive semi-definite", psd_ok)
    except Exception as e:
        all_ok &= check(f"build_covariance_3d raised {e}", False)

    # ---- project_mean ----
    section("project_mean")
    try:
        cam = S.Camera(eye=(0, 0, 5), target=(0, 0, 0), up=(0, 1, 0),
                       fov_deg=90, width=100, height=100)
        # A point on the camera's forward axis should land at the
        # principal point (cx, cy).
        p_cam = np.array([[0.0, 0.0, -2.0]])  # 2 units in front
        uv, depth = S.project_mean(cam, p_cam)
        ok = np.allclose(uv[0], [cam.cx, cam.cy], atol=1e-4) and np.isclose(depth[0], 2.0)
        all_ok &= check("on-axis point projects to principal point at correct depth", ok)
    except Exception as e:
        all_ok &= check(f"project_mean raised {e}", False)

    # ---- projection_jacobian (numerical check) ----
    section("projection_jacobian (numerical gradient check)")
    try:
        cam = S.Camera(eye=(0, 0, 5), target=(0, 0, 0), up=(0, 1, 0),
                       fov_deg=70, width=128, height=128)
        p0 = np.array([[0.3, -0.2, -3.0]])
        J = S.projection_jacobian(cam, p0)[0]

        eps = 1e-5
        J_num = np.zeros((2, 3))
        for k in range(3):
            dp = np.zeros((1, 3)); dp[0, k] = eps
            uv_plus, _ = S.project_mean(cam, p0 + dp)
            uv_minus, _ = S.project_mean(cam, p0 - dp)
            J_num[:, k] = (uv_plus[0] - uv_minus[0]) / (2 * eps)

        ok = np.allclose(J, J_num, atol=1e-2)
        all_ok &= check("analytic Jacobian matches numerical gradient", ok)
    except Exception as e:
        all_ok &= check(f"projection_jacobian raised {e}", False)

    # ---- end to end render vs reference image ----
    section("end-to-end render (PSNR vs reference)")
    try:
        ref = np.load("reference_outputs/reference_frame.npz")
        means, scales, quats = ref["means"], ref["scales"], ref["quats"]
        colors, opacities = ref["colors"], ref["opacities"]
        ref_img = ref["image"]

        cam = S.Camera(eye=tuple(ref["cam_eye"]), target=(0, 0, 0), up=(0, 1, 0),
                        fov_deg=float(ref["fov_deg"]), width=int(ref["W"]), height=int(ref["H"]))
        Sigma_w = S.build_covariance_3d(scales, quats)
        img = S.render(means, Sigma_w, colors, opacities, cam, bg=(0.05, 0.06, 0.09))

        mse = np.mean((img - ref_img) ** 2)
        psnr = 999 if mse < 1e-12 else 10 * np.log10(1.0 / mse)
        ok = psnr > 28.0  # generous threshold -- small numerical differences are fine
        print(f"      PSNR = {psnr:.2f} dB (need > 28 dB)")
        all_ok &= check("rendered image matches reference render", ok)
    except FileNotFoundError:
        print("      (reference_outputs/reference_frame.npz not found -- run "
              "make_reference.py first, or skip this check in early development)")
    except Exception as e:
        all_ok &= check(f"render raised {e}", False)

    section("RESULT")
    print("ALL CHECKS PASSED" if all_ok else "SOME CHECKS FAILED -- see above")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
