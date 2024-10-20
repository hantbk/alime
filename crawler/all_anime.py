import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import random
from helpers.page_finder import find_max_page

# Constants
BASE_URL = "https://myanimelist.net/topanime.php?limit="
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
}

def get_page_content(page_number):
    retries = 3
    while retries > 0:
        try:
            response = requests.get(BASE_URL + str(page_number), headers=HEADERS, timeout=10)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error retrieving page {page_number // 50 + 1}: {e}")
            retries -= 1
            if retries > 0:
                wait_time = (4 - retries) ** 2
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
    print(f"Failed to retrieve page {page_number // 50 + 1} after 3 attempts")
    return None

def parse_anime_info(anime):
    title_tag = anime.find("h3", class_="anime_ranking_h3")
    title = title_tag.get_text(strip=True)
    anime_url = title_tag.find("a")["href"]
    anime_id = re.search(r"/anime/(\d+)/", anime_url).group(1)

    info_div = anime.find("div", class_="information di-ib mt4")
    if info_div:
        info_list = list(info_div.stripped_strings)
        type_eps = info_list[0] if info_list else "N/A"
        type_eps_match = re.match(r"(\w+)(?:\s*\((\d+)\s*eps\))?", type_eps)
        anime_type = type_eps_match.group(1) if type_eps_match else "N/A"
        episodes = type_eps_match.group(2) if type_eps_match and type_eps_match.group(2) else "N/A"

        aired_dates = info_list[1] if len(info_list) > 1 else "N/A"
        dates = re.findall(r"(\w{3}\s+\d{4})", aired_dates)
        aired_start = dates[0] if dates else "N/A"
        aired_end = dates[1] if len(dates) > 1 else "N/A"

        members_info = info_list[2] if len(info_list) > 2 else "N/A"
        members_match = re.search(r"([\d,]+)\s*members", members_info)
        members = members_match.group(1).replace(",", "") if members_match else "N/A"
    else:
        anime_type, episodes, aired_start, aired_end, members = "N/A", "N/A", "N/A", "N/A", "N/A"

    score_tag = anime.find("span", class_="score-label")
    score = score_tag.get_text(strip=True) if score_tag else "N/A"

    return [anime_id, title, anime_type, episodes, aired_start, aired_end, members, score]

def scrape_myanimelist(max_anime):
    with open("../data/all_anime.csv", mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([
            "AnimeID", "Title", "Type", "Episodes", "Aired Start", "Aired End", "Members", "Score",
        ])

        for i in range(0, max_anime + 50, 50):
            content = get_page_content(i)
            if content:
                soup = BeautifulSoup(content, "html.parser")
                anime_list = soup.find_all("tr", class_="ranking-list")
                for anime in anime_list:
                    anime_info = parse_anime_info(anime)
                    writer.writerow(anime_info)
                print(f"Successfully scraped page {i // 50 + 1}")
            time.sleep(random.uniform(1, 3))

def main():
    max_anime = find_max_page(BASE_URL, HEADERS)
    print(f"Maximum number of anime found: {max_anime}")
    scrape_myanimelist(max_anime)
    print("Data successfully written to 'all_anime.csv'")

if __name__ == "__main__":
    main()