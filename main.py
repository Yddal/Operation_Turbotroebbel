from get_studies import get_urls

"""
This is main
"""
if __name__ == "__main__":

    urls = get_urls()
    for url in urls:
        print(url)


