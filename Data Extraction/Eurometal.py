import requests
from bs4 import BeautifulSoup
import pandas as pd
from ftfy import fix_text

URLS = [
    "https://eurometal.net/members/regular-federation-members/",
    "https://eurometal.net/members/multi-product-proximity-steel-stockholding-distribution/",
    "https://eurometal.net/members/international-steel-trade-associations-companies/",
    "https://eurometal.net/members/flat-ssc-distribution/",
    "https://eurometal.net/members/eurometal-associate-members/",
]

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/115.0.0.0 Safari/537.36"
    )
}

data = []

for url in URLS:
    print(f"Fetching {url}...")
    response = requests.get(url, headers=headers)
    response.encoding = "utf-8"
    try:
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    containers = soup.find_all("div", class_="elementor-widget-container")
    if len(containers) < 2:
        print(f"Warning: Not enough containers found in {url}")
        continue
    # Target the SECOND occurrence of the container
    container = containers[1]
    paragraphs = container.find_all("p")

    for p in paragraphs:
        strong = p.find("strong")
        link = p.find("a")
        if strong and link:
            raw_name = strong.get_text(strip=True).split("–")[0].strip()
            name = fix_text(raw_name)
            domain = (
                link.get("href")
                .replace("http://", "")
                .replace("https://", "")
                .strip("/")
            )
            data.append({"Company Name": name, "Domain": domain})  # Removed Source URL

# Save to CSV
df = pd.DataFrame(data)
df.to_csv("Company Data/Eurometal_Members.csv", index=False, encoding="utf-8")
print(f"\n Done—with {len(df)} total entries across all categories!")
