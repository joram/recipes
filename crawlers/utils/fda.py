import json
import os
from typing import List, Optional

from dotenv import load_dotenv

from crawlers.utils.caching import get_cached
from models import NutritionalInfo, Ingredient

load_dotenv()


api_key = os.environ.get("FDA_API_KEY")


def _get_cached_fda_info_for_ingredient(ingredient: Ingredient, page=1) -> Optional[dict]:
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?api_key={api_key}&query={ingredient.name}&pageSize=1&page={page}"
    cache_url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={ingredient.name}&pageSize=1&page={page}"

    if "/" in ingredient.name:
        return None

    content = get_cached(url, cache_url)
    try:
        data = json.loads(content)
    except:
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


def ingredient_to_nutrients_infos(ingredient: Ingredient) -> List[NutritionalInfo]:
    data = {}
    good_data = False
    page = 0
    while not good_data:
        page += 1
        data = _get_cached_fda_info_for_ingredient(ingredient, page)
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
