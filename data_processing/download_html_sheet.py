import requests
import csv
from bs4 import BeautifulSoup

def download_pubhtml_sheets(year, link):
    html = requests.get(link).text
    soup = BeautifulSoup(html, "lxml")
    tables = soup.find_all("table")
    index = 0
    for table in tables:
        with open(str(year) + "_sheet_" + str(index) + ".csv", "w") as f:
            wr = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
            wr.writerows([[td.text for td in row.find_all("td")] for row in table.find_all("tr")])
        index = index + 1

    

if __name__ == "__main__":
    download_pubhtml_sheets(2019, "https://docs.google.com/spreadsheets/d/e/2PACX-1vREamImW3yN-q3rio2XIFX497uoIoPprEuSqykuPPP9D9WcMfMJQj0bXcBl1ZGxIcm_tPIuoZPk_GFk/pubhtml")
    download_pubhtml_sheets(2020, "https://docs.google.com/spreadsheets/d/e/2PACX-1vRK1VndO4Dng6TJ2yM8dedF7Bkf0b-VvrK2T5US5Y-YkI-fpxZhNanWWJOdTB-2BrW9eu8o62sGm5_G/pubhtml#")