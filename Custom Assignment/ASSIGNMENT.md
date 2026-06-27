# Assignment: 3D Gaussian Splatting from Scratch

**Course module:** Neural & Differentiable Rendering / Computer Graphics
**Estimated time:** 6–10 hours
**Language/tools:** Python 3, NumPy only (no PyTorch, no CUDA, no existing splatting library)
**Deliverables:** `starter.py` (completed), a 1–2 page writeup, and at least one rendered scene of your own design

---

## 1. Why this assignment exists

Most "intro to Gaussian Splatting" material jumps straight to running someone
else's CUDA rasterizer on a COLMAP dataset. That teaches you to run a
pipeline, not to understand one. This assignment strips 3D Gaussian
Splatting (3DGS) down to the one part that is genuinely teachable on a
laptop in an afternoon: **the forward renderer** — turning a static set of
3D Gaussians into a 2D image. You will not implement training,
backpropagation, or the tile-based CUDA rasterizer from the original paper.
You *will* implement the exact math that the training loop optimizes
through, which is the part that actually explains why the method works.

Background reading (you are not required to read the whole paper, but the
method section maps directly onto this assignment):

> Kerbl, B., Kopanas, G., Leimkühler, T., & Drettakis, G. (2023).
> *3D Gaussian Splatting for Real-Time Radiance Field Rendering.* ACM
> Transactions on Graphics (SIGGRAPH).

---

## 2. The representation

A scene is **not** a mesh and **not** a voxel grid. It is a set of $N$
3D Gaussians. Each one carries:

| Symbol | Shape | Meaning |
|---|---|---|
| $\mu_i$ | (3,) | center position in world space |
| $\Sigma_i$ | (3,3) | covariance — the Gaussian's size + orientation |
| $c_i$ | (3,) | RGB color |
| $\alpha_i$ | scalar | opacity |

Instead of storing $\Sigma_i$ directly, you store a scale vector $s_i \in
\mathbb{R}^3$ and a unit quaternion $q_i$, and build:

$$\Sigma_i = R_i S_i S_i^\top R_i^\top, \qquad S_i = \text{diag}(s_i), \quad R_i = \text{rot}(q_i)$$

**This is the first thing your writeup must explain**: why is this
parameterization (scale + rotation) preferred over directly storing the 6
independent entries of a symmetric matrix? (Hint: think about what
constraint a covariance matrix must satisfy, and what happens to that
constraint under unconstrained gradient descent on raw matrix entries.)

---

## 3. The pipeline you are implementing

For a given camera, rendering an image is five steps:

1. **World → camera space.** Transform every $\mu_i$ by the camera's
   rotation and translation.
2. **Perspective projection.** Project the camera-space mean to pixel
   coordinates with a pinhole model.
3. **Covariance projection.** This is the conceptual heart of the
   assignment. You cannot perspective-project a 3D ellipsoid into a 2D
   ellipse in closed form — perspective projection is nonlinear. The 3DGS
   paper (following the older EWA splatting line of work) approximates it
   *locally* with the first-order Taylor expansion (the Jacobian $J$) of
   the projection at each Gaussian's mean:
   $$\Sigma_i' = J_i \, \Sigma_i^{\text{cam}} \, J_i^\top$$
   This turns a 3D covariance into a 2D screen-space covariance — i.e. the
   shape of the ellipse you'll actually draw.
4. **Depth sort.** Gaussians must be composited in depth order for
   transparency to look correct (this is also exactly why the real
   paper's biggest engineering challenge is doing this sort fast on a
   GPU — you'll feel why once you profile your own pure-Python loop).
5. **Rasterize.** For every pixel a Gaussian's footprint touches, evaluate
   the 2D Gaussian density (via the Mahalanobis distance under $\Sigma_i'$),
   convert it to an alpha value, and alpha-composite with the "over"
   operator, back-to-front.

You are implementing exactly this in `starter.py`. Every function has a
docstring describing its contract and a derivation hint.

---

## 4. Tasks

### Part A — Geometry (40%)
- [ ] `quat_to_rotmat`
- [ ] `build_covariance_3d`
- [ ] `project_mean`
- [ ] `projection_jacobian`

### Part B — Splatting (40%)
- [ ] `project_gaussians`
- [ ] `render`

### Part C — Your own scene (10%)
Using `render_scene.py` as a template, build **your own** scene out of
Gaussians (not a re-skin of the planet-and-ring demo). Ideas: a low-poly
animal made of blobby Gaussians, a fake "reconstruction" of a photographed
object using a few hundred hand-placed anisotropic Gaussians, a simple
text logo extruded into 3D, a galaxy/starfield. Render it from at least 3
camera angles. Marked on: does it actually exercise anisotropic Gaussians
(non-uniform scale + non-identity rotation), and does your camera path
show real occlusion?

### Part D — Writeup (10%)
1-2 pages, answering:
1. The scale/quaternion parameterization question from Section 2.
2. Why does the renderer need the "low-pass filter" (`low_pass` added to
   the diagonal of `cov2d`)? What artifact would you see without it, and
   for which kind of Gaussian specifically?
3. Your rasterizer is $O(N \cdot \text{splat area})$ with a Python-level
   loop over Gaussians. The real paper's contribution is largely about
   making this fast (tile-based, GPU-parallel, custom backward pass).
   Describe in your own words what a tile-based rasterizer would do
   differently, and why naive depth-sorting *all* Gaussians globally (as
   you did) becomes a bottleneck at scale.
4. Pick one frame you rendered. Identify one Gaussian's contribution you
   can visually point to, and explain why it looks the way it does in
   terms of $\mu$, $\Sigma$, $c$, $\alpha$.

---

## 5. Grading & self-check

Run:

```bash
python check_solution.py
```

This checks each function in isolation (closed-form cases, a numerical
gradient check on your Jacobian, etc.) and then does one end-to-end
comparison: it renders a small fixed random scene with your code and
checks the PSNR against the reference render. You need **PSNR > 28 dB**
on that check to pass the end-to-end test. Passing it does not by itself
guarantee full marks — Parts C and D are graded separately by a human.

| Component | Weight |
|---|---|
| Part A (geometry functions, autograder) | 40% |
| Part B (splatting functions, autograder) | 40% |
| Part C (your own scene) | 10% |
| Part D (writeup) | 10% |

**Do not** import `gsplat_core` from your `starter.py` or otherwise call
the reference implementation — the autograder checks for this and it is
an academic-integrity violation, same as it would be to import a solution
key.

---

## 6. Common pitfalls

- **Forgetting to normalize the quaternion.** A raw quaternion parameter
  is not guaranteed unit length; if you skip normalization your rotation
  matrix won't be orthonormal and your covariance won't be physically
  valid (you'll usually notice this as warped, shearing-looking splats).
- **Sign error in the y-axis projection.** Image row 0 is the top of the
  image but a right-handed camera's "up" is usually $+y$ — if your
  rendered scene comes out vertically flipped, this is almost always why.
- **Depth sign confusion.** This starter's camera looks down its local
  $-z$ axis, so "depth" (distance in front of the camera) is $-z_{\text{cam}}$,
  not $z_{\text{cam}}$. Get this backwards and your near/far culling and
  your perspective divide will both be wrong, usually all at once.
- **Forgetting the low-pass filter** entirely, or adding it to the wrong
  matrix (it goes on `cov2d`, the *projected* 2D covariance, not the 3D one).
- **Not skipping near-singular `cov2d`.** A Gaussian viewed exactly
  edge-on can have a 2D covariance with a near-zero eigenvalue; invert it
  naively and you'll get `inf`/`NaN` pixels.

---

## 7. Stretch goals (ungraded, optional)

If you finish early and want to go further:

- **Differentiability.** Make every step NumPy-autograd or PyTorch
  compatible, and try optimizing the Gaussians' parameters to match a
  *target* rendered image (i.e. an extremely small-scale version of the
  real training loop), using just a handful of Gaussians and a single view.
- **Tile-based rasterization.** Bucket Gaussians into screen-space tiles
  and only test the Gaussians relevant to each tile, instead of one global
  Python loop. Profile the speedup.
- **Real data.** Install [gsplat](https://github.com/nerfstudio-project/gsplat)
  or try [nerfstudio](https://docs.nerf.studio/), run COLMAP on a short
  phone video of an object, and train a real splat scene. Compare what
  you now understand about the renderer to what the library is actually
  doing internally.
- **Spherical harmonics color.** The real paper stores view-dependent
  color via low-order spherical harmonics per Gaussian instead of a flat
  RGB. Add a degree-1 SH color model and re-render the same scene from
  several angles to see the view-dependent shading effect.

---

## Appendix: file manifest

```
starter.py              <- YOU EDIT THIS. All TODOs live here.
check_solution.py       <- autograder, run it yourself before submitting
render_scene.py         <- example scene builder + multi-view render driver
                            (reference implementation; read for Part C, don't copy)
gsplat_core.py           <- reference implementation (do not import from your code)
reference_outputs/      <- fixture used by check_solution.py
renders/                <- example output from the reference implementation
gaussian_splat_viewer.html <- bonus: interactive 3D viewer of the demo scene
```
