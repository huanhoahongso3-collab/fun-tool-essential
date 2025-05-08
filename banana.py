import argparse
import os
import sys
from PIL import Image

try:
    import pyperclip
except ImportError:
    print("Missing dependency: pyperclip. Install it with `pip install pyperclip`.")
    sys.exit(1)

ASCII_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

def image_to_ascii(image_path, scale=None, width=None, height=None, invert=False):
    if image_path.lower().endswith('.gif'):
        raise ValueError("GIF format is not supported.")

    try:
        image = Image.open(image_path)
    except Exception as e:
        raise ValueError(f"Unable to open image: {e}")

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
    image = image.convert('L')

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
    print("banana v1.2: convert JPG to ASCII art")

    parser = argparse.ArgumentParser(
        add_help=False,
        usage="banana [-f F] [-s S] [-w WIDTH] [-h HEIGHT] [-o O] [-c] [-t] [-i] [--help] [positional_input]",
        description="banana: convert JPG to ASCII art"
    )

    flags = parser.add_argument_group("options")
    flags.add_argument('-f', help="Input image file (excluding .gif)")
    flags.add_argument('-s', type=float, help="Scale factor (e.g., -s 0.5)")
    flags.add_argument('-w', type=int, dest='width', help="Width of ASCII output (e.g., -w 100)")
    flags.add_argument('-h', type=int, dest='height', help="Height of ASCII output (e.g., -h 100)")
    flags.add_argument('-o', help="Output .txt file")
    flags.add_argument('-c', action='store_true', help="Copy ASCII art to clipboard")
    flags.add_argument('-t', action='store_true', help="Disable terminal output (requires -o or -c)")
    flags.add_argument('-i', action='store_true', help="Invert brightness (dark becomes light)")
    flags.add_argument('--help', action='help', help="Show this help message and exit")

    parser.add_argument('positional_input', nargs='?', help="Positional input file fallback")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    image_file = args.f or args.positional_input

    if not image_file:
        print("Error: No input file provided. Use -f or provide image path directly.")
        sys.exit(1)

    if not os.path.isfile(image_file):
        print(f"Error: File '{image_file}' does not exist.")
        sys.exit(1)

    if image_file.lower().endswith('.gif'):
        print("Error: .gif images are not supported.")
        sys.exit(1)

    if args.t and not (args.o or args.c):
        print("Error: When using -t (no terminal output), at least -o or -c must be specified.")
        sys.exit(1)

    if args.s and (args.width or args.height):
        print("Error: Use either -s (scale) OR -w/-h (dimensions), not both.")
        sys.exit(1)

    try:
        ascii_art = image_to_ascii(
            image_path=image_file,
            scale=args.s,
            width=args.width,
            height=args.height,
            invert=args.i
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    if not args.t:
        print(ascii_art)

    if args.o:
        try:
            with open(args.o, 'w') as f:
                f.write(ascii_art)
            print(f"ASCII art written to {args.o}")
        except Exception as e:
            print(f"Error writing to file: {e}")
            sys.exit(1)

    if args.c:
        try:
            pyperclip.copy(ascii_art)
            print("ASCII art copied to clipboard.")
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()
