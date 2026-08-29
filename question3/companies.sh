#!/usr/bin/env bash

# =============================================================================
# Question 3: S&P 500 Companies Data Processing Script
# =============================================================================
# Usage:
#   ./companies.sh "<DATASET_URL>"
#
# The script:
#   1. Accepts the CSV URL as a command-line argument.
#   2. Downloads the CSV using curl or wget.
#   3. Extracts company name, headquarters location, and founding year.
#   4. Sorts the records by founding year.
#   5. Displays the results in a readable format.
# =============================================================================

set -e

# -----------------------------------------------------------------------------
# 1. Validate command-line argument
# -----------------------------------------------------------------------------

if [ "$#" -ne 1 ]; then
    echo "Error: CSV dataset URL is required." >&2
    echo "Usage: $0 <DATASET_URL>" >&2
    exit 1
fi

DATASET_URL="$1"

# -----------------------------------------------------------------------------
# 2. Create temporary file and clean it up when the script exits
# -----------------------------------------------------------------------------

CSV_TEMP=$(mktemp)
trap 'rm -f "$CSV_TEMP"' EXIT

# -----------------------------------------------------------------------------
# 3. Download the CSV dataset
# -----------------------------------------------------------------------------

if command -v curl >/dev/null 2>&1; then
    if ! curl -fsSL "$DATASET_URL" -o "$CSV_TEMP"; then
        echo "Error: Failed to retrieve dataset." >&2
        echo "URL: $DATASET_URL" >&2
        exit 1
    fi

elif command -v wget >/dev/null 2>&1; then
    if ! wget -qO "$CSV_TEMP" "$DATASET_URL"; then
        echo "Error: Failed to retrieve dataset." >&2
        echo "URL: $DATASET_URL" >&2
        exit 1
    fi

else
    echo "Error: Neither curl nor wget is available." >&2
    exit 1
fi

# -----------------------------------------------------------------------------
# 4. Verify that the downloaded file is not empty
# -----------------------------------------------------------------------------

if [ ! -s "$CSV_TEMP" ]; then
    echo "Error: Retrieved dataset is empty." >&2
    exit 1
fi

# -----------------------------------------------------------------------------
# 5. Process the CSV
#
# The dataset columns are:
#   1 - Symbol
#   2 - Security
#   3 - GICS Sector
#   4 - GICS Sub-Industry
#   5 - Headquarters Location
#   6 - Date added
#   7 - CIK
#   8 - Founded
#
# Python's csv module is used because it correctly handles CSV fields
# containing commas inside quotation marks.
# -----------------------------------------------------------------------------

python3 - "$CSV_TEMP" << 'PYTHON'
import csv
import re
import sys

csv_file = sys.argv[1]

records = []

try:
    with open(csv_file, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        required_columns = {
            "Security",
            "Headquarters Location",
            "Founded"
        }

        if not required_columns.issubset(reader.fieldnames or []):
            print("Error: Required CSV columns are missing.", file=sys.stderr)
            sys.exit(1)

        for row in reader:
            company = row["Security"].strip()
            location = row["Headquarters Location"].strip()
            founded = row["Founded"].strip()

            if not company:
                continue

            # Extract the first four-digit year.
            match = re.search(r"\b(1[6-9]\d{2}|20\d{2})\b", founded)

            if match:
                founding_year = int(match.group(1))
            else:
                # Put records without a valid year at the end.
                founding_year = None

            records.append(
                (founding_year, company, location)
            )

except (OSError, csv.Error) as error:
    print(f"Error processing CSV: {error}", file=sys.stderr)
    sys.exit(1)

# Sort by founding year in ascending order.
# Records without a founding year are placed at the end.
records.sort(
    key=lambda record: (
        record[0] is None,
        record[0] if record[0] is not None else 0,
        record[1].lower()
    )
)

print()
print("S&P 500 Companies - Sorted by Founding Year")
print("=" * 100)
print(
    f"{'Founding Year':<15} | "
    f"{'Company Name':<40} | "
    f"Headquarters Location"
)
print("-" * 100)

for founding_year, company, location in records:
    year = str(founding_year) if founding_year is not None else "N/A"

    print(
        f"{year:<15} | "
        f"{company:<40} | "
        f"{location}"
    )

print("-" * 100)
print(f"Total Companies Processed: {len(records)}")
