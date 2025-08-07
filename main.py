import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv

# Load Serper API key
load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

# Config: roles to search for
roles = [
    "Finance Director",
    "Operations Manager",
    "Head of Production",
    "Sustainability",
]

results = []


def is_current_employee(snippet: str, company: str) -> bool:
    """Check if the LinkedIn snippet shows current employment at the company."""
    if not snippet:
        return False
    snippet_lower = snippet.lower()
    company_lower = company.lower()

    # Exclude if these terms appear
    bad_terms = ["former", "ex-", "previously at", "worked at", "past employee"]
    if any(term in snippet_lower for term in bad_terms):
        return False

    # Include if clearly current
    good_terms = [
        f"currently at {company_lower}",
        "currently",
        "present",
        f"at {company_lower}",
        f"{company_lower}",
    ]
    return any(term in snippet_lower for term in good_terms)


def split_name(full_name: str):
    parts = full_name.strip().split()
    if len(parts) >= 2:
        return parts[0], " ".join(parts[1:])
    return parts[0], ""


def generate_email_guesses(first_name, last_name, domain):
    first = first_name.lower()
    last = last_name.lower()
    f = first[0]
    return [
        f"{first}.{last}@{domain}",
        f"{f}.{last}@{domain}",
        f"{first}@{domain}",
        f"{last}@{domain}",
        f"{first}{last}@{domain}",
        f"{f}{last}@{domain}",
    ]


input_file = "Company Data\\Bar_UK_Members.csv"  # Your input CSV
try:
    companies_df = pd.read_csv(input_file)
except Exception as e:
    print(f"Failed to read '{input_file}': {e}")
    exit()

headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}


for _, row in companies_df.iterrows():
    company_name = str(row["Company Name"]).strip()
    domain = str(row["Email Domain"]).strip()
    company_email = str(row.get("Email", "")).strip()  # <- Get company contact email

    for role in roles:
        query = f'site:linkedin.com/in "{role}" "{company_name}"'
        body = {"q": query, "num": 10}

        print(f"Searching: {role} at {company_name}")
        response = requests.post(
            "https://google.serper.dev/search", headers=headers, json=body
        )

        if response.status_code != 200:
            print(f"Error {response.status_code} - {response.text}")
            continue

        data = response.json()
        organic = data.get("organic", [])

        for item in organic:
            title = item.get("title", "")
            link = item.get("link", "")
            snippet = item.get("snippet", "")

            if "linkedin.com/in/" not in link:
                continue
            if not is_current_employee(snippet, company_name):
                continue

            full_name = title.split(" - ")[0].strip()
            first_name, last_name = split_name(full_name)
            email_guesses = generate_email_guesses(first_name, last_name, domain)

            results.append(
                {
                    "Company": company_name,
                    "Company Contact Email": company_email,
                    "First Name": first_name,
                    "Last Name": last_name,
                    "Role (Search Term)": role,
                    "Role (From Title)": title,
                    "LinkedIn URL": link,
                    "Email Guesses": ", ".join(email_guesses),
                }
            )

        time.sleep(1.5)

# Save results
df = pd.DataFrame(results)
output_file = "Rebar Manufacturers.csv"
df.to_csv(output_file, index=False)
print(f"✅ Done! Saved {len(df)} contacts to '{output_file}'")
