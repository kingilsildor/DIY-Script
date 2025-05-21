import os
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

base_url = "https://unosat-ai.web.cern.ch/files/AI20240703MMR/statistics/"
path = os.path.expanduser("~/CLS/2024-2025/Individual_Project/downloaded_files")
os.makedirs(path, exist_ok=True)

response = requests.get(base_url)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
print("Connected!")

links = [link["href"] for link in soup.find_all("a", href=True) if not link["href"].endswith("/")]

for link in tqdm(links, desc="Downloading Files", unit="file"):
    file_url = urljoin(base_url, link)
    filename = os.path.join(path, link)

    with requests.get(file_url, stream=True) as file_response:
        file_response.raise_for_status()
        with open(filename, "wb") as file_out:
            for chunk in file_response.iter_content(chunk_size=8192):
                file_out.write(chunk)
