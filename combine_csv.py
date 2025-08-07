import chardet
import os
import pandas as pd


def detect_encoding(file_path, num_bytes=10000):
    """
    Detect the encoding of a file by reading a portion of it.
    """
    with open(file_path, "rb") as f:
        raw_data = f.read(num_bytes)
    result = chardet.detect(raw_data)
    return result["encoding"]


def combine_csv_files():
    """
    Combine all CSV files from the Company Data folder into one unified CSV file.
    """
    company_data_path = "Company Data"
    all_dataframes = []

    csv_files = [
        ("Bar_UK_Members.csv", "Bar UK"),
        ("Cares_UK_Member.csv", "Cares UK"),
        ("Eurofer_Members.csv", "Eurofer"),
        ("Eurometal_Members.csv", "Eurometal"),
    ]

    for filename, source in csv_files:
        file_path = os.path.join(company_data_path, filename)

        if os.path.exists(file_path):
            print(f"Processing {filename}...")

            # Detect file encoding
            encoding = detect_encoding(file_path)
            print(f"Detected encoding for {filename}: {encoding}")

            try:
                df = pd.read_csv(file_path, encoding=encoding)
            except Exception as e:
                print(f"Failed to read {filename} with encoding {encoding}: {e}")
                continue

            # Standardize column names
            if "Name" in df.columns:
                df = df.rename(columns={"Name": "Company Name"})
            if "Domain" in df.columns:
                df = df.rename(columns={"Domain": "Email Domain"})

            if "Company Name" not in df.columns:
                print(f"Warning: {filename} does not have a Company Name column")
                continue

            df["Source"] = source

            if "Email" in df.columns:
                df = df[["Company Name", "Email Domain", "Email", "Source"]]
            else:
                df = df[["Company Name", "Email Domain", "Source"]]
                df["Email"] = ""

            all_dataframes.append(df)
            print(f"  Added {len(df)} records from {filename}")
        else:
            print(f"Warning: {filename} not found")

    if all_dataframes:
        combined_df = pd.concat(all_dataframes, ignore_index=True)
        combined_df = combined_df.drop_duplicates(
            subset=["Company Name", "Email Domain"], keep="first"
        )
        combined_df = combined_df.sort_values("Company Name")

        output_filename = "Combined_Company_Data.csv"
        combined_df.to_csv(output_filename, index=False)

        print(
            f"\nSuccessfully combined {len(combined_df)} unique records into {output_filename}"
        )
        print(f"Records by source:")
        print(combined_df["Source"].value_counts())

        return output_filename
    else:
        print("No CSV files were processed successfully")
        return None


if __name__ == "__main__":
    combine_csv_files()
