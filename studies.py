from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import time

def get_urls():
    base_url = "https://fagskolen-viken.no/"

    page = 0
    urls = []
    while True:


        req = Request(f"{base_url}studier?page={page}", headers={"User-Agent": "Mozilla/5.0"})
        html = urlopen(req).read().decode("utf-8", errors="ignore")
        soup = BeautifulSoup(html, "lxml")

        results = soup.find_all("a", class_="study-guide__link", href=True)

        if not results:
            break

        for link in results:
            urls.append(base_url + link['href'])

        page += 1
        time.sleep(0.5)

    return urls


print(get_urls())