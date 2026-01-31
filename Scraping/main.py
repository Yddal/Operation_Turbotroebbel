from get_studies import get_urls
from DataExtractor import extract
from Push2SQL import main
import time
import os

"""
Starter scraping av nettsiden
1. Hent alle linker til studie sider
2. Hent ut all data for hvert studi og lagre dem som json filer
3. Lagrer skrapet data i databasen
"""

if __name__ == "__main__":
    # hent linker
    path = os.path.join(os.path.dirname(__file__))+"\\"
    urls = get_urls(path + r"studies_urls.json", use_buffer=True)
    
    # les ut alle data for studier
    for url in urls:
        extract(url)
        # vent litt mellom hver forespørsel
        time.sleep(1)
    
    # push to database
    main()
