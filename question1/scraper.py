import sys
import urllib.parse
import requests
from bs4 import BeautifulSoup


def scrape_mdcomputers(search_term: str):
    """
    Dynamically fetches and parses search results from MDComputers for a given search term.
    """
    base_url = "https://mdcomputers.in/index.php"
    params = {
        "route": "product/search",
        "search": search_term
    }
    search_url = f"{base_url}?{urllib.parse.urlencode(params)}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    print(f"Searching MDComputers for: '{search_term}'")
    print(f"URL: {search_url}\n")
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching search results: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    product_cards = soup.select(".product-grid-item")
    
    if not product_cards:
        print(f"No products found for search term: '{search_term}'")
        return

    results = []
    for card in product_cards:
        # Extract product title
        title_elem = card.select_one(".product-entities-title a") or card.select_one(".product-entities-title")
        title = title_elem.get_text(strip=True) if title_elem else "N/A"
        
        # Extract selling price
        price_elem = card.select_one(".price")
        selling_price = "N/A"
        
        if price_elem:
            ins_elem = price_elem.select_one("ins") or price_elem.select_one(".ins")
            if ins_elem:
                selling_price = ins_elem.get_text(strip=True)
            else:
                del_elem = price_elem.select_one("del") or price_elem.select_one(".del")
                if del_elem:
                    price_text = price_elem.get_text(strip=True)
                    del_text = del_elem.get_text(strip=True)
                    selling_price = price_text.replace(del_text, "").strip()
                else:
                    selling_price = price_elem.get_text(strip=True)
        
        # Normalize whitespace
        selling_price = " ".join(selling_price.split())
        
        if title != "N/A":
            results.append({"name": title, "price": selling_price})

    if not results:
        print(f"No products found for search term: '{search_term}'")
        return

    print(f"Found {len(results)} product(s):\n")
    print(f"{'#':<4} | {'Product Name':<75} | {'Selling Price'}")
    print("-" * 100)
    
    for idx, item in enumerate(results, start=1):
        print(f"{idx:<4} | {item['name']:<75} | {item['price']}")


def main():
    # Ensure stdout handles UTF-8 characters (e.g. Rupee symbol ₹) on Windows consoles
    if hasattr(sys.stdout, "reconfigure") and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    if len(sys.argv) > 1:
        search_term = " ".join(sys.argv[1:])
    else:
        try:
            search_term = input("Enter search term: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nOperation cancelled.")
            sys.exit(0)
            
    if not search_term:
        print("Error: Search term cannot be empty.")
        sys.exit(1)
        
    scrape_mdcomputers(search_term)


if __name__ == "__main__":
    main()
