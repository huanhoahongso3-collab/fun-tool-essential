#include <iostream>
#include <fstream>
#include <opencv2/opencv.hpp>
#include <string>
#include <vector>
#include <getopt.h>
#include <filesystem>

#ifdef USE_CLIP
#include <clip/clip.h>
#endif

const std::string ASCII_CHARS = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ";

std::string image_to_ascii(const std::string& image_path, double scale, int width, int height, bool invert) {
    if (image_path.size() >= 4 && image_path.substr(image_path.size() - 4) == ".gif") {
        throw std::runtime_error("GIF format is not supported.");
    }

    cv::Mat image = cv::imread(image_path, cv::IMREAD_GRAYSCALE);
    if (image.empty()) {
        throw std::runtime_error("Could not open or read image.");
    }

    int orig_w = image.cols;
    int orig_h = image.rows;
    int new_w, new_h;

    if (width > 0 && height > 0) {
        new_w = width;
        new_h = height;
    } else if (width > 0) {
        new_w = width;
        new_h = static_cast<int>((width / static_cast<double>(orig_w)) * orig_h * 0.5);
    } else if (height > 0) {
        new_h = height;
        new_w = static_cast<int>((height / static_cast<double>(orig_h)) * orig_w * 2);
    } else if (scale > 0) {
        new_w = static_cast<int>(orig_w * scale);
        new_h = static_cast<int>(orig_h * scale * 0.5);
    } else {
        new_w = orig_w;
        new_h = static_cast<int>(orig_h * 0.5);
    }

    cv::resize(image, image, cv::Size(new_w, new_h));

    std::string ascii;
    for (int y = 0; y < new_h; ++y) {
        for (int x = 0; x < new_w; ++x) {
            int pixel = image.at<uchar>(y, x);
            if (invert) pixel = 255 - pixel;
            int idx = pixel * ASCII_CHARS.size() / 256;
            ascii += ASCII_CHARS[idx];
        }
        ascii += '\n';
    }

    return ascii;
}

void print_usage() {
    std::cout <<
        "Usage: banana [-f FILE] [-s SCALE] [-w WIDTH] [-h HEIGHT] [-o OUTPUT] [-c] [-t] [-i]\n"
        "Options:\n"
        "  -f FILE     Input image file (excluding .gif)\n"
        "  -s SCALE    Scale factor (e.g., 0.5)\n"
        "  -w WIDTH    Output width in characters\n"
        "  -h HEIGHT   Output height in characters\n"
        "  -o FILE     Output ASCII art to text file\n"
        "  -c          Copy ASCII art to clipboard (requires clip library)\n"
        "  -t          Disable terminal output\n"
        "  -i          Invert brightness\n"
        "  --help      Show this help message\n";
}

int main(int argc, char* argv[]) {
    std::string input_file;
    std::string output_file;
    bool copy_clipboard = false;
    bool no_terminal = false;
    bool invert = false;
    double scale = 0;
    int width = 0, height = 0;

    static struct option long_options[] = {
        {"help", no_argument, 0, 0},
        {0, 0, 0, 0}
    };

    int opt;
    int opt_index = 0;
    while ((opt = getopt_long(argc, argv, "f:s:w:h:o:cti", long_options, &opt_index)) != -1) {
        switch (opt) {
            case 0:
                print_usage();
                return 0;
            case 'f':
                input_file = optarg;
                break;
            case 's':
                scale = std::stod(optarg);
                break;
            case 'w':
                width = std::stoi(optarg);
                break;
            case 'h':
                height = std::stoi(optarg);
                break;
            case 'o':
                output_file = optarg;
                break;
            case 'c':
                copy_clipboard = true;
                break;
            case 't':
                no_terminal = true;
                break;
            case 'i':
                invert = true;
                break;
            default:
                print_usage();
                return 1;
        }
    }

    if (input_file.empty() && optind < argc) {
        input_file = argv[optind];
    }

    if (input_file.empty()) {
        std::cerr << "Error: No input file provided.\n";
        return 1;
    }

    if (!std::filesystem::exists(input_file)) {
        std::cerr << "Error: File does not exist.\n";
        return 1;
    }

    if (no_terminal && output_file.empty() && !copy_clipboard) {
        std::cerr << "Error: -t requires -o or -c.\n";
        return 1;
    }

    if (scale > 0 && (width > 0 || height > 0)) {
        std::cerr << "Error: Use either -s or -w/-h, not both.\n";
        return 1;
    }

    try {
        std::string ascii = image_to_ascii(input_file, scale, width, height, invert);

        if (!no_terminal) {
            std::cout << ascii;
        }

        if (!output_file.empty()) {
            std::ofstream out(output_file);
            if (!out) {
                std::cerr << "Error writing to file.\n";
                return 1;
            }
            out << ascii;
            std::cout << "ASCII art written to " << output_file << "\n";
        }

#ifdef USE_CLIP
        if (copy_clipboard) {
            clip::set_text(ascii);
            std::cout << "ASCII art copied to clipboard.\n";
        }
#else
        if (copy_clipboard) {
            std::cerr << "Clipboard feature not available. Rebuild with clip support.\n";
        }
#endif

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }

    return 0;
}
