import os
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

base_url = "https://unosat-ai.web.cern.ch/files/AI20240912THA/statistics/"

os.makedirs("downloaded_files", exist_ok=True)

response = requests.get(base_url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

for link in soup.find_all("a", href=True):
    file_url = urljoin(base_url, link["href"])

    if file_url.endswith("/"):
        continue

    filename = os.path.join("downloaded_files", link["href"])

    with requests.get(file_url, stream=True) as file_response:
        file_response.raise_for_status()
        with open(filename, "wb") as file_out:
            for chunk in file_response.iter_content(chunk_size=8192):
                file_out.write(chunk)
