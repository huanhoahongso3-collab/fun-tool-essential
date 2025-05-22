import argparse
import os
from pydub import AudioSegment
from pydub.effects import spatialize
from pydub.exceptions import CouldntDecodeError

def convert_to_8d(input_path, output_path):
    """
    Converts an audio file to 8D audio and saves it.

    Args:
        input_path (str): The path to the input audio file.
        output_path (str): The path to save the 8D audio file.
    """
    try:
        # Load the audio file
        print(f"Loading audio from: {input_path}")
        # AudioSegment.from_file automatically detects the format
        audio = AudioSegment.from_file(input_path)

        # Convert the audio to 8D
        print("Converting to 8D audio...")
        # The spatialize effect simulates 8D audio by panning the sound
        # left and right over time. The 'spatial_type' can be adjusted
        # for different panning patterns if desired, but '8d' is a common
        # and effective one for this purpose.
        audio_8d = spatialize(audio, spatial_type='8d')

        # Save the 8D audio to a file
        print(f"Exporting 8D audio to: {output_path}")
        # Exporting in mp3 format. Ensure FFmpeg is installed and accessible in your system's PATH.
        audio_8d.export(output_path, format="mp3")
        print("Conversion complete!")
    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_path}'")
    except CouldntDecodeError:
        print(f"Error: Could not decode audio file '{input_path}'. Make sure it's a valid audio format (e.g., MP3, WAV) and FFmpeg is correctly installed.")
    except Exception as e:
        print(f"An unexpected error occurred during conversion: {e}")

def main():
    """
    Parses command-line arguments and orchestrates the 8D audio conversion.
    """
    parser = argparse.ArgumentParser(
        description="Convert audio files to 8D audio.",
        formatter_class=argparse.RawTextHelpFormatter
    )

    # Create mutually exclusive groups for file and folder operations
    group_file = parser.add_argument_group('Single File Conversion')
    group_folder = parser.add_argument_group('Folder Conversion')

    group_file.add_argument(
        '-f', '--file',
        type=str,
        help="Input audio file path (e.g., audio.mp3).\nRequires -o/--output."
    )
    group_file.add_argument(
        '-o', '--output',
        type=str,
        help="Output 8D audio file path (e.g., 8d.mp3).\nRequires -f/--file."
    )

    group_folder.add_argument(
        '-fo', '--folder_in',
        type=str,
        help="Input folder containing audio files.\nRequires -of/--folder_out."
    )
    group_folder.add_argument(
        '-of', '--folder_out',
        type=str,
        help="Output folder to save 8D audio files.\nRequires -fo/--folder_in."
    )

    # Add a help argument
    parser.add_argument(
        '-h', '--help',
        action='help',
        default=argparse.SUPPRESS, # Suppress default help to use our custom one
        help="Show this help message and exit."
    )

    args = parser.parse_args()

    # Check for valid argument combinations
    if args.file and args.output:
        if args.folder_in or args.folder_out:
            parser.error("Error: Cannot use -f/-o with -fo/-of simultaneously.")
        convert_to_8d(args.file, args.output)
    elif args.folder_in and args.folder_out:
        if args.file or args.output:
            parser.error("Error: Cannot use -fo/-of with -f/-o simultaneously.")

        input_folder = args.folder_in
        output_folder = args.folder_out

        if not os.path.isdir(input_folder):
            print(f"Error: Input folder '{input_folder}' does not exist.")
            return

        os.makedirs(output_folder, exist_ok=True) # Create output folder if it doesn't exist

        print(f"Processing files in folder: {input_folder}")
        for filename in os.listdir(input_folder):
            # Process common audio formats. pydub relies on FFmpeg for decoding.
            if filename.lower().endswith(('.mp3', '.wav', '.flac', '.ogg', '.aac', '.m4a')):
                input_path = os.path.join(input_folder, filename)
                # Construct output filename, preserving the original extension
                name, ext = os.path.splitext(filename)
                # Append '_8d' to the filename before the extension
                output_path = os.path.join(output_folder, f"{name}_8d{ext}")
                convert_to_8d(input_path, output_path)
            else:
                print(f"Skipping non-audio file: {filename}")
    else:
        # If no valid combination is provided, show help
        parser.print_help()
        print("\nError: Please provide either -f and -o for single file conversion, or -fo and -of for folder conversion.")

if __name__ == "__main__":
    main()
