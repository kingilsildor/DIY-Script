#!/bin/bash

# Usage check
if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <input_directory> <output_file>"
  exit 1
fi

PDF_DIR="$1"
OUTPUT="$2"

# Check if directory exists
if [[ ! -d "$PDF_DIR" ]]; then
  echo "Directory not found: $PDF_DIR"
  exit 1
fi

# Rename files with spaces to use underscores
find "$PDF_DIR" -maxdepth 1 -type f -name "* *" | while IFS= read -r file; do
  newname="${file// /_}"
  mv "$file" "$newname"
done

# Create temporary directory for cleaned PDFs
TMP_DIR=$(mktemp -d)

# Preprocess and collect PDFs (no subdirectories)
mapfile -t sorted_pdfs < <(find "$PDF_DIR" -maxdepth 1 -type f -name "*.pdf" -printf '%T@ %p\n' | sort -n | awk '{print $2}')

# Exit if no PDFs found
if [[ ${#sorted_pdfs[@]} -eq 0 ]]; then
  echo "No PDF files found in directory: $PDF_DIR"
  rm -rf "$TMP_DIR"
  exit 1
fi

# Clean PDFs using qpdf
cleaned_pdfs=()
for f in "${sorted_pdfs[@]}"; do
  base=$(basename "$f")
  qpdf "$f" --linearize "$TMP_DIR/$base"
  cleaned_pdfs+=("$TMP_DIR/$base")
done

# Merge cleaned PDFs
pdfunite "${cleaned_pdfs[@]}" "$OUTPUT"

# Cleanup
rm -rf "$TMP_DIR"

echo "Merged into $OUTPUT"

