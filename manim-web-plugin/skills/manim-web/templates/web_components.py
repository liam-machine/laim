"""
Web Component Animation Templates

Animations for common web UI elements: buttons, cards, notifications, etc.

Render with:
    manim -t --format gif -qm web_components.py ButtonHover
"""

from manim import *


class ButtonHover(Scene):
    """
    Button hover state animation.
    Export frames for CSS sprite or use as reference.
    """

    def construct(self):
        # Button shape
        button = RoundedRectangle(
            corner_radius=0.2,
            width=3,
            height=1,
            color=BLUE,
            fill_opacity=1,
        )

        label = Text("Click me", font_size=32, color=WHITE)
        label.move_to(button.get_center())

        btn_group = VGroup(button, label)

        self.add(btn_group)
        self.wait(0.2)

        # Hover effect: scale up slightly, brighten
        self.play(
            btn_group.animate.scale(1.05),
            button.animate.set_color(BLUE_B),
            rate_func=ease_out_quad,
            run_time=0.2,
        )

        self.wait(0.3)

        # Return to normal
        self.play(
            btn_group.animate.scale(1 / 1.05),
            button.animate.set_color(BLUE),
            rate_func=ease_out_quad,
            run_time=0.2,
        )

        self.wait(0.2)


class CardFlip(Scene):
    """
    3D card flip animation.
    Great for reveal effects or card-based UIs.
    """

    def construct(self):
        # Front of card
        front = RoundedRectangle(
            corner_radius=0.3,
            width=3,
            height=4,
            color=BLUE,
            fill_opacity=1,
        )
        front_label = Text("Front", color=WHITE)
        front_label.move_to(front.get_center())
        front_group = VGroup(front, front_label)

        # Back of card
        back = RoundedRectangle(
            corner_radius=0.3,
            width=3,
            height=4,
            color=GREEN,
            fill_opacity=1,
        )
        back_label = Text("Back", color=WHITE)
        back_label.move_to(back.get_center())
        back_group = VGroup(back, back_label)

        # Position back behind front
        back_group.set_opacity(0)

        self.add(front_group, back_group)
        self.wait(0.3)

        # Flip animation (scale X to 0, swap, scale X back)
        self.play(
            front_group.animate.scale([0, 1, 1]),
            run_time=0.3,
            rate_func=ease_in_quad,
        )

        front_group.set_opacity(0)
        back_group.set_opacity(1)
        back_group.scale([0, 1, 1])

        self.play(
            back_group.animate.scale([1, 1, 1]),
            run_time=0.3,
            rate_func=ease_out_quad,
        )

        self.wait(0.3)


class NotificationSlide(Scene):
    """
    Toast notification sliding in from top.
    """

    def construct(self):
        # Notification card
        notif = RoundedRectangle(
            corner_radius=0.2,
            width=5,
            height=1,
            color=DARK_GRAY,
            fill_opacity=0.95,
        )

        icon = Circle(radius=0.2, color=GREEN, fill_opacity=1)
        icon.move_to(notif.get_left() + RIGHT * 0.5)

        message = Text("Success! Your changes were saved.", font_size=20, color=WHITE)
        message.next_to(icon, RIGHT, buff=0.3)

        notif_group = VGroup(notif, icon, message)

        # Start above screen
        notif_group.move_to(UP * 5)

        self.add(notif_group)

        # Slide in
        self.play(
            notif_group.animate.move_to(UP * 3),
            rate_func=ease_out_back,
            run_time=0.4,
        )

        self.wait(1.5)

        # Slide out
        self.play(
            notif_group.animate.move_to(UP * 5),
            rate_func=ease_in_quad,
            run_time=0.3,
        )


class ProgressBar(Scene):
    """
    Animated progress bar filling up.
    """

    def construct(self):
        # Background track
        track = RoundedRectangle(
            corner_radius=0.15,
            width=6,
            height=0.3,
            color=DARK_GRAY,
            fill_opacity=1,
        )

        # Progress fill
        fill = RoundedRectangle(
            corner_radius=0.15,
            width=0.1,  # Start tiny
            height=0.3,
            color=BLUE,
            fill_opacity=1,
        )
        fill.align_to(track, LEFT)

        # Percentage text
        percent = Text("0%", font_size=24, color=WHITE)
        percent.next_to(track, UP, buff=0.3)

        self.add(track, fill, percent)
        self.wait(0.3)

        # Animate to 100%
        target_fill = fill.copy()
        target_fill.stretch_to_fit_width(6)
        target_fill.align_to(track, LEFT)

        self.play(
            Transform(fill, target_fill),
            run_time=2,
            rate_func=ease_in_out_quad,
        )

        # Update percentage (simplified - in practice you'd use ValueTracker)
        self.play(
            Transform(percent, Text("100%", font_size=24, color=WHITE).move_to(percent)),
            run_time=0.3,
        )

        self.wait(0.3)


class SkeletonLoader(Scene):
    """
    Skeleton loading state with shimmer effect.
    """

    def construct(self):
        # Skeleton rectangles
        skeleton = VGroup(
            RoundedRectangle(width=5, height=0.5, corner_radius=0.1, color=GRAY, fill_opacity=0.3),
            RoundedRectangle(width=4, height=0.5, corner_radius=0.1, color=GRAY, fill_opacity=0.3),
            RoundedRectangle(width=4.5, height=0.5, corner_radius=0.1, color=GRAY, fill_opacity=0.3),
        )
        skeleton.arrange(DOWN, buff=0.3, aligned_edge=LEFT)

        # Shimmer gradient (simplified - a moving highlight)
        shimmer = Rectangle(width=1, height=3, fill_opacity=0.3, color=WHITE)
        shimmer.set_stroke(width=0)
        shimmer.move_to(LEFT * 4)

        self.add(skeleton, shimmer)

        # Move shimmer across
        for _ in range(2):
            self.play(
                shimmer.animate.move_to(RIGHT * 4),
                rate_func=linear,
                run_time=1.5,
            )
            shimmer.move_to(LEFT * 4)


class CheckmarkSuccess(Scene):
    """
    Animated checkmark appearing in a circle.
    Classic success indicator.
    """

    def construct(self):
        # Circle
        circle = Circle(radius=1, color=GREEN, stroke_width=6)
        circle.set_fill(opacity=0)

        # Checkmark path
        check = VMobject()
        check.set_points_as_corners([
            LEFT * 0.4 + DOWN * 0.1,
            DOWN * 0.4,
            RIGHT * 0.5 + UP * 0.4,
        ])
        check.set_stroke(color=GREEN, width=6)

        # Animate circle drawing
        self.play(Create(circle), run_time=0.5)

        # Animate checkmark
        self.play(Create(check), run_time=0.4, rate_func=ease_out_quad)

        # Scale pulse
        group = VGroup(circle, check)
        self.play(
            group.animate.scale(1.1),
            rate_func=there_and_back,
            run_time=0.3,
        )

        self.wait(0.3)


class MenuExpand(Scene):
    """
    Hamburger menu expanding to full menu.
    """

    def construct(self):
        # Hamburger icon (three lines)
        lines = VGroup(
            Line(LEFT * 0.5, RIGHT * 0.5, color=WHITE, stroke_width=4),
            Line(LEFT * 0.5, RIGHT * 0.5, color=WHITE, stroke_width=4),
            Line(LEFT * 0.5, RIGHT * 0.5, color=WHITE, stroke_width=4),
        )
        lines.arrange(DOWN, buff=0.15)
        lines.move_to(LEFT * 3 + UP * 3)

        # Menu items (hidden initially)
        menu_items = VGroup(
            Text("Home", font_size=36, color=WHITE),
            Text("About", font_size=36, color=WHITE),
            Text("Contact", font_size=36, color=WHITE),
        )
        menu_items.arrange(DOWN, buff=0.5)
        menu_items.set_opacity(0)

        self.add(lines, menu_items)
        self.wait(0.3)

        # Transform hamburger to X
        x_lines = VGroup(
            Line(LEFT * 0.4 + UP * 0.4, RIGHT * 0.4 + DOWN * 0.4, color=WHITE, stroke_width=4),
            Line(LEFT * 0.4 + DOWN * 0.4, RIGHT * 0.4 + UP * 0.4, color=WHITE, stroke_width=4),
        )
        x_lines.move_to(lines.get_center())

        self.play(
            Transform(lines, x_lines),
            run_time=0.3,
        )

        # Fade in menu items
        self.play(
            menu_items.animate.set_opacity(1),
            LaggedStart(
                *[item.animate.shift(RIGHT * 0.5) for item in menu_items],
                lag_ratio=0.1,
            ),
            run_time=0.5,
        )

        self.wait(0.5)


class TabSwitch(Scene):
    """
    Tab indicator sliding between tabs.
    """

    def construct(self):
        # Tab labels
        tabs = VGroup(
            Text("Tab 1", font_size=28, color=WHITE),
            Text("Tab 2", font_size=28, color=GRAY),
            Text("Tab 3", font_size=28, color=GRAY),
        )
        tabs.arrange(RIGHT, buff=1.5)

        # Active indicator (underline)
        indicator = Line(
            tabs[0].get_left() + DOWN * 0.3,
            tabs[0].get_right() + DOWN * 0.3,
            color=BLUE,
            stroke_width=4,
        )

        self.add(tabs, indicator)
        self.wait(0.3)

        # Switch to tab 2
        self.play(
            indicator.animate.move_to(tabs[1].get_center() + DOWN * 0.3),
            tabs[0].animate.set_color(GRAY),
            tabs[1].animate.set_color(WHITE),
            run_time=0.3,
            rate_func=ease_out_quad,
        )

        self.wait(0.3)

        # Switch to tab 3
        self.play(
            indicator.animate.move_to(tabs[2].get_center() + DOWN * 0.3),
            tabs[1].animate.set_color(GRAY),
            tabs[2].animate.set_color(WHITE),
            run_time=0.3,
            rate_func=ease_out_quad,
        )

        self.wait(0.3)
