import requests
from bs4 import BeautifulSoup
import csv
import re

# Define the base URL of the page to scrape
url = "https://myanimelist.net/topanime.php?limit="

# Open a CSV file for writing
with open('anime.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    
    # Write the header row
    writer.writerow(['Title', 'Type', 'Episodes', 'Aired Start', 'Aired End', 'Members', 'Score'])

    # Function to scrape and extract anime details
    def scrape_myanimelist():
        for i in range(0, 1000, 50):  # Iterate through the pages (0, 50, 100,... up to 1000)
            response = requests.get(url + str(i))
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract anime title, type, aired, members, and score
                anime_list = soup.find_all('tr', class_='ranking-list')
                
                for anime in anime_list:
                    title = anime.find('h3', class_='anime_ranking_h3').get_text(strip=True)
                    
                    # Get 'type', 'aired', and 'members' information
                    info_div = anime.find('div', class_='information di-ib mt4')
                    
                    if info_div:
                        info_lines = info_div.stripped_strings
                        info_list = list(info_lines)
                        
                        # Extract type and number of episodes
                        type_eps = info_list[0] if info_list else 'N/A'
                        type_eps_match = re.match(r'(\w+)(?:\s*\((\d+)\s*eps\))?', type_eps)
                        anime_type = type_eps_match.group(1) if type_eps_match else 'N/A'
                        episodes = type_eps_match.group(2) if type_eps_match and type_eps_match.group(2) else 'N/A'
                        
                        # Extract airing dates
                        aired_dates = info_list[1] if len(info_list) > 1 else 'N/A'
                        dates = re.findall(r'(\w{3}\s+\d{4})', aired_dates)
                        aired_start = dates[0] if dates else 'N/A'
                        aired_end = dates[1] if len(dates) > 1 else 'N/A'
                        
                        # Extract number of members
                        members_info = info_list[2] if len(info_list) > 2 else 'N/A'
                        members_match = re.search(r'([\d,]+)\s*members', members_info)
                        members = members_match.group(1).replace(',', '') if members_match else 'N/A'
                    else:
                        anime_type, episodes, aired_start, aired_end, members = 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'
                    
                    # Find score
                    score_tag = anime.find('span', class_='score-label')
                    score = score_tag.get_text(strip=True) if score_tag else 'N/A'
                    
                    # Write the extracted details into the CSV file
                    writer.writerow([title, anime_type, episodes, aired_start, aired_end, members, score])
            else:
                print(f"Failed to retrieve page {i // 50 + 1}, Status code: {response.status_code}")

    # Run the scraping function
    scrape_myanimelist()

print("Data successfully written to 'anime.csv'")
