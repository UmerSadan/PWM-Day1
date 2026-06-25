"""
Gaussian Splatting Visualizer
==============================
A real-time interactive demo of Gaussian Splatting concepts:
- 3D Gaussian primitives projected to 2D screen space
- Alpha-blended compositing (front-to-back depth sorting)
- Covariance-based elliptical splats with color & opacity
- Animated camera orbit + interactive mouse drag

Dependencies: pip install numpy matplotlib scipy
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Ellipse
from matplotlib.animation import FuncAnimation
from scipy.spatial.transform import Rotation
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
#  SCENE DEFINITION  –  each Gaussian: [x, y, z, r, g, b, opacity, sx, sy, sz]
# ─────────────────────────────────────────────────────────────

np.random.seed(42)

def make_scene():
    gaussians = []

    # ── Sphere of colourful gaussians ──
    n = 220
    phi   = np.random.uniform(0, 2*np.pi, n)
    theta = np.random.uniform(0,   np.pi, n)
    r     = np.random.uniform(1.5,  2.5, n)
    x = r * np.sin(theta) * np.cos(phi)
    y = r * np.sin(theta) * np.sin(phi)
    z = r * np.cos(theta)
    for i in range(n):
        hue  = (phi[i] / (2*np.pi))
        col  = plt.cm.hsv(hue)[:3]
        sx   = np.random.uniform(0.08, 0.28)
        sy   = np.random.uniform(0.08, 0.28)
        sz   = np.random.uniform(0.08, 0.28)
        opa  = np.random.uniform(0.55, 0.95)
        gaussians.append([x[i], y[i], z[i], col[0], col[1], col[2], opa, sx, sy, sz])

    # ── Ground plane ──
    for _ in range(80):
        gx = np.random.uniform(-3, 3)
        gz = np.random.uniform(-3, 3)
        gy = -2.6 + np.random.uniform(-0.1, 0.1)
        col = (0.15, 0.55 + np.random.uniform(0, 0.2), 0.25)
        gaussians.append([gx, gy, gz, col[0], col[1], col[2],
                          0.7, 0.4, 0.05, 0.4])

    # ── Central bright core ──
    for _ in range(30):
        cx = np.random.uniform(-0.3, 0.3)
        cy = np.random.uniform(-0.3, 0.3)
        cz = np.random.uniform(-0.3, 0.3)
        col = (1.0, 0.95, 0.7)
        gaussians.append([cx, cy, cz, col[0], col[1], col[2],
                          0.6, 0.12, 0.12, 0.12])

    return np.array(gaussians, dtype=np.float32)

GAUSSIANS = make_scene()   # shape (N, 10)

# ─────────────────────────────────────────────────────────────
#  PROJECTION HELPERS
# ─────────────────────────────────────────────────────────────

def rotation_matrix(yaw, pitch):
    """Camera rotation: yaw around Y, pitch around X."""
    Ry = np.array([[np.cos(yaw), 0, np.sin(yaw)],
                   [0,           1, 0           ],
                   [-np.sin(yaw),0, np.cos(yaw) ]])
    Rx = np.array([[1, 0,            0           ],
                   [0, np.cos(pitch),-np.sin(pitch)],
                   [0, np.sin(pitch), np.cos(pitch)]])
    return Rx @ Ry

def project_gaussians(gaussians, cam_pos, R, focal=3.0):
    """
    Project 3D Gaussians → 2D screen ellipses.
    Returns list of dicts with screen info, sorted back-to-front.
    """
    results = []
    for g in gaussians:
        wx, wy, wz = g[0], g[1], g[2]
        r, gr, b   = g[3], g[4], g[5]
        opa        = g[6]
        sx, sy, sz = g[7], g[8], g[9]

        # Camera-space position
        world_pt = np.array([wx, wy, wz]) - cam_pos
        cam_pt   = R @ world_pt
        cx, cy, cz = cam_pt

        if cz <= 0.1:          # behind camera
            continue

        # Perspective divide
        sx2d = (focal * cx / cz)
        sy2d = (focal * cy / cz)

        # Approximate 2D covariance (axis-aligned for simplicity)
        scale = focal / cz
        ex = np.sqrt(sx**2 * (R[0,0]**2) + sy**2 * (R[0,1]**2) + sz**2 * (R[0,2]**2)) * scale
        ey = np.sqrt(sx**2 * (R[1,0]**2) + sy**2 * (R[1,1]**2) + sz**2 * (R[1,2]**2)) * scale

        ex = max(ex, 0.01)
        ey = max(ey, 0.01)

        # Compute angle from projected covariance
        angle = np.degrees(np.arctan2(
            R[1,0]*sx + R[1,1]*sy,
            R[0,0]*sx + R[0,1]*sy
        ))

        results.append({
            'sx': sx2d, 'sy': sy2d,
            'depth': cz,
            'ex': ex, 'ey': ey,
            'angle': angle,
            'color': (r, gr, b),
            'alpha': float(opa),
        })

    # Depth sort: back → front (painter's algorithm)
    results.sort(key=lambda d: -d['depth'])
    return results

# ─────────────────────────────────────────────────────────────
#  MATPLOTLIB FIGURE SETUP
# ─────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(11, 8), facecolor='#050812')
fig.patch.set_facecolor('#050812')

# Main render pane
ax = fig.add_axes([0.0, 0.15, 0.72, 0.85])
ax.set_facecolor('#050812')
ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-1.8, 1.8)
ax.set_aspect('equal')
ax.axis('off')

# Side info panel
ax_info = fig.add_axes([0.73, 0.0, 0.27, 1.0])
ax_info.set_facecolor('#0a0f1e')
ax_info.axis('off')

# Bottom depth chart
ax_depth = fig.add_axes([0.0, 0.0, 0.72, 0.13])
ax_depth.set_facecolor('#080d1a')
ax_depth.tick_params(colors='#4a90d9')
for sp in ax_depth.spines.values():
    sp.set_color('#1a2a4a')

fig.suptitle('Gaussian Splatting — Real-Time 3D Scene Renderer',
             color='#7ec8f7', fontsize=13, fontweight='bold', y=0.995,
             fontfamily='monospace')

# ─────────────────────────────────────────────────────────────
#  SIDE PANEL  –  static legend & info
# ─────────────────────────────────────────────────────────────

def draw_info_panel():
    ax_info.clear()
    ax_info.set_facecolor('#0a0f1e')
    ax_info.axis('off')

    lines = [
        ("GAUSSIAN SPLATTING", '#7ec8f7', 12, 'bold'),
        ("", '#ffffff', 9, 'normal'),
        ("How it works:", '#a0c8f0', 10, 'bold'),
        ("① 3D Gaussians defined", '#c8e0ff', 8.5, 'normal'),
        ("   by position, colour,", '#c8e0ff', 8.5, 'normal'),
        ("   opacity & covariance.", '#c8e0ff', 8.5, 'normal'),
        ("", '#ffffff', 8, 'normal'),
        ("② Project to screen via", '#c8e0ff', 8.5, 'normal'),
        ("   perspective camera.", '#c8e0ff', 8.5, 'normal'),
        ("", '#ffffff', 8, 'normal'),
        ("③ Sort back→front and", '#c8e0ff', 8.5, 'normal'),
        ("   alpha-composite.", '#c8e0ff', 8.5, 'normal'),
        ("", '#ffffff', 8, 'normal'),
        ("Scene Contents:", '#a0c8f0', 10, 'bold'),
        (f"  Splats : {len(GAUSSIANS)}", '#e0f0ff', 8.5, 'normal'),
        ("  Shell  : 220 splats", '#e0f0ff', 8.5, 'normal'),
        ("  Ground : 80  splats", '#e0f0ff', 8.5, 'normal'),
        ("  Core   : 30  splats", '#e0f0ff', 8.5, 'normal'),
        ("", '#ffffff', 8, 'normal'),
        ("Controls:", '#a0c8f0', 10, 'bold'),
        ("  Drag mouse to orbit", '#e0f0ff', 8.5, 'normal'),
        ("  Auto-orbit animates", '#e0f0ff', 8.5, 'normal'),
        ("", '#ffffff', 8, 'normal'),
        ("Tech Stack:", '#a0c8f0', 10, 'bold'),
        ("  NumPy · Matplotlib", '#e0f0ff', 8.5, 'normal'),
        ("  SciPy · Painter's alg", '#e0f0ff', 8.5, 'normal'),
    ]

    y = 0.97
    for text, color, size, weight in lines:
        ax_info.text(0.07, y, text, transform=ax_info.transAxes,
                     color=color, fontsize=size, fontweight=weight,
                     fontfamily='monospace', va='top')
        y -= 0.038

    # Colour legend swatches
    y -= 0.01
    ax_info.text(0.07, y, "Depth Cue:", transform=ax_info.transAxes,
                 color='#a0c8f0', fontsize=10, fontweight='bold',
                 fontfamily='monospace', va='top')
    y -= 0.04
    for label, col in [("Near", '#ff7043'), ("Mid", '#7ec8f7'), ("Far", '#3a4a6a')]:
        rect = patches.FancyBboxPatch((0.07, y - 0.025), 0.12, 0.022,
                                       boxstyle="round,pad=0.002",
                                       facecolor=col, edgecolor='none',
                                       transform=ax_info.transAxes)
        ax_info.add_patch(rect)
        ax_info.text(0.22, y - 0.015, label, transform=ax_info.transAxes,
                     color='#c8e0ff', fontsize=8, fontfamily='monospace', va='center')
        y -= 0.038

draw_info_panel()

# ─────────────────────────────────────────────────────────────
#  ANIMATION STATE
# ─────────────────────────────────────────────────────────────

state = {
    'yaw': 0.3,
    'pitch': -0.25,
    'cam_dist': 6.0,
    'dragging': False,
    'last_xy': None,
    'auto_orbit': True,
    'frame': 0,
}

# ─────────────────────────────────────────────────────────────
#  RENDER FUNCTION
# ─────────────────────────────────────────────────────────────

def render(yaw, pitch):
    ax.clear()
    ax.set_facecolor('#050812')
    ax.set_xlim(-2.2, 2.2)
    ax.set_ylim(-1.8, 1.8)
    ax.set_aspect('equal')
    ax.axis('off')

    # Subtle star-field background
    rng = np.random.RandomState(0)
    stars_x = rng.uniform(-2.2, 2.2, 200)
    stars_y = rng.uniform(-1.8, 1.8, 200)
    stars_a = rng.uniform(0.1, 0.5, 200)
    ax.scatter(stars_x, stars_y, s=0.3, color='white', alpha=stars_a, zorder=0)

    R        = rotation_matrix(yaw, pitch)
    cam_pos  = np.array([0, 0, -state['cam_dist']])
    splats   = project_gaussians(GAUSSIANS, cam_pos, R, focal=3.0)

    depths = [s['depth'] for s in splats]
    d_min  = min(depths) if depths else 1
    d_max  = max(depths) if depths else 10

    for s in splats:
        t     = (s['depth'] - d_min) / max(d_max - d_min, 1e-6)
        r, g, b = s['color']

        # Slight depth-tinted colour
        r2 = r * (1 - 0.35*t) + 0.05*(1-t)
        g2 = g * (1 - 0.35*t) + 0.10*(1-t)
        b2 = b * (1 - 0.30*t) + 0.25*(1-t)
        r2, g2, b2 = np.clip([r2, g2, b2], 0, 1)

        alpha = s['alpha'] * (1 - 0.5*t)   # fade far splats

        ell = Ellipse(
            xy     = (s['sx'], s['sy']),
            width  = s['ex'] * 2,
            height = s['ey'] * 2,
            angle  = s['angle'],
            facecolor = (r2, g2, b2, alpha),
            edgecolor = (r2, g2, b2, alpha * 0.25),
            linewidth = 0.2,
            zorder = 1,
        )
        ax.add_patch(ell)

    # Frame counter overlay
    ax.text(-2.1, -1.7, f"Frame {state['frame']:04d}  |  Splats: {len(splats)}",
            color='#2a4a6a', fontsize=7, fontfamily='monospace', va='bottom')
    ax.text(-2.1,  1.65, f"Yaw: {np.degrees(yaw):6.1f}°   Pitch: {np.degrees(pitch):5.1f}°",
            color='#2a5a7a', fontsize=7, fontfamily='monospace', va='top')

    # Depth histogram in bottom panel
    ax_depth.clear()
    ax_depth.set_facecolor('#080d1a')
    if depths:
        ax_depth.hist(depths, bins=40, color='#2a6aaa', edgecolor='#1a3a6a',
                      linewidth=0.4, alpha=0.85)
        ax_depth.set_xlabel('Depth (camera space)', color='#4a7aaa', fontsize=7,
                             fontfamily='monospace')
        ax_depth.set_ylabel('Splat count', color='#4a7aaa', fontsize=7,
                             fontfamily='monospace')
        ax_depth.tick_params(colors='#3a6a9a', labelsize=6)
        ax_depth.set_title('Depth Distribution of Visible Splats',
                            color='#4a8aba', fontsize=7.5, fontfamily='monospace', pad=2)
    for sp in ax_depth.spines.values():
        sp.set_color('#1a2a4a')

# ─────────────────────────────────────────────────────────────
#  MOUSE INTERACTION
# ─────────────────────────────────────────────────────────────

def on_press(event):
    if event.inaxes == ax:
        state['dragging']  = True
        state['auto_orbit'] = False
        state['last_xy']   = (event.xdata, event.ydata)

def on_release(event):
    state['dragging'] = False
    state['last_xy']  = None

def on_move(event):
    if state['dragging'] and event.inaxes == ax and state['last_xy']:
        lx, ly = state['last_xy']
        dx = (event.xdata or lx) - lx
        dy = (event.ydata or ly) - ly
        state['yaw']   += dx * 0.6
        state['pitch'] += dy * 0.4
        state['pitch']  = np.clip(state['pitch'], -1.3, 1.3)
        state['last_xy'] = (event.xdata, event.ydata)

fig.canvas.mpl_connect('button_press_event',   on_press)
fig.canvas.mpl_connect('button_release_event', on_release)
fig.canvas.mpl_connect('motion_notify_event',  on_move)

# ─────────────────────────────────────────────────────────────
#  ANIMATION LOOP
# ─────────────────────────────────────────────────────────────

def animate(frame):
    state['frame'] = frame
    if state['auto_orbit']:
        state['yaw']   = frame * 0.018
        state['pitch'] = -0.25 + 0.15 * np.sin(frame * 0.012)
    render(state['yaw'], state['pitch'])
    return []

ani = FuncAnimation(fig, animate, frames=range(0, 10000),
                    interval=50, blit=False, repeat=True)

plt.tight_layout(pad=0)
plt.show()
