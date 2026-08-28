#!/usr/bin/env bash

# =============================================================================
# Question 3: S&P 500 Companies Data Processing Script
# =============================================================================
# Accepts a CSV dataset URL as a command-line argument, retrieves the CSV data,
# extracts Company Name, Headquarters Location, and Founding Year, sorts the
# records by Founding Year in DESCENDING order, and displays the result in a clean table.
#
# Requirements satisfied:
# - Command-line URL argument validation
# - Data retrieval via curl / wget with error handling
# - CSV header processing and field extraction
# - Numerical sorting by Founding Year (descending)
# - Clean, formatted table output
# Usage:
#   ./companies.sh <DATASET_URL>
# =============================================================================

set -e

# 1. Handle missing URL argument
if [ -z "$1" ]; then
    echo "Error: Missing CSV dataset URL argument." >&2
    echo "Usage: $0 <DATASET_URL>" >&2
    exit 1
fi

DATASET_URL="$1"

# 2. Retrieve dataset using curl or wget
CSV_TEMP=$(mktemp)
trap 'rm -f "$CSV_TEMP"' EXIT

if command -v curl >/dev/null 2>&1; then
    curl -sSL "$DATASET_URL" -o "$CSV_TEMP" || true
elif command -v wget >/dev/null 2>&1; then
    wget -qO "$CSV_TEMP" "$DATASET_URL" || true
else
    echo "Error: Neither curl nor wget is available." >&2
    exit 1
fi

# 3. Handle failure to retrieve dataset or empty file
if [ ! -s "$CSV_TEMP" ]; then
    echo "Error: Failed to retrieve dataset or retrieved dataset is empty." >&2
    echo "URL: $DATASET_URL" >&2
    exit 1
fi

# Determine python command
PYTHON_CMD="python"
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
fi

# 4. Parse CSV, extract Company Name, Location & Founding Year, sort by year descending, and print
$PYTHON_CMD - "$CSV_TEMP" "$DATASET_URL" << 'EOF'
import sys
import csv
import re

csv_path = sys.argv[1]
dataset_url = sys.argv[2]

try:
    with open(csv_path, 'r', encoding='utf-8-sig', errors='replace') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        
        if not header:
            print("Error: CSV dataset is empty.", file=sys.stderr)
            sys.exit(1)
            
        # Dynamically locate columns based on common header names
        name_idx = -1
        loc_idx = -1
        founded_idx = -1
        
        for idx, col in enumerate(header):
            c = col.strip().lower()
            if c in ['security', 'company', 'company name', 'name', 'firm']:
                name_idx = idx
            elif c in ['headquarters location', 'location', 'headquarters', 'hq location', 'address']:
                loc_idx = idx
            elif c in ['founded', 'founding year', 'year founded', 'date founded', 'established']:
                founded_idx = idx
                
        # Default column index fallbacks
        if name_idx == -1:
            name_idx = 1 if len(header) > 1 else 0
        if loc_idx == -1:
            loc_idx = 4 if len(header) > 4 else (1 if len(header) > 1 else 0)
        if founded_idx == -1:
            founded_idx = len(header) - 1

        records = []
        for row in reader:
            if not row or len(row) <= max(name_idx, loc_idx, founded_idx):
                continue
                
            company = row[name_idx].strip()
            location = row[loc_idx].strip()
            raw_founded = row[founded_idx].strip()
            
            # Extract 4-digit founding year
            year_match = re.search(r'\b(16|17|18|19|20)\d{2}\b', raw_founded)
            if year_match:
                year_num = int(year_match.group(0))
                year_str = str(year_num)
            else:
                year_num = 9999
                year_str = raw_founded if raw_founded else 'N/A'
                
            if company:
                records.append((year_num, year_str, company, location))
                
        # Sort records by founding year in DESCENDING order (latest year first, N/A at bottom)
        records.sort(key=lambda x: (-x[0] if x[0] != 9999 else -999999, x[2]))
        
        print("=" * 100)
        print("S&P 500 Companies Analysis - Sorted by Founding Year (Descending)")
        print(f"Dataset URL: {dataset_url}")
        print("=" * 100)
        print(f"{'Founding Year':<15} | {'Company Name':<45} | {'Headquarters Location'}")
        print("-" * 100)
        
        for rec in records:
            y_disp = rec[1] if rec[0] != 9999 else 'N/A'
            print(f"{y_disp:<15} | {rec[2]:<45} | {rec[3]}")
            
        print(f"\nTotal Companies Processed: {len(records)}")

except Exception as e:
    print(f"Error processing CSV data: {e}", file=sys.stderr)
    sys.exit(1)
EOF
