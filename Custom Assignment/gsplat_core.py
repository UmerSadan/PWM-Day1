"""
gsplat_core.py
==============
INSTRUCTOR REFERENCE SOLUTION for the 3D Gaussian Splatting assignment.
Function-for-function, this mirrors starter.py exactly -- it's what a
correct starter.py looks like once every TODO is filled in. Students
never see this file directly; they see starter.py and are graded by
check_solution.py.

See starter.py for the full conceptual walkthrough of each step; this
file keeps comments brief since the explanation lives there.
"""

import numpy as np


def quat_to_rotmat(q):
    """q: (N,4) unit quaternions in (w,x,y,z) order -> (N,3,3) rotation matrices."""
    q = np.asarray(q, dtype=np.float64)
    q = q / np.linalg.norm(q, axis=-1, keepdims=True)
    w, x, y, z = q[:, 0], q[:, 1], q[:, 2], q[:, 3]
    N = q.shape[0]
    R = np.empty((N, 3, 3))
    R[:, 0, 0] = 1 - 2 * (y * y + z * z)
    R[:, 0, 1] = 2 * (x * y - z * w)
    R[:, 0, 2] = 2 * (x * z + y * w)
    R[:, 1, 0] = 2 * (x * y + z * w)
    R[:, 1, 1] = 1 - 2 * (x * x + z * z)
    R[:, 1, 2] = 2 * (y * z - x * w)
    R[:, 2, 0] = 2 * (x * z - y * w)
    R[:, 2, 1] = 2 * (y * z + x * w)
    R[:, 2, 2] = 1 - 2 * (x * x + y * y)
    return R


def build_covariance_3d(scales, quats):
    """Sigma = R @ diag(scales)^2 @ R^T for each of the N Gaussians."""
    scales = np.asarray(scales, dtype=np.float64)
    R = quat_to_rotmat(quats)
    S = np.zeros((scales.shape[0], 3, 3))
    S[:, 0, 0] = scales[:, 0]
    S[:, 1, 1] = scales[:, 1]
    S[:, 2, 2] = scales[:, 2]
    M = R @ S
    Sigma = M @ np.transpose(M, (0, 2, 1))
    return Sigma


class Camera:
    """A minimal pinhole camera defined by a look-at pose."""

    def __init__(self, eye, target, up, fov_deg, width, height, near=0.05, far=100.0):
        self.eye = np.asarray(eye, dtype=np.float64)
        self.width, self.height = width, height
        self.near, self.far = near, far

        forward = np.asarray(target, dtype=np.float64) - self.eye
        forward /= np.linalg.norm(forward)
        right = np.cross(forward, up)
        right /= np.linalg.norm(right)
        true_up = np.cross(right, forward)

        self.R = np.stack([right, true_up, -forward], axis=0)  # camera looks down -z
        self.t = -self.R @ self.eye

        f = 1.0 / np.tan(np.radians(fov_deg) / 2.0)
        self.fx = f * height / 2.0
        self.fy = f * height / 2.0
        self.cx = width / 2.0
        self.cy = height / 2.0


def project_mean(cam, p_cam):
    """p_cam: (N,3) camera-space points -> (uv (N,2), depth (N,))."""
    depth = -p_cam[:, 2]
    u = cam.fx * (p_cam[:, 0] / depth) + cam.cx
    v = -cam.fy * (p_cam[:, 1] / depth) + cam.cy
    return np.stack([u, v], axis=-1), depth


def projection_jacobian(cam, p_cam):
    """(N,2,3) Jacobian of project_mean w.r.t. camera-space (x,y,z)."""
    x, y = p_cam[:, 0], p_cam[:, 1]
    zc = -p_cam[:, 2]
    N = p_cam.shape[0]
    J = np.zeros((N, 2, 3))
    J[:, 0, 0] = cam.fx / zc
    J[:, 0, 2] = cam.fx * x / (zc * zc)
    J[:, 1, 1] = -cam.fy / zc
    J[:, 1, 2] = -cam.fy * y / (zc * zc)
    return J


def project_gaussians(means, Sigma_w, cam, low_pass=0.3):
    """Project N world-space Gaussians through a camera."""
    p_cam = means @ cam.R.T + cam.t
    uv, depth = project_mean(cam, p_cam)

    Sigma_cam = np.einsum('ij,njk,lk->nil', cam.R, Sigma_w, cam.R)
    J = projection_jacobian(cam, p_cam)
    cov2d = np.einsum('nij,njk,nlk->nil', J, Sigma_cam, J)

    cov2d[:, 0, 0] += low_pass
    cov2d[:, 1, 1] += low_pass

    valid = depth > cam.near
    return {"uv": uv, "depth": depth, "cov2d": cov2d, "valid": valid}


def render(means, Sigma_w, colors, opacities, cam, low_pass=0.3, bg=(1.0, 1.0, 1.0)):
    """Depth-sorted, alpha-composited splat rasterizer."""
    H, W = cam.height, cam.width
    img = np.tile(np.array(bg, dtype=np.float64), (H, W, 1))

    proj = project_gaussians(means, Sigma_w, cam, low_pass=low_pass)
    uv, depth, cov2d, valid = proj["uv"], proj["depth"], proj["cov2d"], proj["valid"]

    order = np.argsort(-depth)  # farthest first (painter's algorithm)

    for i in order:
        if not valid[i]:
            continue
        cx, cy = uv[i]
        cov = cov2d[i]
        det = cov[0, 0] * cov[1, 1] - cov[0, 1] * cov[1, 0]
        if det <= 1e-12:
            continue
        inv = np.array([[cov[1, 1], -cov[0, 1]], [-cov[1, 0], cov[0, 0]]]) / det

        eigvals = np.linalg.eigvalsh(cov)
        radius = 3.0 * np.sqrt(max(eigvals.max(), 1e-6))
        radius = min(radius, 80)

        x0, x1 = int(max(cx - radius, 0)), int(min(cx + radius, W))
        y0, y1 = int(max(cy - radius, 0)), int(min(cy + radius, H))
        if x1 <= x0 or y1 <= y0:
            continue

        xs = np.arange(x0, x1) + 0.5
        ys = np.arange(y0, y1) + 0.5
        dx = xs[None, :] - cx
        dy = ys[:, None] - cy

        mdist2 = (inv[0, 0] * dx * dx + (inv[0, 1] + inv[1, 0]) * dx * dy
                  + inv[1, 1] * dy * dy)
        weight = np.exp(-0.5 * mdist2)

        alpha = np.clip(opacities[i] * weight, 0.0, 0.999)

        patch = img[y0:y1, x0:x1, :]
        color = np.asarray(colors[i])
        img[y0:y1, x0:x1, :] = color * alpha[..., None] + patch * (1.0 - alpha[..., None])

    return np.clip(img, 0.0, 1.0)
