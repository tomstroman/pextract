import requests
from bs4 import BeautifulSoup
import re
import csv

url = "http://physicseducation.net/talks/contributed.php"
response = requests.get(url)
html_content = response.text

soup = BeautifulSoup(html_content, "html.parser")

outer_table = soup.find_all("table")[7] # the first 7 tables are header/navigation

nested_tables = outer_table.find("tr").find("td").find_all("table")


data = []
DESCRIPTION = re.compile(
    r"(?P<num>\d+)\.\s?(?P<authors>.*), ?<span class=\"title\">(?P<title>.*)</span>(?:,\s*)?(?P<desc>.*)(?:\s*</p>)"
)
field_names = None
for nt in nested_tables:
    rows = nt.find_all("tr")
    for row in rows:
        # These table rows have variable numbers of cells, so some creativity is warranted
        # Can't do this: description, res1, res2, res3, res4 = row.find_all("td")
        # Instead:
        row_data = [None, None, None, None, None]
        for index, cell in enumerate(row.find_all("td")):
            row_data[index] = cell
        description, res1, res2, res3, res4 = row_data

        td = re.sub(r"\s+", " ", description.decode_contents())
        match = DESCRIPTION.search(td)
        if not match:
            print(f"No match for {td=}")
            continue

        output_data = {
            "visibleID": match.group("num"),
            "authorOverride": match.group("authors"),
            "title": match.group("title"),
            "description": match.group("desc"),
        }

        for key, res in {"res1": res1, "res2": res2, "res3": res3, "res4": res4}.items():
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
        
            if url is not None:
                if url.startswith("../"):
                    url = url[3:]
                elif not url.startswith("http"):
                    url = f"talks/{url}"

            if img.startswith("/"):
                img = img[1:]
            elif img.startswith("../"):
                img = img[3:]

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
    with open("contributed_data.csv", "w", encoding="utf-8") as outcsv:
        writer = csv.DictWriter(outcsv, field_names, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        writer.writerows(data)


