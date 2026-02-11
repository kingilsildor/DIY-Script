import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import json
import unicodedata


def normalize_first_char(text):
    """Normalize Unicode characters to their ASCII equivalents for categorization."""
    if not text:
        return None

    first_char = text[0]

    # Check if it's a digit
    if first_char.isdigit():
        return "numbers"

    # Normalize Unicode character (e.g., é -> e, ñ -> n, ø -> o)
    normalized = unicodedata.normalize("NFD", first_char)
    # Remove combining characters (accents, etc.)
    ascii_char = "".join(c for c in normalized if unicodedata.category(c) != "Mn")

    # If we have an ASCII letter, return it uppercase
    if ascii_char and ascii_char.isalpha():
        return ascii_char.upper()

    # If normalization didn't work, try direct letter check
    if first_char.isalpha():
        return first_char.upper()

    return None


def scrape_genres(url):
    # Fetch the webpage
    response = requests.get(url)
    response.raise_for_status()

    # Parse HTML
    soup = BeautifulSoup(response.text, "html.parser")

    # Dictionary to store genres by first letter
    genres_by_letter = defaultdict(list)

    # Find all <tr valign="top"> elements
    rows = soup.find_all("tr", valign="top")

    for row in rows:
        # Find <span class="note"> within each row
        note_span = row.find("span", class_="note")
        if note_span:
            # Find <a> tag within the span
            link = note_span.find("a")
            if link:
                genre = link.get_text(strip=True)
                if genre:
                    category = normalize_first_char(genre)
                    if category:
                        genres_by_letter[category].append(genre)

    # Convert defaultdict to regular dict and sort by keys
    result = {k: genres_by_letter[k] for k in sorted(genres_by_letter.keys())}

    return result


if __name__ == "__main__":
    url = "https://everynoise.com/thesoundofeverything.html"

    try:
        genres = scrape_genres(url)

        # Write to JSON file with proper Unicode characters
        output_file = "genres.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(genres, f, indent=2, ensure_ascii=True)

        print(f"Genres saved to {output_file}")
        print(f"Total letters: {len(genres)}")
        print(f"Total genres: {sum(len(v) for v in genres.values())}")

    except Exception as e:
        print(f"Error: {e}")
