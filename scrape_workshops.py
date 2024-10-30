import requests
from bs4 import BeautifulSoup
import re

url = "http://physicseducation.net/workshops/index.php"
response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, "html.parser")

outer_table = soup.find_all("table")[7] # the first 7 tables are header/navigation
nested_table = outer_table.find("tr").find("td").find("table")

data = []
DESCRIPTION = re.compile(
    r"(?P<num>\d+)\.\s?(?P<authors>.*), <span class=\"title\">(?P<title>.*)</span>(?:,\s*)?(?P<desc>.*)(?:\s*</p>)"
)
for row in nested_table.find_all("tr"):
    # These table rows have variable numbers of cells, so some creativity is warranted
    # Can't do this: description, res1, res2, res3 = row.find_all("td")
    # Instead:
    row_data = [None, None, None, None]
    for index, cell in enumerate(row.find_all("td")):
        row_data[index] = cell
    description, res1, res2, res3 = row_data

    td = re.sub(r"\s+", " ", description.decode_contents())
    # temporary
    print(DESCRIPTION.findall(td))

    # TODO: 
    # - inspect the three resN cells for hyperlinks and images.
    # - produce CSV

    



