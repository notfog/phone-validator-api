import cloudscraper
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://temp-number.com/"

def get_countries():
    scraper = cloudscraper.create_scraper()
    resp = scraper.get(BASE_URL)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    countries = []
    for link in soup.select('a.country-link[href^="countries/"]'):
        country_url = urljoin(BASE_URL, link['href'])
        country_name_elem = link.select_one('h4.card-title')
        if country_name_elem:
            country_name = country_name_elem.text.strip()
            countries.append({"name": country_name, "url": country_url})
    return countries

def get_all_phone_numbers(country_url):
    scraper = cloudscraper.create_scraper()
    page = 1
    all_numbers = []

    while True:
        url = country_url
        if page > 1:
            url = country_url.rstrip('/') + f'/{page}'
        resp = scraper.get(url)
        if resp.status_code != 200:
            print(f"Stopping pagination: got status {resp.status_code} on page {page}")
            break
        soup = BeautifulSoup(resp.text, "html.parser")
        phone_numbers = []
        for card in soup.select('div.country-box a.country-link[href^="/temporary-numbers/"]'):
            number_elem = card.select_one('h4.card-title')
            if not number_elem:
                continue
            number = number_elem.text.strip()
            href = urljoin(BASE_URL, card['href'])
            time_elem = card.find_previous('div', class_='time-tex-wrap')
            timestamp = time_elem.select_one('div.add_time-top').text.strip() if time_elem else "Unknown"
            phone_numbers.append({"number": number, "url": href, "timestamp": timestamp})

        if not phone_numbers:
            print(f"No phone numbers found on page {page}. Stopping.")
            break

        all_numbers.extend(phone_numbers)
        print(f"Page {page}: Found {len(phone_numbers)} phone numbers")
        page += 1

    return all_numbers

def save_numbers_to_txt(numbers, filename="phone_numbers.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("phone_numbers = [\n")
        for num in numbers:
            f.write(f'    "{num["number"]}",\n')
        f.write("]\n")
    print(f"Saved {len(numbers)} numbers to {filename}")



if __name__ == "__main__":
    print("Fetching countries...")
    countries = get_countries()
    all_numbers = []

    for country in countries:
        print(f"\nCountry: {country['name']}")
        print(f"URL: {country['url']}")
        print("Fetching phone numbers (all pages)...")
        numbers = get_all_phone_numbers(country['url'])
        all_numbers.extend(numbers)

    save_numbers_to_txt(all_numbers)
