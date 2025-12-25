"""
Splash Screen Templates for Manim Web

Ready-to-use templates for common splash screen patterns.
Copy and customize for your project.

Render with:
    manim -t --format webm -qh splash_screens.py LogoReveal
"""

from manim import *


class LogoReveal(Scene):
    """
    Classic logo reveal with scale and glow effect.
    Customize: Change "YourApp" to your app name, adjust colors.
    """

    def construct(self):
        # Configuration
        APP_NAME = "YourApp"
        PRIMARY_COLOR = "#6366f1"  # Indigo
        SECONDARY_COLOR = "#8b5cf6"  # Purple

        # Create logo text with gradient
        logo = Text(
            APP_NAME,
            font_size=120,
            font="SF Pro Display",  # Change to your font
            gradient=(PRIMARY_COLOR, SECONDARY_COLOR),
        )

        # Glow effect (blurred copy behind)
        glow = logo.copy()
        glow.set_color(PRIMARY_COLOR)
        glow.set_opacity(0.4)
        glow.scale(1.02)

        # Animation sequence
        self.play(
            FadeIn(glow, scale=0.7),
            FadeIn(logo, scale=0.7),
            run_time=1.2,
            rate_func=ease_out_back,
        )

        # Subtle pulse
        self.play(
            logo.animate.scale(1.05),
            glow.animate.scale(1.08).set_opacity(0.6),
            rate_func=there_and_back,
            run_time=0.4,
        )

        self.wait(0.5)


class LogoWithTagline(Scene):
    """
    Logo with animated tagline appearing below.
    """

    def construct(self):
        APP_NAME = "YourApp"
        TAGLINE = "Build something amazing"

        logo = Text(APP_NAME, font_size=100, color=WHITE)
        tagline = Text(TAGLINE, font_size=36, color=GRAY_B)

        # Position tagline below logo
        tagline.next_to(logo, DOWN, buff=0.5)

        # Logo enters
        self.play(
            FadeIn(logo, scale=0.8),
            run_time=0.8,
            rate_func=ease_out_back,
        )

        # Tagline types in
        self.play(
            AddTextLetterByLetter(tagline),
            run_time=1.2,
        )

        self.wait(0.5)


class ParticleLogoReveal(Scene):
    """
    Logo letters fly in from scattered positions.
    Great for energetic, dynamic brands.
    """

    def construct(self):
        APP_NAME = "LAUNCH"

        logo = Text(APP_NAME, font_size=120, color=WHITE)

        # Each letter animates in from a different direction
        self.play(
            LaggedStart(
                *[
                    FadeIn(
                        char,
                        shift=UP * 3 * ((-1) ** i),  # Alternate up/down
                        scale=0.3,
                    )
                    for i, char in enumerate(logo)
                ],
                lag_ratio=0.08,
            ),
            run_time=1.5,
            rate_func=ease_out_expo,
        )

        # Settle with a bounce
        self.play(
            logo.animate.scale(1.05),
            rate_func=ease_out_elastic,
            run_time=0.6,
        )

        self.wait(0.3)


class CircularReveal(Scene):
    """
    Logo reveals with a circular mask/wipe effect.
    Clean, modern feel.
    """

    def construct(self):
        APP_NAME = "Flow"

        logo = Text(APP_NAME, font_size=120, color=WHITE)

        # Start scaled down
        logo.scale(0.1)

        # Grow outward
        self.play(
            logo.animate.scale(10),  # Scale to normal (0.1 * 10 = 1)
            rate_func=ease_out_expo,
            run_time=1.0,
        )

        self.wait(0.5)


class GradientMorphLogo(Scene):
    """
    Shape morphs into logo text.
    Great for showing transformation/evolution.
    """

    def construct(self):
        APP_NAME = "Morph"

        # Starting shape
        circle = Circle(radius=1.5, color=BLUE, fill_opacity=1)

        # Target logo
        logo = Text(APP_NAME, font_size=100, color=BLUE)

        # Show circle
        self.play(GrowFromCenter(circle), run_time=0.5)
        self.wait(0.2)

        # Morph to logo
        self.play(
            ReplacementTransform(circle, logo),
            run_time=1.2,
            rate_func=ease_in_out_cubic,
        )

        # Color shift
        self.play(
            logo.animate.set_color_by_gradient(BLUE, PURPLE, PINK),
            run_time=0.5,
        )

        self.wait(0.5)


class LoadingSpinner(Scene):
    """
    Simple loading spinner animation.
    Loops seamlessly - render with --loop flag or repeat in CSS.
    """

    def construct(self):
        # Spinner ring
        ring = Circle(radius=0.8, color=BLUE_C, stroke_width=8)
        ring.set_fill(opacity=0)

        # Arc that rotates
        arc = Arc(
            radius=0.8,
            start_angle=0,
            angle=PI / 2,
            color=WHITE,
            stroke_width=8,
        )

        self.add(ring)

        # One full rotation
        self.play(
            Rotate(arc, TAU, about_point=ORIGIN),
            rate_func=linear,
            run_time=1.0,
        )


class LoadingDots(Scene):
    """
    Three dots pulsing in sequence.
    Classic loading indicator.
    """

    def construct(self):
        dots = VGroup(*[Dot(radius=0.15, color=WHITE) for _ in range(3)])
        dots.arrange(RIGHT, buff=0.4)

        self.add(dots)

        # Pulse each dot in sequence
        for _ in range(2):  # Two cycles
            for dot in dots:
                self.play(
                    dot.animate.scale(1.5).set_color(BLUE),
                    rate_func=there_and_back,
                    run_time=0.3,
                )


class MinimalLogoReveal(Scene):
    """
    Ultra-minimal: just fade and slight movement.
    For understated, professional brands.
    """

    def construct(self):
        APP_NAME = "minimal"

        logo = Text(APP_NAME, font_size=80, color=WHITE, font="Helvetica")

        self.play(
            FadeIn(logo, shift=UP * 0.3),
            run_time=1.5,
            rate_func=ease_out_quad,
        )

        self.wait(1)


class IconWithText(Scene):
    """
    Icon/symbol with app name.
    Replace the circle with your SVG icon.
    """

    def construct(self):
        APP_NAME = "AppName"

        # Replace with: SVGMobject("your_icon.svg")
        icon = Circle(radius=0.6, color=BLUE, fill_opacity=1)

        name = Text(APP_NAME, font_size=60, color=WHITE)
        name.next_to(icon, RIGHT, buff=0.5)

        group = VGroup(icon, name)
        group.move_to(ORIGIN)

        # Icon scales in
        self.play(
            GrowFromCenter(icon),
            run_time=0.6,
            rate_func=ease_out_back,
        )

        # Text fades in
        self.play(
            FadeIn(name, shift=LEFT * 0.3),
            run_time=0.5,
        )

        self.wait(0.5)


class SplitReveal(Scene):
    """
    Two halves of logo slide together.
    Dramatic reveal effect.
    """

    def construct(self):
        APP_NAME = "SPLIT"

        # Create full logo, then split
        full_logo = Text(APP_NAME, font_size=120, color=WHITE)

        # Get left and right halves
        midpoint = len(APP_NAME) // 2
        left_text = Text(APP_NAME[:midpoint], font_size=120, color=WHITE)
        right_text = Text(APP_NAME[midpoint:], font_size=120, color=WHITE)

        # Position halves
        left_text.move_to(LEFT * 4)
        right_text.move_to(RIGHT * 4)

        self.add(left_text, right_text)

        # Slide together
        self.play(
            left_text.animate.move_to(full_logo[:midpoint].get_center()),
            right_text.animate.move_to(full_logo[midpoint:].get_center()),
            run_time=0.8,
            rate_func=ease_out_expo,
        )

        self.wait(0.5)
