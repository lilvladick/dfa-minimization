#!/bin/bash

SOURCE_FILES="*.cpp"
OUTPUT_FILE="dfa"

echo "Compiling..."

clang++ -std=c++17 -o $OUTPUT_FILE $SOURCE_FILES

if [ $? -eq 0 ]; then
    echo "Compilation successful."
else
    echo "Compilation failed."
    exit 1
fi