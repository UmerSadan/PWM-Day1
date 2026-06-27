"""
render_scene.py
================
Builds a demo scene out of thousands of 3D Gaussians (no meshes, no
textures -- this is the whole point of Gaussian Splatting: the *only*
3D representation is a cloud of little oriented, colored, fuzzy
ellipsoids) and renders it from several camera angles using
gsplat_core.render().

Scene: a "gas giant" sphere + a tilted ring system (a tiny Saturn),
because it cleanly demonstrates:
  - smooth shaded-looking surfaces built from overlapping soft Gaussians
  - anisotropic Gaussians (the ring particles are flattened disks, not
    spheres -- you can see the splat shape directly in the ring)
  - depth sorting / occlusion (the ring passes both behind and in front
    of the sphere depending on viewing angle)
"""

import numpy as np
import os
from PIL import Image

from gsplat_core import build_covariance_3d, Camera, render

rng = np.random.default_rng(7)


def make_planet(n=9000, radius=1.0):
    """Fill a sphere's surface (with some radial jitter / interior fill)
    with small isotropic-ish Gaussians, colored like a banded gas giant."""
    # Sample uniformly on a sphere, then push a fraction of points slightly
    # inward so the surface reads as solid/filled rather than a thin shell.
    phi = rng.uniform(0, 2 * np.pi, n)
    cos_theta = rng.uniform(-1, 1, n)
    theta = np.arccos(cos_theta)
    r = radius * (1.0 - rng.uniform(0, 0.08, n))  # slight shell thickness

    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.cos(phi) * 0  # placeholder, fixed below
    y = r * np.cos(theta)
    z = r * np.sin(theta) * np.sin(phi)
    means = np.stack([x, y, z], axis=1)

    # Banded coloring by latitude (cos_theta), like Jupiter/Saturn bands,
    # plus a touch of longitude-based noise so bands aren't perfectly flat.
    band = np.sin(cos_theta * 9.0 + 0.6 * np.sin(phi * 3.0)) * 0.5 + 0.5
    base_a = np.array([0.92, 0.78, 0.55])   # warm cream band
    base_b = np.array([0.65, 0.45, 0.30])   # darker terracotta band
    colors = base_a[None, :] * band[:, None] + base_b[None, :] * (1 - band[:, None])
    colors += rng.normal(0, 0.02, colors.shape)
    colors = np.clip(colors, 0, 1)

    scales = np.full((n, 3), 0.045) * (1.0 + rng.uniform(-0.2, 0.2, (n, 1)))
    quats = np.tile(np.array([1.0, 0, 0, 0]), (n, 1))  # isotropic -> rotation irrelevant
    opacities = np.full(n, 0.9)

    return means, scales, quats, colors, opacities


def make_ring(n=6000, r_in=1.5, r_out=2.6, tilt_deg=22):
    """A flattened disk of small flattened (anisotropic) Gaussians."""
    ang = rng.uniform(0, 2 * np.pi, n)
    rad = np.sqrt(rng.uniform(r_in ** 2, r_out ** 2, n))  # uniform area density
    x = rad * np.cos(ang)
    z = rad * np.sin(ang)
    y = rng.normal(0, 0.01, n)  # paper-thin ring
    means = np.stack([x, y, z], axis=1)

    # Tilt the whole ring about the x-axis.
    t = np.radians(tilt_deg)
    Rt = np.array([[1, 0, 0], [0, np.cos(t), -np.sin(t)], [0, np.sin(t), np.cos(t)]])
    means = means @ Rt.T

    # Color: dusty gold, with subtle radial banding (Cassini-division-ish gaps).
    gap = 0.5 + 0.5 * np.sin(rad * 9.0)
    base = np.array([0.80, 0.72, 0.55])
    colors = base[None, :] * (0.6 + 0.4 * gap[:, None])
    colors = np.clip(colors + rng.normal(0, 0.015, colors.shape), 0, 1)

    # Anisotropic, flattened "pancake" Gaussians: large in-plane, tiny
    # out-of-plane scale -- this is what makes them look like thin ring
    # particles instead of fuzzy balls. Each ring particle gets a random
    # spin about y so the flattening direction matches the ring plane
    # after the global tilt (since means already include the tilt, we
    # bake the same tilt rotation into every particle's orientation).
    scales = np.stack([
        rng.uniform(0.02, 0.05, n),
        np.full(n, 0.004),
        rng.uniform(0.02, 0.05, n),
    ], axis=1)

    # quaternion for rotation Rt about x-axis: w = cos(t/2), x = sin(t/2)
    half = t / 2.0
    quats = np.tile(np.array([np.cos(half), np.sin(half), 0.0, 0.0]), (n, 1))

    opacities = np.full(n, 0.85)
    return means, scales, quats, colors, opacities


def assemble_scene():
    m1, s1, q1, c1, o1 = make_planet()
    m2, s2, q2, c2, o2 = make_ring()
    means = np.concatenate([m1, m2], axis=0)
    scales = np.concatenate([s1, s2], axis=0)
    quats = np.concatenate([q1, q2], axis=0)
    colors = np.concatenate([c1, c2], axis=0)
    opacities = np.concatenate([o1, o2], axis=0)
    return means, scales, quats, colors, opacities


def to_uint8(img):
    return (img * 255).astype(np.uint8)


def main():
    out_dir = "renders"
    os.makedirs(out_dir, exist_ok=True)

    means, scales, quats, colors, opacities = assemble_scene()
    print(f"Scene: {means.shape[0]} 3D Gaussians")

    Sigma_w = build_covariance_3d(scales, quats)

    W, H = 360, 360
    n_frames = 8
    frames = []
    for i in range(n_frames):
        az = 2 * np.pi * i / n_frames
        eye = np.array([3.6 * np.cos(az), 1.6, 3.6 * np.sin(az)])
        cam = Camera(eye=eye, target=(0, 0, 0), up=(0, 1, 0),
                     fov_deg=40, width=W, height=H)
        img = render(means, Sigma_w, colors, opacities, cam,
                     bg=(0.05, 0.06, 0.09))
        frame = Image.fromarray(to_uint8(img))
        frame.save(f"{out_dir}/frame_{i:02d}.png")
        frames.append(frame)
        print(f"  rendered frame {i+1}/{n_frames} (azimuth {np.degrees(az):.0f}deg)")

    # animated turntable GIF
    frames[0].save(f"{out_dir}/turntable.gif", save_all=True,
                    append_images=frames[1:], duration=160, loop=0)

    # contact sheet (4x2 grid) for a single-image preview
    cols, rows = 4, 2
    sheet = Image.new("RGB", (W * cols, H * rows), (10, 10, 12))
    for i, f in enumerate(frames):
        x = (i % cols) * W
        y = (i // cols) * H
        sheet.paste(f, (x, y))
    sheet.save(f"{out_dir}/contact_sheet.png")

    # also export the raw point data for the interactive viewer
    np.savez(f"{out_dir}/scene_points.npz", means=means, colors=colors,
              scales=scales, opacities=opacities)

    print("Done. Outputs in ./renders/")


if __name__ == "__main__":
    main()
