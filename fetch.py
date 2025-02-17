#!/usr/bin/env python3

import argparse
import json as json_lib
import os
from pathlib import Path
import re
import requests
import time
from tqdm import tqdm

parser = argparse.ArgumentParser(description="Fetch and save pdfs from an archive.org collection")
parser.add_argument("collection", help="The name of an archive.org collection.")
parser.add_argument("--delay", type=int, default=3, help="How long to sleep between fetches.")

# pub_chicago-daily-tribune

def fetch_identifiers(collection):
    try:
        cached = Path(f"{collection}.json")
        if cached.is_file():
            print(f"Using cached index: {cached}")
            print(f"Delete {cached} if you want to force a re-fetch of the index.")
            with open(cached, 'r') as f:
                json = json_lib.load(f)
        else:
            print(f"Request index for collection: {collection}")
            params = {
                "q": f"collection:{collection}",
                "fl[]": "identifier",
                "rows": "1000000000", # yes, really
                "output": "json",
            }
            response = requests.get("https://archive.org/advancedsearch.php", params=params)
            response.raise_for_status()

            json = response.json()

            print(f"Writing index to cache file: {cached}")
            with open(cached, 'w') as f:
                f.write(response.text)

        return [ doc['identifier'] for doc in json['response']['docs'] ]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")
        return None

def fetch_and_save_link(url, filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get("content-length", 0))
        with tqdm(total=total_size, unit="B", unit_scale=True) as progress:
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=32*1024):
                    progress.update(len(chunk))
                    f.write(chunk)
        print(f"Saved {url} to {filename}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL: {e}")

def main():
    args = parser.parse_args()
    identifiers = fetch_identifiers(args.collection)
    for identifier in identifiers:
        filename = f"{identifier}.pdf"
        link = f"https://archive.org/download/{identifier}/{filename}"

        match = re.search(r'(\d{4})-\d{2}-\d{2}', filename)
        if match and int(match.group(1)) < 1920:
            print(f"Skipping {link}: too old!")
            continue
        
        if os.path.exists(filename):
            print(f"Skipping {link}: already exists!")
            continue

        print(f"Downloading: {link}")
        fetch_and_save_link(link, filename)
        time.sleep(args.delay)

if __name__ == "__main__":
    main()
