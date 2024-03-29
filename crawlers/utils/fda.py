import json
import os
import time
from typing import List, Optional

from dotenv import load_dotenv

from crawlers.utils.caching import get_cached, get_cached_request
from recipes.models import NutritionalInfo, Ingredient

load_dotenv()


api_key = os.environ.get("FDA_API_KEY")


def _get_cached_fda_info_for_ingredient(ingredient: Ingredient, page=1) -> Optional[dict]:
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={ingredient.name}&pageSize=1&page={page}"
    cache_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={ingredient.name}&pageSize=1&page={page}"

    attempts = 0
    content = None
    while True:
        if attempts >= 3:
            return None
        try:
            content = get_cached_request(url, cache_url)
            break
        except Exception as e:
            attempts += 1
            print("Error getting cached request for url: ", url)
            time.sleep(1)
            continue
    try:
        # for bad in ['<html><head><meta name="color-scheme" content="light dark"></head><body><pre style="word-wrap: break-word; white-space: pre-wrap;">', '</pre></body></html>']:
        #     content = content.replace(bad, "")
        data = json.loads(content)
    except Exception as e:
        print(f"Could not parse json for {url}")
        return None
    return data


def _convert_serving_size_to_grams(value, units):
    if units == "g":
        return value
    if units == "mg":
        return value / 1000
    if units == "kg":
        return value * 1000
    if units == "oz":
        return value * 28.3495
    if units == "lb":
        return value * 453.592
    if units == "fl oz":
        return value * 29.5735
    if units == "cup":
        return value * 236.588
    if units == "tbsp":
        return value * 14.7868
    if units == "tsp":
        return value * 4.92892
    if units == "ml":
        return value * 1

def convert_ingredient_using_golden_file(ingredient_string):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_golden_file.json")
    with open(path) as f:
        content = f.read()
        hard_strings = json.loads(content)
        return hard_strings.get(ingredient_string, ingredient_string)

def add_ingredient_to_test_golden_file(ingredient_string):
    path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_golden_file.json")

    if not os.path.exists(path):
        hard_strings = {}
    else:
        with open(path) as f:
            content = f.read()
            hard_strings = json.loads(content)
    hard_strings[ingredient_string] = ""

    with open(path, "w") as f:
        f.write(json.dumps(hard_strings, indent=2, sort_keys=True))


def ingredient_to_nutrients_infos(ingredient: Ingredient) -> List[NutritionalInfo]:

    # for not_food_words in ["pan", "plate", "1/4 tsp", "1/2 tsp"]:
    #     if not_food_words in ingredient.name:
    #         return []

    data = {}
    good_data = False
    page = 0
    attempts = 0
    while not good_data:
        if attempts >= 3:
            return []

        page += 1
        data = _get_cached_fda_info_for_ingredient(ingredient, page)
        if data is None or "Internal Server Error" in str(data):
            print("Internal Server Error for ingredient: ", ingredient.name, "\t"*5, ingredient.original_string)
            add_ingredient_to_test_golden_file(ingredient.original_string)
            time.sleep(1)
            attempts += 1
            continue

        if data is None:
            return []
        if data["totalHits"] == 0:
            return []
        if "servingSizeUnit" in data["foods"][0]:
            good_data = True
        if page >=3:
            return []

    food = data["foods"][0]


    if food["servingSizeUnit"] != "g":
        food["servingSize"] = _convert_serving_size_to_grams(food["servingSize"], food["servingSizeUnit"])
        food["servingSizeUnit"] = "g"

    if food["servingSizeUnit"] != "g":
        raise ValueError(f"Serving size unit is not g, it is {food['servingSizeUnit']}")

    nutrients = food["foodNutrients"]
    nutrients_infos = []
    for nutrient in nutrients:
        nutrients_infos.append(
            NutritionalInfo(
                name=nutrient["nutrientName"],
                amount=nutrient["value"],
                unit=nutrient["unitName"],
                serving_size=food["servingSize"] or 1,
                serving_size_unit=food["servingSizeUnit"],
            )
        )
    return nutrients_infos
