#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
# ]
# ///
"""
Animate an image using Google's Veo API (image-to-video).

Usage:
    uv run animate_image.py --image "input.png" --prompt "description of motion" --filename "output.mp4"
"""

import argparse
import base64
import mimetypes
import os
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Animate an image using Google Veo API"
    )
    parser.add_argument(
        "--image", "-i",
        required=True,
        help="Input image file to animate"
    )
    parser.add_argument(
        "--prompt", "-p",
        required=True,
        help="Description of the motion/animation"
    )
    parser.add_argument(
        "--filename", "-f",
        required=True,
        help="Output filename (e.g., output.mp4)"
    )
    parser.add_argument(
        "--duration", "-d",
        type=int,
        default=8,
        help="Video duration in seconds (default: 8)"
    )
    parser.add_argument(
        "--aspect-ratio", "-a",
        choices=["16:9", "9:16", "1:1"],
        default="16:9",
        help="Aspect ratio (default: 16:9)"
    )
    parser.add_argument(
        "--model", "-m",
        default="veo-3.1-generate-preview",
        help="Veo model to use (default: veo-3.1-generate-preview)"
    )

    args = parser.parse_args()

    # Verify input image exists
    image_path = Path(args.image)
    if not image_path.exists():
        print(f"Error: Image file not found: {args.image}", file=sys.stderr)
        sys.exit(1)

    # Import after parsing to fail fast if google-genai isn't installed
    from google import genai
    from google.genai import types

    # Initialize client (relies on GEMINI_API_KEY env var)
    client = genai.Client()

    # Set up output path
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Animating image with model {args.model}...")
    print(f"  Image: {args.image}")
    print(f"  Prompt: {args.prompt}")
    print(f"  Duration: {args.duration}s")
    print(f"  Aspect ratio: {args.aspect_ratio}")

    try:
        # Read image and encode as base64
        print("Loading image...")
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        
        # Detect mime type
        mime_type, _ = mimetypes.guess_type(str(image_path))
        if mime_type is None:
            mime_type = "image/png"  # Default
        
        print(f"Image mime type: {mime_type}")
        
        # Create Image object with raw bytes
        image = types.Image(
            image_bytes=image_bytes,
            mime_type=mime_type
        )

        # Start the video generation with image
        operation = client.models.generate_videos(
            model=args.model,
            prompt=args.prompt,
            image=image,
            config=types.GenerateVideosConfig(
                duration_seconds=args.duration,
                aspect_ratio=args.aspect_ratio,
            )
        )

        print(f"Operation started: {operation.name}")

        # Poll until done
        while not operation.done:
            print("Waiting for video generation to complete...")
            time.sleep(10)
            # Refresh operation state
            operation = client.operations.get(operation)

        print("Video generation complete!")

        # Get the generated video
        generated_video = operation.response.generated_videos[0]

        # Download the video
        print(f"Downloading video...")
        client.files.download(file=generated_video.video)
        generated_video.video.save(str(output_path))

        # Verify and report
        if output_path.exists():
            size_mb = output_path.stat().st_size / (1024 * 1024)
            print(f"\nVideo saved: {output_path} ({size_mb:.2f} MB)")
            print(f"MEDIA: {output_path}")
        else:
            print("Error: Video file was not saved.", file=sys.stderr)
            sys.exit(1)

    except Exception as e:
        print(f"Error generating video: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
