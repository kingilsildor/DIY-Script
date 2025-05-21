#!/bin/bash

# Check if at least one argument (repo URL) is provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 <repo_url1> <repo_url2> ..."
    exit 1
fi

# Counter for team numbers
count=1

# Loop through each repository URL provided as arguments
for repo in "$@"; do
    # Extract the repository name (last part of the URL without .git)
    repo_name=$(basename -s .git "$repo")
    
    # Clone the repository
    git clone "$repo"
    
    # Check if cloning was successful
    if [ $? -eq 0 ]; then
        # Rename the cloned directory to teamN
        mv "$repo_name" "team$count"
        echo "Renamed $repo_name to team$count"
        ((count++))
    else
        echo "Failed to clone $repo"
    fi

done

