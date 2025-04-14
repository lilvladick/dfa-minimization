#!/bin/bash

SOURCE_FILES="*.cpp"
OUTPUT_FILE="dfa_minimizer"
INCLUDE_DIRS="-Iinclude -I/opt/homebrew/include -I/usr/local/include -Iinclude -I/opt/homebrew/include/nlohmann"
CXX_FLAGS="-std=c++17 -pthread"

echo "Compiling..."

clang++ $CXX_FLAGS $INCLUDE_DIRS -o $OUTPUT_FILE $SOURCE_FILES

if [ $? -eq 0 ]; then
    echo "Compilation successful. Run with ./dfa_minimizer"
else
    echo "Compilation failed."
    exit 1
fi
