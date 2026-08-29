import urllib.parse
import requests
from bs4 import BeautifulSoup


def scrape_mdcomputers(search_term: str):
    """
    Fetch and parse search results from MDComputers.
    """

    # CHANGED: Use the base URL format given in the assignment
    base_url = "https://mdcomputers.in/"

    params = {
        "route": "product/search",
        "search": search_term
    }

    # CHANGED: Build the search URL dynamically
    search_url = f"{base_url}?{urllib.parse.urlencode(params)}"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    print(f"Searching MDComputers for: '{search_term}'")
    print(f"URL: {search_url}\n")

    try:
        response = requests.get(
            search_url,
            headers=headers,
            timeout=15
        )
        response.raise_for_status()

    except requests.RequestException as error:
        print(f"Error fetching search results: {error}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    product_cards = soup.select(".product-grid-item")

    if not product_cards:
        print(f"No products found for search term: '{search_term}'")
        return

    results = []

    for card in product_cards:

        # Extract product name
        title_element = (
            card.select_one(".product-entities-title a")
            or card.select_one(".product-entities-title")
        )

        title = (
            title_element.get_text(strip=True)
            if title_element
            else "N/A"
        )

        # Extract selling price
        price_element = card.select_one(".price")
        selling_price = "N/A"

        if price_element:
            ins_element = (
                price_element.select_one("ins")
                or price_element.select_one(".ins")
            )

            if ins_element:
                selling_price = ins_element.get_text(strip=True)

            else:
                del_element = (
                    price_element.select_one("del")
                    or price_element.select_one(".del")
                )

                if del_element:
                    price_text = price_element.get_text(strip=True)
                    del_text = del_element.get_text(strip=True)
                    selling_price = price_text.replace(
                        del_text, ""
                    ).strip()

                else:
                    selling_price = price_element.get_text(
                        strip=True
                    )

        # Normalize whitespace
        selling_price = " ".join(selling_price.split())

        if title != "N/A":
            results.append({
                "name": title,
                "price": selling_price
            })

    if not results:
        print(f"No products found for search term: '{search_term}'")
        return

    print(f"Found {len(results)} product(s):\n")

    print(
        f"{'#':<4} | "
        f"{'Product Name':<75} | "
        f"{'Selling Price'}"
    )

    print("-" * 100)

    for index, product in enumerate(results, start=1):
        print(
            f"{index:<4} | "
            f"{product['name']:<75} | "
            f"{product['price']}"
        )


def main():
    try:
        search_term = input("Enter search term: ").strip()

    except (KeyboardInterrupt, EOFError):
        print("\nOperation cancelled.")
        return

    if not search_term:
        print("Error: Search term cannot be empty.")
        return

    scrape_mdcomputers(search_term)


if __name__ == "__main__":
    main()
