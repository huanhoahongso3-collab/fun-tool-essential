#include <opencv2/opencv.hpp>
#include <iostream>
#include <fstream>
#include <string>
#include <thread>
#include <chrono>
#include <getopt.h>

const std::string ASCII_CHARS = R"($@B%8&WM#*oahkbdpqwmZ0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,"^`'. )";

std::string frameToAscii(const cv::Mat& frame, int width = 0, int height = 0, float scale = 0.0, bool invert = false) {
    cv::Mat gray;
    cv::cvtColor(frame, gray, cv::COLOR_BGR2GRAY);

    int orig_w = gray.cols;
    int orig_h = gray.rows;

    int new_w = orig_w, new_h = orig_h * 0.5;

    if (width > 0 && height > 0) {
        new_w = width;
        new_h = height;
    } else if (width > 0) {
        new_w = width;
        new_h = (float(width) / orig_w) * orig_h * 0.5;
    } else if (height > 0) {
        new_h = height;
        new_w = (float(height) / orig_h) * orig_w * 2;
    } else if (scale > 0.0f) {
        new_w = orig_w * scale;
        new_h = orig_h * scale * 0.5;
    }

    cv::resize(gray, gray, cv::Size(new_w, new_h));

    std::string ascii;
    for (int y = 0; y < gray.rows; y++) {
        for (int x = 0; x < gray.cols; x++) {
            int pixel = gray.at<uchar>(y, x);
            if (invert) pixel = 255 - pixel;
            char c = ASCII_CHARS[pixel * ASCII_CHARS.length() / 256];
            ascii += c;
        }
        ascii += '\n';
    }
    return ascii;
}

void printHelp() {
    std::cout << "Usage: banana-video -f FILE [-w WIDTH -H HEIGHT | -s SCALE] [-i] [-o OUTPUT] [-t] [-p] [-frame N -frame-out FILE]\n";
}

int main(int argc, char** argv) {
    std::string file, outputFile, frameOutFile;
    int width = 0, height = 0, frameNum = -1;
    float scale = 0.0;
    bool invert = false, suppress = false, play = false;

    const struct option long_opts[] = {
        {"file", required_argument, nullptr, 'f'},
        {"scale", required_argument, nullptr, 's'},
        {"width", required_argument, nullptr, 'w'},
        {"height", required_argument, nullptr, 'H'},
        {"output", required_argument, nullptr, 'o'},
        {"invert", no_argument, nullptr, 'i'},
        {"suppress", no_argument, nullptr, 't'},
        {"play", no_argument, nullptr, 'p'},
        {"frame", required_argument, nullptr, 1},
        {"frame-out", required_argument, nullptr, 2},
        {nullptr, 0, nullptr, 0}
    };

    int opt;
    while ((opt = getopt_long(argc, argv, "f:s:w:H:o:itp", long_opts, nullptr)) != -1) {
        switch (opt) {
            case 'f': file = optarg; break;
            case 's': scale = std::stof(optarg); break;
            case 'w': width = std::stoi(optarg); break;
            case 'H': height = std::stoi(optarg); break;
            case 'o': outputFile = optarg; break;
            case 'i': invert = true; break;
            case 't': suppress = true; break;
            case 'p': play = true; break;
            case 1: frameNum = std::stoi(optarg); break;
            case 2: frameOutFile = optarg; break;
            default: printHelp(); return 1;
        }
    }

    if (file.empty()) {
        std::cerr << "Error: Missing input file.\n";
        printHelp();
        return 1;
    }

    if ((width || height) && scale > 0.0f) {
        std::cerr << "Error: Use either width/height or scale, not both.\n";
        return 1;
    }

    if ((width && !height) || (!width && height)) {
        std::cerr << "Error: Both width and height must be specified.\n";
        return 1;
    }

    cv::VideoCapture cap(file);
    if (!cap.isOpened()) {
        std::cerr << "Error: Could not open video.\n";
        return 1;
    }

    int totalFrames = cap.get(cv::CAP_PROP_FRAME_COUNT);

    // Frame export
    if (frameNum >= 0 && !frameOutFile.empty()) {
        if (frameNum >= totalFrames || frameNum < 0) {
            std::cerr << "Error: Frame out of range (0 to " << totalFrames - 1 << ").\n";
            return 1;
        }
        cap.set(cv::CAP_PROP_POS_FRAMES, frameNum);
        cv::Mat frame;
        if (cap.read(frame)) {
            cv::imwrite(frameOutFile, frame);
            std::cout << "Saved frame " << frameNum << " to " << frameOutFile << "\n";
            return 0;
        } else {
            std::cerr << "Error: Could not read the requested frame.\n";
            return 1;
        }
    }

    std::ostringstream output;

    int frameIdx = 0;
    while (true) {
        cv::Mat frame;
        if (!cap.read(frame)) break;

        std::string ascii = frameToAscii(frame, width, height, scale, invert);

        if (play) {
            std::cout << "\033[2J\033[H";  // Clear screen
            std::cout << ascii;
            std::this_thread::sleep_for(std::chrono::milliseconds(100));
        } else if (!suppress) {
            std::cout << "Frame " << frameIdx++ << ":\n";
            std::cout << ascii << "\n";
        }

        if (!outputFile.empty()) {
            output << ascii << "\n";
        }
    }

    cap.release();

    if (!outputFile.empty()) {
        std::ofstream out(outputFile);
        if (out) {
            out << output.str();
            std::cout << "Saved output to " << outputFile << "\n";
        } else {
            std::cerr << "Error: Could not write to file.\n";
        }
    }

    return 0;
}
