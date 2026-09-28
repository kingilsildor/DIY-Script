#!/bin/bash

set -euo pipefail

if [[ $# -ne 1 ]]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

dir="$1"

if [[ ! -d "$dir" ]]; then
    echo "Error: '$dir' is not a directory."
    exit 1
fi

shopt -s nullglob

for file in "$dir"/imm???_*; do
    base=$(basename "$file")

    # Extract the 3-digit number
    num="${base:3:3}"

    # Ensure it's numeric
    [[ "$num" =~ ^[0-9]{3}$ ]] || continue

    # Add 25 and keep leading zeros
    newnum=$(printf "%03d" $((10#$num + 25)))
    newbase="imm${newnum}${base:6}"
    newfile="$dir/$newbase"

    echo "Renaming: $base -> $newbase"
    mv -- "$file" "$newfile"
done
