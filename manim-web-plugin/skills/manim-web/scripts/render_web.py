#!/usr/bin/env python3
"""
Manim Web Renderer

Utility script for rendering Manim scenes optimized for web use.
Handles transparent backgrounds, web-friendly formats, and common presets.

Usage:
    python render_web.py scene.py ClassName --format gif --quality medium
    python render_web.py scene.py ClassName --transparent --format webm
    python render_web.py scene.py ClassName --preset splash
"""

import argparse
import subprocess
import sys
from pathlib import Path


PRESETS = {
    "splash": {
        "quality": "h",  # 1080p
        "fps": 60,
        "format": "webm",
        "transparent": True,
        "description": "Splash screen (1080p, 60fps, transparent WebM)"
    },
    "splash-gif": {
        "quality": "m",  # 720p
        "fps": 30,
        "format": "gif",
        "transparent": True,
        "description": "Splash screen GIF fallback (720p, 30fps)"
    },
    "loading": {
        "quality": "l",  # 480p
        "fps": 30,
        "format": "gif",
        "transparent": True,
        "description": "Loading spinner (480p, 30fps, small file)"
    },
    "hero": {
        "quality": "k",  # 4K
        "fps": 60,
        "format": "webm",
        "transparent": False,
        "description": "Hero section video (4K, 60fps)"
    },
    "preview": {
        "quality": "l",  # 480p
        "fps": 15,
        "format": "gif",
        "transparent": False,
        "description": "Quick preview (480p, 15fps)"
    },
    "social": {
        "quality": "m",  # 720p
        "fps": 30,
        "format": "gif",
        "transparent": False,
        "description": "Social media (720p, 30fps, no transparency)"
    },
}


def build_command(
    scene_file: str,
    scene_name: str,
    quality: str = "m",
    fps: int = None,
    format: str = None,
    transparent: bool = False,
    output_dir: str = None,
    output_file: str = None,
) -> list:
    """Build the manim command with appropriate flags."""
    cmd = ["manim"]

    # Quality flag
    cmd.append(f"-q{quality}")

    # FPS override
    if fps:
        cmd.extend(["--fps", str(fps)])

    # Output format
    if format:
        cmd.extend(["--format", format])

    # Transparency
    if transparent:
        cmd.append("-t")

    # Output directory
    if output_dir:
        cmd.extend(["--media_dir", output_dir])

    # Output file name
    if output_file:
        cmd.extend(["-o", output_file])

    # Scene file and name
    cmd.append(scene_file)
    cmd.append(scene_name)

    return cmd


def list_presets():
    """Print available presets."""
    print("\nAvailable presets:\n")
    for name, config in PRESETS.items():
        print(f"  {name:12} - {config['description']}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Render Manim scenes optimized for web use",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use a preset
  python render_web.py scene.py LogoReveal --preset splash

  # Custom settings
  python render_web.py scene.py Loading --format gif --transparent -q l

  # High quality hero video
  python render_web.py scene.py HeroAnimation --preset hero

  # List all presets
  python render_web.py --list-presets
        """
    )

    parser.add_argument("scene_file", nargs="?", help="Python file containing the scene")
    parser.add_argument("scene_name", nargs="?", help="Name of the Scene class to render")

    parser.add_argument("--preset", "-p", choices=list(PRESETS.keys()),
                        help="Use a predefined configuration preset")
    parser.add_argument("--list-presets", action="store_true",
                        help="List available presets and exit")

    parser.add_argument("--quality", "-q", choices=["l", "m", "h", "k"],
                        default="m", help="Quality: l=480p, m=720p, h=1080p, k=4K")
    parser.add_argument("--fps", type=int, help="Frames per second (default: based on quality)")
    parser.add_argument("--format", "-f", choices=["gif", "webm", "mp4", "mov"],
                        help="Output format")
    parser.add_argument("--transparent", "-t", action="store_true",
                        help="Render with transparent background")
    parser.add_argument("--output-dir", "-d", help="Output directory")
    parser.add_argument("--output-file", "-o", help="Output filename (without extension)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print command without executing")

    args = parser.parse_args()

    # Handle --list-presets
    if args.list_presets:
        list_presets()
        return 0

    # Require scene file and name
    if not args.scene_file or not args.scene_name:
        parser.print_help()
        return 1

    # Check scene file exists
    if not Path(args.scene_file).exists():
        print(f"Error: Scene file '{args.scene_file}' not found", file=sys.stderr)
        return 1

    # Apply preset if specified
    if args.preset:
        preset = PRESETS[args.preset]
        quality = preset["quality"]
        fps = preset.get("fps")
        format = preset["format"]
        transparent = preset["transparent"]
        print(f"Using preset '{args.preset}': {preset['description']}")
    else:
        quality = args.quality
        fps = args.fps
        format = args.format
        transparent = args.transparent

    # Build command
    cmd = build_command(
        scene_file=args.scene_file,
        scene_name=args.scene_name,
        quality=quality,
        fps=fps,
        format=format,
        transparent=transparent,
        output_dir=args.output_dir,
        output_file=args.output_file,
    )

    print(f"Command: {' '.join(cmd)}")

    if args.dry_run:
        print("(dry run - not executing)")
        return 0

    # Execute
    try:
        result = subprocess.run(cmd, check=True)
        return result.returncode
    except subprocess.CalledProcessError as e:
        print(f"Error: Manim exited with code {e.returncode}", file=sys.stderr)
        return e.returncode
    except FileNotFoundError:
        print("Error: 'manim' command not found. Install with: pip install manim", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
