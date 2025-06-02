from bs4 import BeautifulSoup
import re
import time
import requests
import random

def download_latest_news(data):
    latest_links = [re.split("&ved", link)[0] for link in data['link']]

    description = []
    summary_details = []

    for idx, link in enumerate(latest_links):

        try:
            response = requests.get(link, timeout=10)

            if response.status_code == 200:
                html_content = response.text
            else:
                print(
                    f"Failed to retrieve: {link} (Status code: {response.status_code})")
                description.append("Failed to retrieve the webpage.")
                continue

            soup = BeautifulSoup(html_content, "html.parser")
            paragraphs = soup.find_all("p")

            page_description = " ".join([p.get_text() for p in paragraphs])
            description.append(page_description)
            if idx <= 5:
                summary_details.append(page_description)

        except requests.exceptions.RequestException as e:
            print(f"Error retrieving {idx}: {e}")
            description.append("Failed to retrieve the webpage.")
            continue

        time.sleep(random.uniform(1, 3))

    print(description)

    data["description"] = description
    return data
