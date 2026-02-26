#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-genai>=1.0.0",
# ]
# ///
"""
Generate videos using Google's Veo API.
"""

import argparse
import sys
import time
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description="Generate video using Google Veo API")
    parser.add_argument("--prompt", "-p", required=True, help="Video description/prompt")
    parser.add_argument("--filename", "-f", required=True, help="Output filename")
    parser.add_argument("--image", "-i", help="Input image for image-to-video")
    parser.add_argument("--duration", "-d", type=int, default=8, help="Duration in seconds")
    parser.add_argument("--aspect-ratio", "-a", choices=["16:9", "9:16", "1:1"], default="16:9")
    parser.add_argument("--model", "-m", default="veo-3.0-generate-001")
    args = parser.parse_args()

    from google import genai
    from google.genai import types

    client = genai.Client()
    output_path = Path(args.filename)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"Generating video with model {args.model}...")
    print(f"  Prompt: {args.prompt}")
    print(f"  Duration: {args.duration}s")
    print(f"  Aspect ratio: {args.aspect_ratio}")

    try:
        config = types.GenerateVideosConfig(
            duration_seconds=args.duration,
            aspect_ratio=args.aspect_ratio,
        )

        # Handle image-to-video
        image_obj = None
        if args.image:
            image_path = Path(args.image)
            if not image_path.exists():
                print(f"Error: Image not found: {args.image}", file=sys.stderr)
                sys.exit(1)
            print(f"  Input image: {args.image}")
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
            suffix = image_path.suffix.lower()
            mime_type = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}.get(suffix, 'image/png')
            image_obj = types.Image(image_bytes=image_bytes, mime_type=mime_type)

        # Start generation
        if image_obj:
            operation = client.models.generate_videos(
                model=args.model, prompt=args.prompt, image=image_obj, config=config
            )
        else:
            operation = client.models.generate_videos(
                model=args.model, prompt=args.prompt, config=config
            )

        print(f"Operation started: {operation.name}")

        # Poll with proper check (done can be None, False, or True)
        max_attempts = 60
        for attempt in range(max_attempts):
            if operation.done is True:
                break
            print("Waiting for video generation to complete...")
            time.sleep(10)
            operation = client.operations.get(operation)
        
        if operation.done is not True:
            print("Error: Timeout waiting for video generation", file=sys.stderr)
            sys.exit(1)

        print("Video generation complete!")

        # Check for errors
        if operation.error:
            print(f"Error from API: {operation.error}", file=sys.stderr)
            sys.exit(1)

        # Check response
        if not operation.response or not operation.response.generated_videos:
            print("Error: No video generated (response empty)", file=sys.stderr)
            if operation.response:
                print(f"Response: {operation.response}", file=sys.stderr)
            sys.exit(1)

        # Download
        generated_video = operation.response.generated_videos[0]
        print("Downloading video...")
        client.files.download(file=generated_video.video)
        generated_video.video.save(str(output_path))

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
