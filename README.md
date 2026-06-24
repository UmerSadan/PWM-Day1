<div align="center">

# 🛠️ Muhammad Umer Sadan — Portfolio Repository

**Personal developer portfolio, project showcase, and ongoing learning log.**

[![No Dependencies](https://img.shields.io/badge/site-zero%20dependencies-success?style=flat-square)](#)
[![Vanilla JS](https://img.shields.io/badge/javascript-vanilla-f7df1e?style=flat-square&logo=javascript&logoColor=black)](#)
[![MERN](https://img.shields.io/badge/MERN-learning-orange?style=flat-square)](#)


</div>

---

## 👋 About Me

I'm Muhammad Umer Sadan, a software developer currently building my way up from the foundations. My main focus has been **low-level systems programming** — Assembly and C++ — where I enjoy working close to the hardware: memory management, registers, and how code actually executes underneath all the abstraction layers most frameworks hide.

Alongside that, I'm **learning full-stack web development with the MERN stack (MongoDB, Express, React, Node.js)**. I'm still at a beginner level here — comfortable with the basics of building CRUD apps, wiring up REST APIs, and connecting a React front end to a Node/Express back end, but very much still learning the deeper patterns (state management at scale, auth, testing, deployment pipelines) that come with experience.

This repo is where that learning shows up as actual code: a mix of low-level experiments, classic data-structures-and-algorithms practice, and beginner-to-intermediate MERN projects, all tied together by this portfolio site.

**What I'm currently focused on:**
- 🔧 Strengthening core CS fundamentals — data structures, algorithms, OOP design
- 🌐 Leveling up from beginner to intermediate in the MERN stack
- ⚙️ Exploring low-level systems work (Assembly, manual memory management) as a way to understand what's really happening under high-level code
- 🎨 Picking up front-end craft — animation, interaction design, performance — through projects like this portfolio itself

---

## 🧪 Projects

A breakdown of the projects featured on the portfolio, what they actually are, and what I was practicing with each:

### 🌐 Full-Stack CRUD Core
**Stack:** MongoDB · Express · React · Node.js

My main MERN learning project — a management/admin-style app covering the core CRUD lifecycle (Create, Read, Update, Delete) end-to-end. Built to practice structuring a REST API with Express, modeling data in MongoDB, and connecting it all to a React front end with basic state handling. As a beginner-level MERN project, the focus here was getting the fundamentals solid: routing, controllers, schema design, and a clean separation between client and server.

### ⚙️ Direct Assembly Engine
**Stack:** x86 Assembly · NASM

A low-level exercise in writing and running code directly in x86 Assembly — working with registers, manual control flow, and custom routines without any high-level language between me and the CPU. This is where I go to understand *why* higher-level languages behave the way they do.

### 🧩 Interactive OOP Pipeline
**Stack:** C++ · SFML

A small real-time rendering/interaction project used to practice solid object-oriented design in C++ — class hierarchies, polymorphism, and manual memory safety, paired with SFML for the rendering/interaction layer. Built primarily as OOP design practice rather than a finished product.

### 📊 Algorithmic Data Framework
**Stack:** C++ · Data Structures · Algorithms

A collection of custom data structure implementations and algorithm practice — sorting routines, tree operations, and graph traversal — written in C++ with manual memory handling. This is ongoing DS&A practice rather than a single app, the kind of repo that keeps growing as I work through new problems.

> 📝 **Note:** Project descriptions above are based on what's currently shown on the live site. If you'd like more detail per project (specific challenges solved, what you'd change now, live links, screenshots), let me know and I'll expand this section — that level of detail is best written by you, since you know what you actually built and learned.

---

## 🧱 Skills

| Area | Where I'm at |
|---|---|
| **Low-Level Systems (Assembly, C++)** | Most comfortable area — registers, manual memory, control flow |
| **C++ / OOP & Data Structures** | Solid practice with classes, polymorphism, sorting/tree/graph algorithms |
| **MERN Stack (MongoDB, Express, React, Node)** | Beginner — comfortable with CRUD apps and basic REST APIs, still building toward intermediate |
| **HTML / CSS3 / Vanilla JS** | Used to build this entire portfolio site from scratch, no frameworks |

I'd rather this list stay honest than impressive — it's a snapshot of where I am right now, not where I'll stay.

---

## 🖥️ Portfolio Site Features

Beyond the projects themselves, this repo also contains the portfolio site you're looking at — built as its own mini front-end project, with **zero external libraries**, just to practice CSS3 and vanilla JS interaction design:

| Feature | Description |
|---|---|
| 🧊 **Interactive 3D Cube** | A wireframe cube in the hero section auto-rotates at idle and turns to directly track the cursor on hover — built with pure CSS `transform-style: preserve-3d`, no canvas or WebGL. |
| 🌌 **Living Particle Background** | A lightweight Canvas2D node field drifts across the page, connecting nearby particles with proximity-based lines, with a subtle pull toward the cursor. |
| 🎨 **Dual Theme System** | A fully-themed dark ("Midnight Aurora") and light ("Sunlit Canvas") mode, toggled instantly with no flash-of-wrong-theme, driven entirely by CSS custom properties. |
| 🃏 **3D Tilt Cards** | Project cards and UI elements tilt realistically toward the cursor using `getBoundingClientRect()` math and CSS perspective transforms, snapping back smoothly on mouse leave. |
| 🧲 **Magnetic CTA Buttons** | Primary call-to-action buttons subtly pull toward the cursor on hover for a tactile, premium feel. |
| 🎞️ **Scroll Reveal Animations** | Sections fade and rise into view on scroll via `IntersectionObserver`, including animated skill-bar fills. |
| 💬 **Testimonials Slider** | A dependency-free carousel for peer/academic evaluations. |
| 📬 **Contact Form** | A clean, validated contact form ready to be wired up to your backend or form-handling service of choice. |
| ♿ **Accessibility-Aware Motion** | Every animation and interactive transform respects `prefers-reduced-motion`, disabling itself gracefully for users who need it. |
| ⚡ **Zero Dependencies** | No Three.js, GSAP, jQuery, or build tools — just modern CSS3 and vanilla JavaScript for maximum load speed. |

---

## 🧰 Site Tech Stack

*(Specifically for the portfolio site itself — see [Skills](#-skills) above for my broader stack.)*

- **Markup:** Semantic HTML5
- **Styling:** CSS3 — custom properties (theming), `perspective`/`transform-style: preserve-3d`, `@keyframes`, `backdrop-filter`
- **Scripting:** Vanilla JavaScript (ES6+) — Canvas API, `IntersectionObserver`, `requestAnimationFrame`, `getBoundingClientRect()`
- **Tooling:** None. Open the file, it just works.

---

## 🚀 Getting Started

No installation, no `npm install`, no build pipeline required.

```bash
# Clone the repository
git clone https://github.com/umersadan/portfolio.git

# Move into the project directory
cd portfolio

# Open it directly in your browser
open index.html        # macOS
start index.html       # Windows
xdg-open index.html    # Linux
```

Or simply double-click `index.html` — everything is bundled into a single file.

> 💡 **Tip:** For the best development experience (live reload while editing), serve it with any static server, e.g. `npx serve .` or the VS Code "Live Server" extension.

---

## 📁 Project Structure

```
portfolio/
├── index.html      # Entire site: markup, styles, and scripts in one file
└── README.md       # You are here
```

Everything lives in `index.html` by design — easy to drop into any static host (GitHub Pages, Netlify, Vercel) with no configuration.

---

## 🎨 Customization

All visual theming is centralized in CSS custom properties at the top of the `<style>` block:

```css
:root, html.dark {
    --bg-dark: #0b0712;
    --wood-glow: #ff7a45;   /* primary accent */
    --accent2: #7c5cff;    /* secondary accent */
    --text-bright: #fdf6f0;
    --text-muted: #b3a6c4;
}
```

To re-skin the entire site, change these values — every gradient, glow, border, and highlight derives from them automatically. Light mode overrides live in the adjacent `html.light` block.

To edit content, update the relevant sections directly in `index.html`:
- **Hero text:** `<header id="hero">`
- **Projects:** `.portfolio-grid` cards in `<section id="portfolio">`
- **Testimonials:** `.testimonial-slide` blocks in `<section id="testimonials">`
- **Contact links:** `.contact-links` in `<section id="contact">`

---

## 🌐 Deployment

This is a fully static site — deploy it anywhere in seconds:

- **GitHub Pages:** Push to a `gh-pages` branch or enable Pages on `main` in repo settings.
- **Netlify / Vercel:** Drag-and-drop the folder, or connect the repo for automatic deploys.
- **Any static host:** Upload `index.html` — no server-side runtime needed.

---

## 🤝 Connect

- 📧 **Email:** [umersadan90@gmail.com](mailto:umersadan90@gmail.com)
- 💼 **LinkedIn:** [linkedin.com/in/umersadan](https://linkedin.com/in/umersadan)
- 💻 **GitHub:** [github.com/umersadan](https://github.com/umersadan)

---

```

**If this portfolio template helped you, consider giving the repo a ⭐**
