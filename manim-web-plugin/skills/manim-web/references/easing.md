# Manim Easing Functions (rate_func)

Easing functions control the pace of animations. Use them via the `rate_func` parameter.

## Standard Easing

### smooth (default)
```python
self.play(FadeIn(obj), rate_func=smooth)
```
Gradual acceleration and deceleration. The default for most animations.

### linear
```python
self.play(Rotate(obj, TAU), rate_func=linear)
```
Constant speed. Best for continuous loops like spinners.

### there_and_back
```python
self.play(obj.animate.scale(1.2), rate_func=there_and_back)
```
Goes forward then reverses. Perfect for pulses and heartbeats.

### there_and_back_with_pause
```python
self.play(obj.animate.scale(1.2), rate_func=there_and_back_with_pause)
```
Forward, pause at peak, then reverse.

## Quadratic Easing

### ease_in_quad
```python
rate_func=ease_in_quad  # Slow start, accelerate
```

### ease_out_quad
```python
rate_func=ease_out_quad  # Fast start, decelerate
```

### ease_in_out_quad
```python
rate_func=ease_in_out_quad  # Smooth both ends
```

## Cubic Easing

### ease_in_cubic
```python
rate_func=ease_in_cubic  # Stronger slow start
```

### ease_out_cubic
```python
rate_func=ease_out_cubic  # Stronger fast start
```

### ease_in_out_cubic
```python
rate_func=ease_in_out_cubic  # Smoother than quad
```

## Quartic Easing

### ease_in_quart
```python
rate_func=ease_in_quart  # Very slow start
```

### ease_out_quart
```python
rate_func=ease_out_quart  # Very fast start
```

### ease_in_out_quart
```python
rate_func=ease_in_out_quart  # Dramatic both ends
```

## Exponential Easing

### ease_in_expo
```python
rate_func=ease_in_expo  # Extreme slow start
```
Great for dramatic exits.

### ease_out_expo
```python
rate_func=ease_out_expo  # Extreme fast start
```
Great for snappy entrances.

### ease_in_out_expo
```python
rate_func=ease_in_out_expo  # Extreme both ends
```

## Back Easing (Overshoot)

### ease_in_back
```python
rate_func=ease_in_back  # Pull back before moving
```

### ease_out_back
```python
rate_func=ease_out_back  # Overshoot then settle
```
**Recommended for logo reveals** - gives a satisfying "pop".

### ease_in_out_back
```python
rate_func=ease_in_out_back  # Back on both ends
```

## Elastic Easing

### ease_in_elastic
```python
rate_func=ease_in_elastic  # Wind up like a spring
```

### ease_out_elastic
```python
rate_func=ease_out_elastic  # Spring release wobble
```
Great for playful, bouncy UI elements.

### ease_in_out_elastic
```python
rate_func=ease_in_out_elastic  # Spring both ends
```

## Bounce Easing

### ease_in_bounce
```python
rate_func=ease_in_bounce  # Bounce at start
```

### ease_out_bounce
```python
rate_func=ease_out_bounce  # Bounce at end
```
Perfect for "landing" animations.

### ease_in_out_bounce
```python
rate_func=ease_in_out_bounce  # Bounce both ends
```

## Special Functions

### rush_into
```python
rate_func=rush_into  # Fast start, slow middle
```

### rush_from
```python
rate_func=rush_from  # Slow start, fast end
```

### double_smooth
```python
rate_func=double_smooth  # Extra smooth (S-curve)
```

### lingering
```python
rate_func=lingering  # Quick start, long settle
```

### running_start
```python
rate_func=running_start  # Pull back then rush forward
```

### not_quite_there
```python
rate_func=not_quite_there  # Approach but don't complete
```

## Web Animation Recommendations

### Logo Reveals
```python
rate_func=ease_out_back  # Pop with overshoot
```

### Loading Spinners
```python
rate_func=linear  # Constant rotation
```

### Button Hovers
```python
rate_func=ease_out_quad  # Quick response
```

### Page Transitions
```python
rate_func=ease_in_out_cubic  # Smooth both ends
```

### Attention Grabbers
```python
rate_func=ease_out_elastic  # Bouncy and fun
```

### Exits/Dismissals
```python
rate_func=ease_in_expo  # Quick exit
```

### Pulses/Heartbeats
```python
rate_func=there_and_back  # Natural pulse
```

## Combining with run_time

The `rate_func` controls *how* it moves, `run_time` controls *how long*:

```python
# Quick, snappy reveal (0.5s with overshoot)
self.play(FadeIn(logo), rate_func=ease_out_back, run_time=0.5)

# Slow, dramatic entrance (2s with elastic)
self.play(FadeIn(logo), rate_func=ease_out_elastic, run_time=2)

# Fast spinner (0.5s per rotation, constant speed)
self.play(Rotate(spinner, TAU), rate_func=linear, run_time=0.5)
```

## Custom Rate Functions

Create your own easing:

```python
def my_easing(t):
    # t goes from 0 to 1
    # return value should also be 0 to 1
    return t * t * t  # cubic ease-in

self.play(FadeIn(obj), rate_func=my_easing)
```
