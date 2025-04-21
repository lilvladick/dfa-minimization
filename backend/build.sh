#!/bin/bash

set -e

SOURCE_FILES="*.cpp"
OUTPUT_FILE="dfa_minimizer"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    INCLUDE_DIRS="-Iinclude -I/opt/homebrew/include -I/usr/local/include -I/opt/homebrew/include/nlohmann"
else
    # Linux (Ubuntu)
    INCLUDE_DIRS="-Iinclude -I/usr/local/include"
fi

CXX_FLAGS="-std=c++17 -pthread"

echo "Текущая директория: $(pwd)"
echo "Файлы:"
ls -l

echo "Compiling..."

clang++ $CXX_FLAGS $INCLUDE_DIRS -o $OUTPUT_FILE $SOURCE_FILES

echo "Compilation successful. Run with ./$OUTPUT_FILE"
exit 0
