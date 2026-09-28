"""
Image scraper for: https://bestellen.fotoxperience.nl/gallery/2562C0306AEF386421C0D607E4786BF5
Requires: selenium, requests, webdriver-manager

Install dependencies:
    pip install selenium requests webdriver-manager
"""

import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    StaleElementReferenceException,
    NoSuchElementException,
)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

# ── Config ────────────────────────────────────────────────────────────────────
URL = "https://bestellen.fotoxperience.nl/gallery/2562C0306AEF386421C0D607E4786BF5"
BASE_URL = "https://bestellen.fotoxperience.nl"
OUTPUT_DIR = "fotoxperience_images"
TOTAL_SLIDES = 76
SLIDE_DELAY = 1.2
# ─────────────────────────────────────────────────────────────────────────────


def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.binary_location = "/usr/sbin/chromium-browser"

    driver_path = ChromeDriverManager(
        driver_version="148.0.7778.96", chrome_type=ChromeType.CHROMIUM
    ).install()

    return webdriver.Chrome(service=Service(driver_path), options=options)


def normalise(path: str) -> str:
    path = path.strip().strip('"').strip("'")
    if path.startswith("http"):
        return path
    if path.startswith("//"):
        return "https:" + path
    if path.startswith("/"):
        return BASE_URL + path
    return path


def collect_urls_from_dom(driver) -> set:
    """Grab all image URLs from the live DOM via JS (no element references stored)."""
    script = """
        const results = new Set();

        // 1. <img> tags
        document.querySelectorAll('img').forEach(el => {
            const src = el.src || el.getAttribute('data-src') || el.getAttribute('data-lazy-src');
            if (src && !src.endsWith('.svg') && !src.endsWith('.png')) results.add(src);
        });

        // 2. background-image in style attributes
        document.querySelectorAll('[style]').forEach(el => {
            const style = el.getAttribute('style') || '';
            const match = style.match(/background-image\\s*:\\s*url\\(["']?([^"')]+)["']?\\)/);
            if (match) results.add(match[1]);
        });

        return Array.from(results);
    """
    raw = driver.execute_script(script)
    return set(raw) if raw else set()


def send_key_safe(driver, key):
    """Send a key to the body element, re-fetching it each time to avoid stale refs."""
    for attempt in range(3):
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            body.send_keys(key)
            return
        except (StaleElementReferenceException, NoSuchElementException):
            time.sleep(0.5)
    # Last resort: use JS to dispatch a keyboard event
    keycode = 39 if key == Keys.ARROW_RIGHT else 37  # right=39, left=37
    driver.execute_script(f"""
        document.dispatchEvent(new KeyboardEvent('keydown', {{keyCode: {keycode}, bubbles: true}}));
    """)


def click_next_safe(driver):
    """Click the Next link, re-fetching it each time to avoid stale refs."""
    selectors = [
        (By.PARTIAL_LINK_TEXT, "Next"),
        (By.CSS_SELECTOR, "a.next"),
        (By.CSS_SELECTOR, "[class*='next']"),
        (By.CSS_SELECTOR, "[aria-label*='Next']"),
    ]
    for by, sel in selectors:
        for attempt in range(3):
            try:
                el = driver.find_element(by, sel)
                try:
                    el.click()
                except Exception:
                    driver.execute_script("arguments[0].click();", el)
                return True
            except (StaleElementReferenceException, NoSuchElementException):
                time.sleep(0.3)
    return False


def advance_slides(driver, direction, count, all_urls, label, use_click=False):
    key = Keys.ARROW_RIGHT if direction == "forward" else Keys.ARROW_LEFT
    for i in range(count):
        if use_click:
            click_next_safe(driver)
        else:
            send_key_safe(driver, key)
        time.sleep(SLIDE_DELAY)
        all_urls.update(collect_urls_from_dom(driver))
        if (i + 1) % 10 == 0:
            print(
                f"    [{label}] Step {i + 1}/{count} — unique URLs so far: {len(all_urls)}"
            )


def scrape_images():
    driver = get_driver()
    all_urls = set()

    try:
        print(f"Loading: {URL}")
        driver.get(URL)
        time.sleep(5)

        # Pass 1: initial snapshot
        all_urls.update(collect_urls_from_dom(driver))
        print(f"  Pass 1 (initial): {len(all_urls)} URL(s)")

        # Pass 2: forward via arrow keys
        print(f"  Pass 2: forward through {TOTAL_SLIDES} slides via arrow keys…")
        advance_slides(driver, "forward", TOTAL_SLIDES, all_urls, "→")
        print(f"  After forward pass: {len(all_urls)} URL(s)")

        # Pass 3: backward via arrow keys
        print(f"  Pass 3: backward through {TOTAL_SLIDES} slides via arrow keys…")
        advance_slides(driver, "backward", TOTAL_SLIDES, all_urls, "←")
        print(f"  After backward pass: {len(all_urls)} URL(s)")

        # Pass 4: if arrow keys didn't work well, try Next link clicks
        if len(all_urls) < TOTAL_SLIDES // 2:
            print(
                f"  Pass 4: only {len(all_urls)} URLs found, trying Next link clicks…"
            )
            driver.get(URL)
            time.sleep(5)
            all_urls.update(collect_urls_from_dom(driver))
            advance_slides(
                driver, "forward", TOTAL_SLIDES, all_urls, "click→", use_click=True
            )
            print(f"  After click pass: {len(all_urls)} URL(s)")

        # Pass 5: extra sweep if still missing images
        if len(all_urls) < TOTAL_SLIDES:
            print(
                f"  Pass 5: still {len(all_urls)}/{TOTAL_SLIDES}, extra forward sweep…"
            )
            advance_slides(driver, "forward", TOTAL_SLIDES, all_urls, "→2")
            print(f"  After extra pass: {len(all_urls)} URL(s)")

    finally:
        driver.quit()

    # Normalise and filter out UI assets
    skip = [
        "logo",
        "icon",
        "svg",
        "swipe",
        "arrow",
        "menu",
        "favicon",
        "thumbnail",
        "thumb",
    ]
    clean = set()
    for u in all_urls:
        u = normalise(u)
        if not any(s in u.lower() for s in skip):
            clean.add(u)

    return sorted(clean)


def download_images(image_urls: list, output_dir: str = OUTPUT_DIR) -> None:
    os.makedirs(output_dir, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0"}
    total = len(image_urls)

    for i, url in enumerate(image_urls, start=1):
        filename = url.split("?")[0].split("/")[-1]
        if not filename or "." not in filename:
            filename = f"image_{i:03d}.jpg"

        filepath = os.path.join(output_dir, f"{i:02d}_{filename}")

        if os.path.exists(filepath):
            print(f"[{i}/{total}] Already exists, skipping: {filename}")
            continue

        try:
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(r.content)
            print(f"[{i}/{total}] ✓ {filename}")
        except requests.RequestException as e:
            print(f"[{i}/{total}] ✗ FAILED: {url} — {e}")


def main():
    image_urls = scrape_images()
    print(f"\nTotal unique images found: {len(image_urls)}")

    if not image_urls:
        print("No images found. Try increasing SLIDE_DELAY.")
        return

    print(f"Downloading to '{OUTPUT_DIR}/'…\n")
    download_images(image_urls)
    print(f"\nDone! Images saved in '{OUTPUT_DIR}/'")


if __name__ == "__main__":
    main()
