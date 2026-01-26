from get_studies import get_urls
import DataExtractor
import time

"""
This is main
"""

if __name__ == "__main__":

    urls = get_urls()
    for url in urls:
        DataExtractor.extract(url)
        # vent litt mellom hver forespørsel
        time.sleep(0.5)
    
