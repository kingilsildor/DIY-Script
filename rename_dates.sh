#!/usr/bin/env bash

shopt -s nullglob

for file in *; do
    if [[ "$file" =~ ([0-3][0-9])-([0-1][0-9])-([0-9]{4}) ]]; then
        day="${BASH_REMATCH[1]}"
        month="${BASH_REMATCH[2]}"
        year="${BASH_REMATCH[3]}"

        new_date="${year}-${month}-${day}"
        new_file="${file/${BASH_REMATCH[0]}/$new_date}"

        if [[ "$file" != "$new_file" ]]; then
            if [[ -e "$new_file" ]]; then
                echo "Skipping '$file' → '$new_file' (target exists)"
            else
                mv -- "$file" "$new_file"
                echo "Renamed '$file' → '$new_file'"
            fi
        fi
    fi
done

