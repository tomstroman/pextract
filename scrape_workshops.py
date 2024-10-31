import requests
from bs4 import BeautifulSoup
import re
import csv

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
field_names = None
for row in nested_table.find_all("tr"):
    # These table rows have variable numbers of cells, so some creativity is warranted
    # Can't do this: description, res1, res2, res3 = row.find_all("td")
    # Instead:
    row_data = [None, None, None, None]
    for index, cell in enumerate(row.find_all("td")):
        row_data[index] = cell
    description, res1, res2, res3 = row_data

    td = re.sub(r"\s+", " ", description.decode_contents())


    match = DESCRIPTION.search(td)
    output_data = {
        "Index": match.group("num"),
        "AuthorOverride": match.group("authors"),
        "Title": match.group("title"),
        "Description": match.group("desc"),
    }

    for key, res in {"res1": res1, "res2": res2, "res3": res3}.items():
        url_key = f"{key}_url"
        target_key = f"{key}_target"
        img_key = f"{key}_img"

        url = None
        target = None
        img = "../images/clear.gif" # a site convention
        if res:
            if (a := res.find("a")):
                url = a.get("href")
                target = a.get("target")
            if (img_tag := res.find("img")):
                img = img_tag.get("src")
    
        output_data.update(
            {
                url_key: url,
                target_key: target,
                img_key: img,
            }
        )

    field_names = list(output_data.keys())
    data.append(output_data)


if field_names is not None:
    with open("workshops_data.csv", "w", encoding="utf-8-sig") as outcsv:
        writer = csv.DictWriter(outcsv, field_names, quoting=csv.QUOTE_NONNUMERIC)
        writer.writerows(data)


