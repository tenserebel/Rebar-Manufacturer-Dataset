from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv
import re
from ftfy import fix_text
import os

# Setup headless Chrome options
options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")

# Start Chrome WebDriver
driver = webdriver.Chrome(options=options)

# Open main URL
url = "https://carescertification.com/certified-companies/search"
driver.get(url)
wait = WebDriverWait(driver, 10)
time.sleep(2)

# Get total number of pages
soup = BeautifulSoup(driver.page_source, "html.parser")
pagination_buttons = soup.select("button[onclick^='changePage']")
total_pages = max(
    [int(btn["onclick"].split("(")[1].split(")")[0]) for btn in pagination_buttons]
)

# Initialize storage
results = []
seen_pairs = set()
email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

# Loop through each page
for page in range(1, total_pages + 1):
    print(f"Scraping page {page}/{total_pages}")
    driver.execute_script(f"changePage({page})")
    time.sleep(2)

    company_buttons = driver.find_elements(
        By.CSS_SELECTOR, "h2.accordion-header button.accordion-button"
    )

    for index, button in enumerate(company_buttons):
        try:
            raw_name = button.text.strip().split(",")[0]
            company_name = fix_text(raw_name)
            print(f"{company_name}")

            # Click and wait for the associated content to open
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(0.5)
            button.click()
            time.sleep(1)

            # Find the closest associated expanded content
            parent = button.find_element(
                By.XPATH, "./ancestor::div[contains(@class, 'accordion-item')]"
            )
            expanded_section = parent.find_element(
                By.CSS_SELECTOR, "div.accordion-collapse"
            )

            html = expanded_section.get_attribute("innerHTML")
            emails = re.findall(email_regex, html)

            for email in set(emails):  # De-dupe at email level per section
                domain = email.split("@")[-1].lower()
                key = (company_name, domain, email)
                if key not in seen_pairs:
                    seen_pairs.add(key)
                    results.append(
                        {
                            "Company Name": company_name,
                            "Email Domain": domain,
                            "Email": email,
                        }
                    )

        except Exception as e:
            print(f"Error processing entry {index}: {e}")

# Create output directory if it doesn't exist
output_dir = "./Company Data"
os.makedirs(output_dir, exist_ok=True)

# Save to CSV
csv_filename = os.path.join(output_dir, "Cares_UK_Member.csv")
with open(csv_filename, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Company Name", "Email Domain", "Email"])
    writer.writeheader()
    writer.writerows(results)

# Close the driver
driver.quit()

# Done
print(
    f"\nScraping complete. Data saved to '{csv_filename}' with {len(results)} unique entries."
)
