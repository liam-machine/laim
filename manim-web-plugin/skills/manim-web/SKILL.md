---
name: manim-web
description: Create animated splash screens and web animations using Manim (the 3Blue1Brown animation library). Use this skill when the user wants to "create a splash screen", "make a loading animation", "animate a logo", "create web animations", "make an intro animation", "generate animated GIFs", "create motion graphics", or mentions Manim, splash screens, logo reveals, or animated intros for websites and web apps.
---

# Manim Web Animations Skill

Create professional splash screens, loading animations, and web-ready motion graphics using Manim Community - the animation engine behind 3Blue1Brown's videos.

## Quick Start

### Prerequisites

```bash
# Install Manim Community
pip install manim

# Verify installation
manim --version
```

### Basic Usage

Create a scene file and render it:

```python
from manim import *

class LogoReveal(Scene):
    def construct(self):
        # Your logo text
        logo = Text("MyApp", font_size=96, gradient=(BLUE, PURPLE))

        # Animate with spiral entry
        self.play(SpiralIn(logo), run_time=1.5)
        self.wait(0.5)

        # Pulse effect
        self.play(logo.animate.scale(1.1), rate_func=there_and_back, run_time=0.3)
        self.wait(0.5)
```

Render with transparency for web:

```bash
# GIF with transparency (web-ready)
manim -t --format gif -ql scene.py LogoReveal

# WebM with transparency (modern browsers)
manim -t --format webm -ql scene.py LogoReveal

# High quality MP4 (no transparency)
manim -qh scene.py LogoReveal
```

## Output Formats

| Format | Transparency | Best For | Command Flag |
|--------|--------------|----------|--------------|
| GIF | Yes | Fallback, email | `--format gif -t` |
| WebM | Yes | Modern browsers | `--format webm -t` |
| MOV | Yes | Video editing | `-t` (default when transparent) |
| MP4 | No | Universal playback | (default) |

## Quality Presets

| Flag | Resolution | FPS | Use Case |
|------|------------|-----|----------|
| `-ql` | 480p | 15 | Quick preview |
| `-qm` | 720p | 30 | Development |
| `-qh` | 1080p | 60 | Production |
| `-qk` | 4K | 60 | High-end |

## Common Patterns

### Logo Reveal with Glow

```python
class GlowingLogo(Scene):
    def construct(self):
        logo = Text("Brand", font_size=120, color=WHITE)
        glow = logo.copy().set_color(BLUE).set_opacity(0.5)
        glow.scale(1.05)

        self.play(
            FadeIn(glow, scale=0.8),
            FadeIn(logo, scale=0.8),
            run_time=1.5,
            rate_func=ease_out_back
        )
        self.wait()
```

### Particle Explosion Entry

```python
class ParticleEntry(Scene):
    def construct(self):
        logo = Text("Launch", font_size=100, gradient=(ORANGE, RED))

        # Break into submobjects for particle effect
        self.play(
            LaggedStart(
                *[FadeIn(char, shift=UP * 2, scale=0.5)
                  for char in logo],
                lag_ratio=0.1
            ),
            run_time=1.5
        )
        self.wait()
```

### Loading Spinner

```python
class LoadingSpinner(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        dot = Dot(color=WHITE).move_to(circle.point_from_proportion(0))

        self.add(circle, dot)
        self.play(
            MoveAlongPath(dot, circle),
            rate_func=linear,
            run_time=2
        )
```

### Morphing Shapes

```python
class ShapeMorph(Scene):
    def construct(self):
        shapes = [
            Circle(color=BLUE, fill_opacity=0.8),
            Square(color=GREEN, fill_opacity=0.8),
            Triangle(color=RED, fill_opacity=0.8),
        ]

        current = shapes[0]
        self.play(Create(current))

        for next_shape in shapes[1:]:
            self.play(Transform(current, next_shape))
            self.wait(0.3)
```

## Easing Functions (rate_func)

Web animations feel polished with the right easing:

| Function | Effect | Best For |
|----------|--------|----------|
| `smooth` | Ease in-out | Default, natural |
| `ease_out_back` | Overshoot then settle | Logo reveals |
| `ease_out_elastic` | Springy bounce | Playful UI |
| `ease_out_bounce` | Ball bounce | Attention grab |
| `ease_in_expo` | Slow start, fast end | Exits |
| `linear` | Constant speed | Spinners, loops |
| `there_and_back` | Forward then reverse | Pulses |

## Color & Gradients

```python
# Gradient text
text = Text("Gradient", gradient=(BLUE, GREEN, YELLOW))

# Apply gradient to any mobject
shape = Circle()
shape.set_color_by_gradient(RED, PURPLE, BLUE)

# Common web palettes
DARK_BG = "#0a0a0a"
ACCENT = "#6366f1"  # Indigo
```

## Transparent Background Setup

For web overlays, use transparent backgrounds:

```python
from manim import *

config.background_color = BLACK  # Will be transparent with -t flag
config.background_opacity = 0    # Fully transparent

class TransparentScene(Scene):
    def construct(self):
        # Your animations here
        pass
```

Then render with:
```bash
manim -t --format webm -qh scene.py TransparentScene
```

## Resources

- **Templates**: Pre-built scenes in `${CLAUDE_PLUGIN_ROOT}/skills/manim-web/templates/`
- **Render Script**: `${CLAUDE_PLUGIN_ROOT}/skills/manim-web/scripts/render_web.py`
- **Animation Reference**: `${CLAUDE_PLUGIN_ROOT}/skills/manim-web/references/animations.md`
- **Easing Reference**: `${CLAUDE_PLUGIN_ROOT}/skills/manim-web/references/easing.md`

## Troubleshooting

### LaTeX not found
```bash
# macOS
brew install --cask mactex-no-gui

# Ubuntu
sudo apt install texlive-full
```

### Slow rendering
- Use `-ql` for previews
- Reduce `run_time` values
- Use simpler shapes during development

### GIF too large
- Reduce resolution with `-ql` or custom `--resolution`
- Shorten animation duration
- Use WebM instead (better compression)

## Tips for Web

1. **Keep animations short** - 1-3 seconds for splash screens
2. **Use WebM** - Best compression with transparency
3. **Provide GIF fallback** - For older browsers/email
4. **Test on mobile** - Render at appropriate sizes
5. **Loop seamlessly** - End state should transition to start
