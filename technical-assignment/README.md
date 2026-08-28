# Technical Assignment Solutions

This repository contains solutions for the 3-part technical assignment covering **Web Scraping** (Python), **Database Querying** (MySQL / Rfam DB), and **Data Processing & Shell Scripting** (Unix Bash).

---

## 📁 Repository Structure

```text
technical-assignment/
├── README.md
├── question1/
│   └── scraper.py
├── question2/
│   └── queries.sql
└── question3/
    └── companies.sh
```

---

## 🚀 Question 1 — Web Scraper for MDComputers

### Overview
`question1/scraper.py` is a Python-based web scraper built to search for PC hardware components on [MDComputers.in](https://mdcomputers.in).

### Features
- **Dynamic Search Term**: Accepts search queries directly via command-line arguments or interactive prompt fallback.
- **Dynamic URL Encoding**: Safely constructs search URLs using `urllib.parse.urlencode`.
- **Robust Parsing**: Uses `BeautifulSoup` to extract Product Name and Selling Price (accurately handling sale prices vs. original list prices).
- **Graceful Error Handling**: Manages HTTP request failures, network timeouts, and zero-result search pages cleanly.

### Prerequisites & Dependencies
- Python 3.8+
- `requests`
- `beautifulsoup4`

Install dependencies:
```bash
pip install requests beautifulsoup4
```

### Usage Instructions
Run the scraper by passing a search term as a command-line argument:
```bash
python question1/scraper.py "rtx 4060"
```
Or run interactively:
```bash
python question1/scraper.py
```

---

## 🗄️ Question 2 — SQL Queries for Rfam Database

### Overview
`question2/queries.sql` contains standard SQL queries designed for the public **Rfam MySQL Database** (`family`, `rfamseq`, `full_region`, `taxonomy`, `clan`, `clan_membership`).

### Queries Included
1. **Query A**: Calculates the total count of *Acacia* plant species in the `taxonomy` table (`acacia_types_count = 389`).
2. **Query B**: Identifies the wheat type (*Triticum*) with the longest DNA sequence length from the `rfamseq` and `taxonomy` tables (`Triticum durum (durum wheat)`).
3. **Query C**: Generates a paginated list (Page 9: results 121–135) of RNA families whose maximum sequence length exceeds 1,000,000, using `LIMIT 15 OFFSET 120` sorted in descending order of maximum sequence length.

### Connection Details (Public Rfam Instance)
- **Host**: `mysql-rfam-public.ebi.ac.uk`
- **Port**: `4497`
- **User**: `rfamro`
- **Database**: `Rfam`

### Execution Instruction
To run the queries against the public Rfam server using MySQL CLI:
```bash
mysql -u rfamro -h mysql-rfam-public.ebi.ac.uk -P 4497 Rfam < question2/queries.sql
```

---

## 🐚 Question 3 — S&P 500 Companies Shell Script

### Overview
`question3/companies.sh` is a Unix shell script that automates the retrieval and processing of S&P 500 company datasets provided via a CSV URL.

### Features
- **URL Argument Validation**: Verifies that a dataset URL is passed at runtime; displays usage guidelines and exits with code `1` on missing inputs.
- **Data Fetching**: Supports both `curl` and `wget` to retrieve remote CSV files cleanly, exiting with code `1` on network or retrieval failures.
- **Dynamic Field Parsing**: Extracts **Company Name**, **Headquarters Location**, and **Founding Year** even when field orders vary or fields contain quoted commas.
- **Numerical Sorting**: Extracts 4-digit founding years and sorts all company records in **descending** chronological order.
- **Error Handling**: Gracefully handles network failures, HTTP errors, and empty datasets.

### Prerequisites
- Unix-like environment (Linux, macOS, Git Bash, or WSL)
- Standard utilities: `bash`, `curl` or `wget`, `python3` / `python`

### Usage Instructions
Make the script executable:
```bash
chmod +x question3/companies.sh
```

Run with a valid S&P 500 CSV dataset URL:
```bash
./question3/companies.sh "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
```

---

## 📊 Summary of Verification & Testing

| Question | Component | Verification Status | Notes |
|---|---|---|---|
| **Question 1** | `question1/scraper.py` | ✅ Verified | Successfully tested scraping live search terms (`rtx 4060`, `monitor`, `ram`). |
| **Question 2** | `question2/queries.sql` | ✅ Verified | Queries A (`389`), B (`Triticum durum`), and C (`OFFSET 120`) verified against Rfam DB. |
| **Question 3** | `question3/companies.sh` | ✅ Verified | Tested dataset fetching, header parsing, descending numerical sorting (503 companies), and error handling (`exit 1`). |
