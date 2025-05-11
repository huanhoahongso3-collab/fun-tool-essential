import argparse
import cv2
import os
import sys
from PIL import Image
import numpy as np
import time

ASCII_CHARS = r"$@B%8&WM#*oahkbdpqwmZ0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

def frame_to_ascii(frame, width=None, height=None, scale=None, invert=False):
    image = Image.fromarray(frame).convert("L")

    orig_w, orig_h = image.size
    if width and height:
        new_w, new_h = width, height
    elif width:
        new_w = width
        new_h = int((width / orig_w) * orig_h * 0.5)
    elif height:
        new_h = height
        new_w = int((height / orig_h) * orig_w * 2)
    elif scale:
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale * 0.5)
    else:
        new_w, new_h = orig_w, int(orig_h * 0.5)

    image = image.resize((new_w, new_h))

    ascii_str = ""
    for y in range(new_h):
        for x in range(new_w):
            pixel = image.getpixel((x, y))
            if invert:
                pixel = 255 - pixel
            ascii_str += ASCII_CHARS[pixel * len(ASCII_CHARS) // 256]
        ascii_str += "\n"
    return ascii_str

def main():
    print("banana: convert video to ASCII art")

    parser = argparse.ArgumentParser(
        usage="banana-video.py [-f FILE] [-s SCALE] [-w WIDTH] [-H HEIGHT] [-o OUTPUT] [-t] [-i] [-p] [-frame N -frame-out FILE]",
        description="banana: convert video to ASCII art"
    )

    parser.add_argument('-f', help="Input video file", required=True)
    parser.add_argument('-s', type=float, help="Scale factor")
    parser.add_argument('-w', type=int, help="Output width")
    parser.add_argument('-H', type=int, help="Output height")
    parser.add_argument('-o', help="Output .txt file")
    parser.add_argument('-t', action='store_true', help="Suppress terminal output")
    parser.add_argument('-i', action='store_true', help="Invert brightness")
    parser.add_argument('-p', action='store_true', help="Play video in terminal (override previous frame)")
    parser.add_argument('-frame', type=int, help="Frame number to export as image")
    parser.add_argument('-frame-out', help="Output image file for frame export")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    if not os.path.isfile(args.f):
        print(f"Error: Video file '{args.f}' does not exist.")
        sys.exit(1)

    cap = cv2.VideoCapture(args.f)
    if not cap.isOpened():
        print("Error: Could not open video.")
        sys.exit(1)

    # Export frame as image if requested
    if args.frame is not None and args.frame_out:
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if args.frame >= total or args.frame < 0:
            print(f"Error: Frame number out of range. Video has {total} frames.")
            sys.exit(1)
        cap.set(cv2.CAP_PROP_POS_FRAMES, args.frame)
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read the requested frame.")
            sys.exit(1)
        cv2.imwrite(args.frame_out, frame)
        print(f"Frame {args.frame} saved to {args.frame_out}")
        sys.exit(0)

    # In case -p is used, we need to play the video frames in the terminal
    if args.p:
        if args.o:
            print("Error: -p and -o cannot be used together. Please choose one.")
            sys.exit(1)

        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            ascii_frame = frame_to_ascii(
                frame,
                width=args.w,
                height=args.H,
                scale=args.s,
                invert=args.i
            )

            # Clear terminal and print the frame
            print("\033c", end="")
            print(ascii_frame, end="")
            time.sleep(0.1)  # Slow down for visual effect (adjust as necessary)

            frame_count += 1

        cap.release()
        return

    frame_count = 0
    output = ""

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ascii_frame = frame_to_ascii(
            frame,
            width=args.w,
            height=args.H,
            scale=args.s,
            invert=args.i
        )

        if args.o:
            # If -o is specified, write output without frame number header and separate with blank line
            output += f"{ascii_frame}\n"

        if not args.t and not args.p:
            print(f"Frame {frame_count}:")
            print(ascii_frame)
            print("\n")

        frame_count += 1

    cap.release()

    if args.o:
        try:
            with open(args.o, 'w') as f:
                f.write(output)
            print(f"ASCII video written to {args.o}")
        except Exception as e:
            print(f"Error writing to file: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()
