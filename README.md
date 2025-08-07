# Rebar Manufacturer Dataset Extractor

A simple Python script to extract rebar manufacturer data from various industry sources.

## Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the script:

```bash
python main.py
```

## What it does

- Extracts manufacturer data from:

  - CARES Steel Certification database (https://carescertification.com/certified-companies/search)
  - British Association of Reinforcement (BAR)
  - IREPAS (International Rebar Producers and Exporters Association)
  - Known UK and European manufacturers

- **LinkedIn Integration**: Automatically searches LinkedIn for company contacts in key roles:

  - Finance, Operations, Production, Sustainability
  - Management and Director positions

- Outputs data in both CSV and Excel formats with fields:
  - Company Name
  - Website
  - Address
  - First Name
  - Last Name
  - Email
  - LinkedIn
  - Job Title
  - Source

## Output Files

- `rebar_manufacturers.csv` - CSV format

## Requirements

- Chrome browser installed (for Selenium web scraping)
- ChromeDriver (automatically managed by Selenium)

## Notes

- The script includes advanced web scraping with Selenium for dynamic content
- LinkedIn contact extraction focuses on key management roles
- Email validation is included
- Sample known manufacturers are added for demonstration
- The script generates a summary report of extracted data
- Respectful delays are implemented to avoid overwhelming servers
