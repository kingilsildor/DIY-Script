#!/bin/bash

# Ensure a file is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <markdown-file>"
    exit 1
fi

MARKDOWN_FILE="$1"

# Check if file exists
if [ ! -f "$MARKDOWN_FILE" ]; then
    echo "Error: File '$MARKDOWN_FILE' not found."
    exit 1
fi

# Check if git-fame is installed
if ! command -v git-fame &> /dev/null; then
    echo "Error: git-fame not found. Install it using 'pip install git-fame'."
    exit 1
fi

# Run git-fame and capture output
GIT_FAME_OUTPUT=$(git-fame --format=markdown)

# Check if "## Git Fame" exists in file
if grep -q "## Git Fame" "$MARKDOWN_FILE"; then
    # Replace existing Git Fame section
    awk -v fame="$GIT_FAME_OUTPUT" '
    BEGIN { in_section=0 }
    /^## Git Fame/ { print; print ""; print fame; in_section=1; next }
    /^## / && in_section { in_section=0 }
    !in_section { print }
    ' "$MARKDOWN_FILE" > tmpfile && mv tmpfile "$MARKDOWN_FILE"
else
    # Append new section if not found
    echo -e "\n## Git Fame\n\n$GIT_FAME_OUTPUT" >> "$MARKDOWN_FILE"
fi

echo "Updated '$MARKDOWN_FILE' with Git Fame statistics."

