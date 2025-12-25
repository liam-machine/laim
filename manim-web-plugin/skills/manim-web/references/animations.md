# Manim Animation Reference

Complete reference for animations useful in splash screens and web graphics.

## Entry Animations

### FadeIn
```python
self.play(FadeIn(mobject))                    # Simple fade
self.play(FadeIn(mobject, shift=UP))          # Fade in from above
self.play(FadeIn(mobject, shift=DOWN * 2))    # Fade in from below
self.play(FadeIn(mobject, scale=0.5))         # Fade in while growing
self.play(FadeIn(mobject, scale=2))           # Fade in while shrinking
```

### GrowFromCenter
```python
self.play(GrowFromCenter(mobject))            # Expand from center point
```

### GrowFromPoint
```python
self.play(GrowFromPoint(mobject, ORIGIN))     # Grow from specific point
self.play(GrowFromPoint(mobject, UP * 3))     # Grow from top
```

### GrowFromEdge
```python
self.play(GrowFromEdge(mobject, LEFT))        # Grow from left edge
self.play(GrowFromEdge(mobject, DOWN))        # Grow from bottom edge
```

### SpinInFromNothing
```python
self.play(SpinInFromNothing(mobject))         # Spin while appearing
```

### SpiralIn
```python
self.play(SpiralIn(shapes))                   # Spiral trajectory entry
self.play(SpiralIn(shapes, scale_factor=8))   # Wider spiral
```

### DrawBorderThenFill
```python
self.play(DrawBorderThenFill(mobject))        # Draw outline, then fill
```

## Exit Animations

### FadeOut
```python
self.play(FadeOut(mobject))                   # Simple fade out
self.play(FadeOut(mobject, shift=UP))         # Fade out upward
self.play(FadeOut(mobject, scale=0.5))        # Shrink while fading
self.play(FadeOut(mobject, scale=2))          # Grow while fading
```

### ShrinkToCenter
```python
self.play(ShrinkToCenter(mobject))            # Collapse to center
```

### Uncreate
```python
self.play(Uncreate(mobject))                  # Reverse of Create
```

## Creation Animations

### Create
```python
self.play(Create(mobject))                    # Draw the mobject
self.play(Create(mobject, lag_ratio=0.1))     # Staggered drawing
```

### Write
```python
self.play(Write(text))                        # Handwriting effect
```

### AddTextLetterByLetter
```python
self.play(AddTextLetterByLetter(text))        # Typewriter effect
```

## Transform Animations

### Transform
```python
self.play(Transform(source, target))          # Morph one into another
```

### ReplacementTransform
```python
self.play(ReplacementTransform(source, target))  # Replace, don't overlay
```

### FadeTransform
```python
self.play(FadeTransform(source, target))      # Cross-fade morph
```

### MoveToTarget
```python
mobject.generate_target()
mobject.target.shift(RIGHT * 2)
mobject.target.scale(1.5)
self.play(MoveToTarget(mobject))              # Animate to target state
```

## Movement Animations

### Rotate
```python
self.play(Rotate(mobject, PI / 2))            # 90 degree rotation
self.play(Rotate(mobject, TAU))               # Full rotation
self.play(Rotate(mobject, PI, axis=RIGHT))    # 3D flip
```

### MoveAlongPath
```python
path = Circle()
dot = Dot()
self.play(MoveAlongPath(dot, path))           # Follow a path
```

### Circumscribe
```python
self.play(Circumscribe(mobject))              # Draw box around
```

### Indicate
```python
self.play(Indicate(mobject))                  # Highlight/pulse
```

### Flash
```python
self.play(Flash(mobject))                     # Brief flash effect
```

### Wiggle
```python
self.play(Wiggle(mobject))                    # Shake/wiggle
```

## Sequencing Animations

### LaggedStart
```python
# Stagger multiple animations
self.play(
    LaggedStart(
        *[FadeIn(m) for m in mobjects],
        lag_ratio=0.1
    )
)
```

### AnimationGroup
```python
# Play multiple animations together
self.play(
    AnimationGroup(
        FadeIn(obj1),
        FadeIn(obj2),
        lag_ratio=0.5
    )
)
```

### Succession
```python
# Chain animations sequentially
self.play(
    Succession(
        FadeIn(obj1),
        Transform(obj1, obj2),
        FadeOut(obj2),
    )
)
```

## The .animate Syntax

Transform any property change into an animation:

```python
# Scale
self.play(mobject.animate.scale(2))

# Move
self.play(mobject.animate.shift(RIGHT * 2))
self.play(mobject.animate.move_to(ORIGIN))

# Rotate
self.play(mobject.animate.rotate(PI / 4))

# Color
self.play(mobject.animate.set_color(RED))

# Opacity
self.play(mobject.animate.set_opacity(0.5))

# Chain multiple
self.play(
    mobject.animate
        .scale(1.5)
        .shift(UP)
        .set_color(BLUE)
)
```

## Timing Control

```python
# Duration
self.play(FadeIn(mobject), run_time=2)

# Wait between animations
self.wait(0.5)

# Easing (see easing.md for full list)
self.play(FadeIn(mobject), rate_func=ease_out_back)
```

## Web-Optimized Patterns

### Quick Logo Reveal
```python
self.play(
    FadeIn(logo, scale=0.8),
    run_time=0.8,
    rate_func=ease_out_back
)
```

### Staggered Text
```python
chars = Text("Loading...")
self.play(
    LaggedStart(
        *[FadeIn(c, shift=UP * 0.3) for c in chars],
        lag_ratio=0.05
    ),
    run_time=1
)
```

### Pulse Loop
```python
self.play(
    mobject.animate.scale(1.1),
    rate_func=there_and_back,
    run_time=0.5
)
```

### Smooth Exit
```python
self.play(
    FadeOut(mobject, shift=UP, scale=0.8),
    run_time=0.5,
    rate_func=ease_in_expo
)
```
