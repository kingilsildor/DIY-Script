#!/bin/bash

# Check if at least one argument (number of copies) is provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <num_copies> <file1> <file2> ..."
    exit 1
fi

# Number of copies is the first argument
NUM_COPIES=$1

# Shift the arguments so that $@ contains only the files
shift

# Loop through all files passed as arguments
for file in "$@"; do
    # Check if the file exists
    if [ -f "$file" ]; then
        # Loop to copy the file NUM_COPIES times
        for i in $(seq 1 $NUM_COPIES); do
            cp "$file" "${file%.*}_$i.${file##*.}"
            echo "Copied $file to ${file%.*}_$i.${file##*.}"
        done
    else
        echo "Error: $file does not exist!"
    fi
done

