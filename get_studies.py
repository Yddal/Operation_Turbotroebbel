from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import time
import json

BASE_URL = "https://fagskolen-viken.no"
APPENT_FOR_OPPTAK = "f[0]=apent_for_opptak%3A1&"
buffer_file = r"studies_urls.json"

"""
leser ut alle nettside linkene til studiene ved fagskolen
"""

def get_urls(use_buffer:bool = False, only_available_studies:bool=True):
    # les url fra buffer
    if use_buffer:
        with open(buffer_file, "r") as file:
            urls = json.loads(file.read())
        return urls
    # hent linker fra nettside og lagre i buffer
    else:
        urls = scrape_urls(only_available_studies)
        with open(buffer_file, "w") as file:
            file.write(json.dumps(urls))
        return urls


def scrape_urls(only_available_studies:bool) -> list:

    # studiene er listet over flere sider, så inkrementer sidetall til alt er lest ut
    page = 0
    urls = []
    while True:

        # send
        url = f"{BASE_URL}/studier?{APPENT_FOR_OPPTAK if only_available_studies else ""}page={page}"
        req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(req).read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(html, "lxml")

        # hent ut alle studier
        results = soup.find_all("a", class_="study-guide__link", href=True)

        # gå ut av loop når det ikke er nye resultater
        if not results:
            break

        # legg linker i listen
        for link in results:
            urls.append(BASE_URL + link['href'])

        page += 1

        # vent litt mellom hver forespørsel
        time.sleep(0.5)

    return urls

if __name__ == "__main__":
    urls = get_urls(use_buffer=True)
    print(f"Fagskolen tilbyr {len(urls)} forskejellige studier")
    print(f"{len(urls)} linker funnet")
    for url in urls:
        print(url)