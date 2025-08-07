import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv
import argparse

# Load API keys from .env
load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
EMAILDETECTIVE_API_KEY = os.getenv("EMAILDETECTIVE_API_KEY")

# Roles to search for
roles = [
    "Finance Director",
    "Operations Manager",
    "Head of Production",
    "Sustainability",
]

results = []


def is_current_employee(snippet: str, company: str) -> bool:
    if not snippet:
        return False
    snippet_lower = snippet.lower()
    company_lower = company.lower()

    bad_terms = ["former", "ex-", "previously at", "worked at", "past employee"]
    if any(term in snippet_lower for term in bad_terms):
        return False

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


def validate_emails_with_emaildetective(emails: list[str]) -> dict:
    url = "https://api.emaildetective.io/emails"
    headers = {
        "Authorization": EMAILDETECTIVE_API_KEY,
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(url, json={"data": emails}, headers=headers)
        response.raise_for_status()
        data = response.json().get("data", [])
        return {entry["email"]: entry for entry in data}
    except Exception as e:
        print(f"❌ EmailDetective API error: {e}")
        return {}


def main():
    parser = argparse.ArgumentParser(description="Process company members CSV.")
    parser.add_argument(
        "input_csv", help="Path to input CSV file with company members data"
    )
    args = parser.parse_args()
    input_file = args.input_csv

    # Read input
    try:
        companies_df = pd.read_csv(input_file)
    except Exception as e:
        print(f"Failed to read '{input_file}': {e}")
        return

    # Shuffle rows randomly
    companies_df = companies_df.sample(frac=1).reset_index(drop=True)

    serper_headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    all_guessed_emails = set()
    email_map = []

    max_contacts = 100
    max_guessed_emails = 100
    total_contacts_found = 0
    total_email_guesses = 0

    for _, row in companies_df.iterrows():
        if (
            total_contacts_found >= max_contacts
            or total_email_guesses >= max_guessed_emails
        ):
            break

        company_name = str(row["Company Name"]).strip()
        domain = str(row["Email Domain"]).strip()
        company_email = str(row.get("Email", "")).strip()

        for role in roles:
            if (
                total_contacts_found >= max_contacts
                or total_email_guesses >= max_guessed_emails
            ):
                break

            query = f'site:linkedin.com/in "{role}" "{company_name}"'
            body = {"q": query, "num": 10}

            response = requests.post(
                "https://google.serper.dev/search", headers=serper_headers, json=body
            )
            if response.status_code != 200:
                print(f"❌ Serper error {response.status_code} - {response.text}")
                continue

            organic = response.json().get("organic", [])

            for item in organic:
                if (
                    total_contacts_found >= max_contacts
                    or total_email_guesses >= max_guessed_emails
                ):
                    break

                title = item.get("title", "")
                link = item.get("link", "")
                snippet = item.get("snippet", "")

                if "linkedin.com/in/" not in link or not is_current_employee(
                    snippet, company_name
                ):
                    continue

                full_name = title.split(" - ")[0].strip()
                first_name, last_name = split_name(full_name)
                guesses = generate_email_guesses(first_name, last_name, domain)

                # Limit email guesses so total stays under cap
                allowed = max(0, max_guessed_emails - total_email_guesses)
                limited_guesses = guesses[:allowed]

                if not limited_guesses:
                    continue

                email_map.append(
                    {
                        "company": company_name,
                        "company_email": company_email,
                        "first_name": first_name,
                        "last_name": last_name,
                        "role_search": role,
                        "role_title": title,
                        "linkedin": link,
                        "email_guesses": limited_guesses,
                    }
                )

                all_guessed_emails.update(limited_guesses)
                total_contacts_found += 1
                total_email_guesses += len(limited_guesses)

            time.sleep(1.5)

    # Validate emails
    print(f"\nValidating {len(all_guessed_emails)} guessed emails...")
    validation_results = validate_emails_with_emaildetective(list(all_guessed_emails))

    # Build final results
    for entry in email_map:
        guessed_email = ""
        validation = {}
        for guess in entry["email_guesses"]:
            v = validation_results.get(guess)
            if v and v.get("valid_email"):
                guessed_email = guess
                validation = v
                break
        if not guessed_email:
            guessed_email = entry["email_guesses"][0]
            validation = validation_results.get(guessed_email, {})

        results.append(
            {
                "Company": entry["company"],
                "Company Contact Email": entry["company_email"],
                "First Name": entry["first_name"],
                "Last Name": entry["last_name"],
                "Role (Search Term)": entry["role_search"],
                "Role (From Title)": entry["role_title"],
                "LinkedIn URL": entry["linkedin"],
                "Guessed Email": guessed_email,
                "Valid Email": validation.get("valid_email", False),
                "Score": validation.get("score", ""),
                "Suspicion Rating": validation.get("suspicion_rating", ""),
                "Similar Email": validation.get("did_you_mean", ""),
            }
        )

    # Export results
    df = pd.DataFrame(results)
    output_file = "Rebar Manufacturers.csv"
    df.to_csv(output_file, index=False)
    print(
        f"\n✅ Done! Saved {len(df)} contacts and {len(all_guessed_emails)} emails to '{output_file}'"
    )


if __name__ == "__main__":
    main()
