import json

from bs4 import BeautifulSoup


def get_schema_data(soup: BeautifulSoup):
    script_tags = soup.find_all("script", {"type": "application/ld+json"})
    schema_datas = []
    for script_tag in script_tags:
        try:
            schema_datas = json.loads(script_tag.text.replace("\u2009", " "))
        except Exception as e:
            continue
    if type(schema_datas) != list:
        schema_datas = [schema_datas]
    for schema_data in schema_datas:
        schema_type = schema_data.get("@type", "wrong")
        if schema_type == ["Recipe"]:
            schema_data["@type"] = "Recipe"
        if schema_data.get("@type") == "Recipe":
            yield schema_data
