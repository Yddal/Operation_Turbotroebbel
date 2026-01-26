
"""
This is main
"""

import DataExtractor



url = "https://fagskolen-viken.no/studier/ledelse/administrativ-koordinator"
#url = "https://fagskolen-viken.no/studier/ledelse/praktisk-lederutdanning"
#url = "https://fagskolen-viken.no/studier/helse/barsel-og-barnepleie"
DataExtractor.extract(url)
