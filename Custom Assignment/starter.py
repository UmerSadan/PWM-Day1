"""
starter.py
==========
CS Assignment: 3D Gaussian Splatting from Scratch
---------------------------------------------------
Fill in every function marked TODO. Do not change function signatures.

You are implementing the forward renderer from:
  Kerbl, Kopanas, Leimkuehler, Drettakis,
  "3D Gaussian Splatting for Real-Time Radiance Field Rendering", SIGGRAPH 2023.

A scene is a set of N anisotropic 3D Gaussians, each with:
  - a mean position  mu_i  in R^3
  - a covariance     Sigma_i  in R^{3x3}, built from a scale vector and a
    rotation quaternion (so it's always symmetric positive semi-definite)
  - an RGB color      c_i
  - an opacity        alpha_i  in [0, 1]

To render an image from a camera you must:
  1. Transform each mean into camera space.
  2. Project it to pixel coordinates with a pinhole camera model.
  3. Project its 3D covariance into a 2D *screen-space* covariance using
     the local affine (Jacobian) approximation of the projection.
  4. Sort Gaussians by depth.
  5. Rasterize: for every pixel under a Gaussian's footprint, evaluate the
     2D Gaussian density there, turn it into an alpha value, and
     alpha-composite it with whatever is already in the image buffer
     (back-to-front, the standard "over" operator).

Run `python check_solution.py` to test your implementation against
known-good outputs once you're done.
"""

import numpy as np


def quat_to_rotmat(q):
    """q: (N,4) unit quaternions in (w,x,y,z) order -> (N,3,3) rotation matrices.

    TODO: implement the standard quaternion-to-rotation-matrix formula.
    Remember to normalize q first (a Gaussian's raw quaternion parameter
    is not guaranteed to be unit-length during optimization in the real
    paper -- always normalize before use).
    """
    raise NotImplementedError


def build_covariance_3d(scales, quats):
    """scales: (N,3) per-axis scale.  quats: (N,4).

    TODO: build Sigma = R @ diag(scales) @ diag(scales)^T @ R^T for each
    of the N Gaussians, returning an (N,3,3) array.

    Question to answer in your writeup: why is it important that we
    parameterize the covariance this way (scale + rotation) rather than
    directly optimizing the 6 independent entries of a symmetric 3x3
    matrix?
    """
    raise NotImplementedError


class Camera:
    """A minimal pinhole camera defined by a look-at pose. Already implemented
    for you -- read it carefully, you will need cam.R, cam.t, cam.fx, cam.fy
    in the functions below."""

    def __init__(self, eye, target, up, fov_deg, width, height, near=0.05, far=100.0):
        self.eye = np.asarray(eye, dtype=np.float64)
        self.width, self.height = width, height
        self.near, self.far = near, far

        forward = np.asarray(target, dtype=np.float64) - self.eye
        forward /= np.linalg.norm(forward)
        right = np.cross(forward, up)
        right /= np.linalg.norm(right)
        true_up = np.cross(right, forward)

        self.R = np.stack([right, true_up, -forward], axis=0)
        self.t = -self.R @ self.eye

        f = 1.0 / np.tan(np.radians(fov_deg) / 2.0)
        self.fx = f * height / 2.0
        self.fy = f * height / 2.0
        self.cx = width / 2.0
        self.cy = height / 2.0


def project_mean(cam, p_cam):
    """p_cam: (N,3) camera-space points.

    TODO: return (uv, depth) where uv is (N,2) pixel coordinates and depth
    is (N,) the distance in front of the camera (positive = in front).
    Camera looks down its local -z axis, so depth = -p_cam[:, 2].

    Pinhole model:
        u = fx * x / depth + cx
        v = -fy * y / depth + cy        (negative: image row 0 is the top)
    """
    raise NotImplementedError


def projection_jacobian(cam, p_cam):
    """TODO: return the (N,2,3) Jacobian of the projection in project_mean
    with respect to camera-space (x, y, z), evaluated at each point.

    This is the first-order (EWA splatting) approximation that lets us
    turn a 3D covariance into a 2D one with a single matrix sandwich:
        Sigma_2d = J @ Sigma_camera @ J^T

    Hint: differentiate u(x,y,z) and v(x,y,z) from project_mean. Let
    zc = -z (the depth). You should get:
        du/dx = fx/zc      du/dy = 0         du/dz = fx*x/zc^2
        dv/dx = 0          dv/dy = -fy/zc    dv/dz = -fy*y/zc^2
    """
    raise NotImplementedError


def project_gaussians(means, Sigma_w, cam, low_pass=0.3):
    """TODO: full per-Gaussian projection pipeline. For each of the N
    Gaussians:
      1. world_to_camera: p_cam = means @ cam.R.T + cam.t
      2. uv, depth = project_mean(cam, p_cam)
      3. Sigma_cam = cam.R @ Sigma_w @ cam.R.T   (rotate world cov into camera space)
      4. J = projection_jacobian(cam, p_cam)
      5. cov2d = J @ Sigma_cam @ J.T
      6. add `low_pass` to the diagonal of cov2d (this is the "minimum
         splat size" trick from the paper -- explain in your writeup why
         a tiny/degenerate Gaussian without this would disappear or alias)

    Return a dict: {"uv": (N,2), "depth": (N,), "cov2d": (N,2,2),
                    "valid": (N,) bool mask where depth > cam.near}
    """
    raise NotImplementedError


def render(means, Sigma_w, colors, opacities, cam, low_pass=0.3, bg=(1.0, 1.0, 1.0)):
    """TODO: the rasterizer.

    1. Call project_gaussians to get uv, depth, cov2d, valid.
    2. Depth-sort indices farthest-to-nearest (painter's algorithm).
    3. For each Gaussian (in that order):
         a. Invert its 2x2 cov2d. Skip if near-singular (det too small).
         b. Compute a splat radius (try 3 * sqrt(largest eigenvalue of cov2d))
            and the pixel bounding box around its projected center, clipped
            to the image.
         c. For every pixel (x,y) in that box, compute the Mahalanobis
            distance under cov2d^-1 and turn it into a Gaussian weight
            exp(-0.5 * mdist2).
         d. alpha = clip(opacity * weight, 0, 0.999)
         e. Composite: pixel = color*alpha + pixel*(1-alpha)
    4. Return the (H,W,3) image, values clipped to [0,1].

    This is the heart of the assignment -- everything before this function
    was just geometry; THIS function is "splatting."
    """
    raise NotImplementedError
