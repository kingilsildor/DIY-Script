#!/bin/bash

# Check if folder is provided as argument
if [ -z "$1" ]; then
  echo "Usage: $0 <folder-path>"
  exit 1
fi

# Folder to organize
folder="$1"

# Check if the provided folder exists
if [ ! -d "$folder" ]; then
  echo "Error: '$folder' is not a valid directory."
  exit 1
fi

# Navigate to the folder
cd "$folder"

# Loop through all files in the folder
for file in *.*; do
  # Only process files, not directories
  if [ -f "$file" ]; then
    # Extract file extension (everything after the last dot)
    extension="${file##*.}"
    
    # Create a subdirectory for the extension if it doesn't exist
    if [ ! -d "$extension" ]; then
      mkdir "$extension"
    fi
    
    # Check if the file already exists in the target folder
    target="$extension/$file"
    if [ -e "$target" ]; then
      # If the file exists, append '-duplicate' to the filename
      base_name="${file%.*}"
      target="$extension/${base_name}-duplicate.$extension"
    fi
    
    # Move the file to the corresponding folder
    mv "$file" "$target"
    echo "Moved $file to $target"
  fi
done

echo "File organization completed!"

