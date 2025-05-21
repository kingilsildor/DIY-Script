#!/bin/bash

# Check if folder path is provided
if [ -z "$1" ]; then
  echo "Usage: $0 <folder_path>"
  exit 1
fi

folder="$1"

# Check if it's a valid directory
if [ ! -d "$folder" ]; then
  echo "Error: '$folder' is not a valid directory."
  exit 1
fi

# Rename files in the specified folder
for file in "$folder"/*\ *; do
  [ -e "$file" ] || continue  # skip if no matching files
  newname="${file// /_}"
  mv "$file" "$newname"
done

echo "Renaming completed."

