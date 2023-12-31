#!/usr/bin/env python
import os
import pprint
from typing import Optional

from bs4 import BeautifulSoup
from parse_ingredients import parse_ingredient

from crawlers.utils.fda import ingredient_to_nutrients_infos
from recipes.models import Recipe, RecipeCategory, Ingredient
from ny_times import NYTimes


def interleaved_get_recipes():
    crawlers = [
        # Epicurious(),
        # AllRecipes(),
        # BonAppetit(),
        # AsEasyAsApplePie(),
        NYTimes(),
        # FoodNetwork(),
        # MarthaStewart(),
    ]

    next_recipes = [crawler.next_recipe() for crawler in crawlers]
    while len(next_recipes) > 0:
        for next_recipe in next_recipes:
            try:
                recipe, url = next_recipe.__next__()
                yield recipe, url
            except StopIteration:
                next_recipes = [f for f in next_recipes if f != next_recipe]
                break


def _parse_categories(data):
    s = data.get("recipeCategory", "")
    categories = []
    for c in s.split(", "):
        try:
            RecipeCategory[c]
        except KeyError:
            continue
        categories.append(RecipeCategory[c])
    return categories


def _parse_servings(data):
    servings = data.get("recipeYield", "1").lower()
    servings = servings.strip()
    words = servings.split(" ")
    numbers = []
    for word in words:
        try:
            numbers.append(int(word))
        except:
            pass
    if len(numbers) == 0:
        return None
    return int(sum(numbers)/len(numbers))


def _parse_minutes(data):
    s = data.get("totalTime")
    if s is None:
        return None
    s = s.lstrip("PDT")

    d = 0
    if "D" in s:
        parts = s.split("D")
        d = parts[0]
        s = parts[1]

    if "H" in s:
        parts = s.split("H")
        h = parts[0]
        m = parts[1].rstrip("M")
        if m == "":
            m = 0
        try:
            return int(d)*60*24 + int(h)*60 + int(m)
        except:
            return None

    if "M" in s:
        s = s.rstrip("M")
        try:
            return int(s)
        except:
            return None


def _parse_ingredients(data):
    ingredient_strings = data.get("recipeIngredient", data.get("recipeIngredients"))
    if ingredient_strings is None:
        return None
    ingredients = []
    for ingredient_string in ingredient_strings:
        ingredient_string = ingredient_string.lower()
        ingredient_string = ingredient_string.split(",")[0]
        ingredient_string = ingredient_string.split("and")[0]
        for bad_word in ["optional", "plus more", "plus", "to taste", "(", ")"]:
            ingredient_string = ingredient_string.replace(bad_word, "")
        if "</" in ingredient_string:
            soup = BeautifulSoup(ingredient_string, 'html.parser')
            ingredient_string = soup.get_text()
        ingredient_string = ingredient_string.strip()

        ingredient_string = ingredient_string.replace("pinch", "a 1/4tsp")
        while "  " in ingredient_string:
            ingredient_string = ingredient_string.replace("  ", " ")


        is_a_seasoning = False
        seasonings = ["lemon", "parsely", "spray", "leaves", "ice", "salt", "pepper", "sugar", "cinnamon", "nutmeg", "cumin", "paprika", "chili powder", "chili flakes", "chili", "chile", "chiles", "chilies", "chili pepper", "chili peppers", "chile pepper", "chile peppers", "chili paste", "chile paste", "chili sauce", "chile sauce", "chili powder", "chile powder", "chili flakes", "chile flakes", "chili oil", "chile oil", "chili sauce", "chile sauce", "chili paste", "chile paste", "chili powder", "chile powder", "chili flakes", "chile flakes", "chili oil", "chile oil", "chili sauce", "chile sauce", "chili paste", "chile paste", "chili powder", "chile powder", "chili flakes", "chile flakes", "chili oil", "chile oil", "chili sauce", "chile sauce", "chili paste", "chile paste", "chili powder", "chile powder", "chili flakes", "chile flakes", "chili oil", "chile oil", "chili sauce", "chile sauce", "chili paste", "chile paste", "chili powder", "chile powder", "chili flakes", "chile flakes", "chili oil", "chile oil", "chili sauce", "chile sauce", "chili paste", "chile paste", "chili powder", "chile powder", "chili flakes", "chile flakes", "chili oil", "chile oil", "chili sauce", "chile sauce", "chili paste", "chile paste", "chili powder", "chile powder", "chili flakes", "chile flakes", "chili oil", "chile oil", "chili sauce", "chile sauce", "chili paste", "chile paste"]
        for seasoning in seasonings:
            if seasoning in ingredient_string:
                is_a_seasoning = True
                break
        if is_a_seasoning:
            continue

        try:
            parsed_ingredient = parse_ingredient(ingredient_string)
        except Exception as e:
            print(f"failed to parse: '{ingredient_string}'")
            continue

        # @dataclass
        # class Ingredient:
        #     name: str
        #     quantity: int
        #     unit: str
        #     comment: str
        #     original_string: str
        nutrients_infos = []


        ingredient = Ingredient(
            name=parsed_ingredient.name,
            amount=parsed_ingredient.quantity,
            unit=parsed_ingredient.unit,
            comment=parsed_ingredient.comment,
            nutrition_infos=nutrients_infos,
        )
        ingredients.append(ingredient)
    return ingredients


def _parse_instructions(data):
    instructions = data.get("recipeInstructions")
    if instructions is None:
        return None

    if isinstance(instructions[0], dict):
        return [inst["text"] for inst in instructions]

    return instructions


def _parse_notes(data):
    notes = data.get("recipeNotes")
    if notes is None:
        return []
    return notes



def create_recipe(data, url) -> Optional[Recipe]:
    if data is None:
        return None
    if data.get("@type", "") != "Recipe":
        return None

    ingredients = _parse_ingredients(data)
    if ingredients is None:
        return None

    total_nutrition_infos = []
    for ingredient in ingredients:
        ingredient.nutrition_infos = ingredient_to_nutrients_infos(ingredient)
        total_nutrition_infos += ingredient.nutrition_infos

    try:

        recipe = Recipe(
            name=data.get("name", ""),
            categories=_parse_categories(data),
            servings=_parse_servings(data),
            minutes=_parse_minutes(data),

            source_url=url,
            image_urls=data.get("image", []),
            ingredients=ingredients,
            instructions=_parse_instructions(data),
            notes=_parse_notes(data),
            nutrition_infos=total_nutrition_infos,
        )
    except Exception as e:
        pprint.pprint(data)
        print(e)
        return None

    return recipe


def recipes_generator():
    for head_recipe, url in interleaved_get_recipes():
        if head_recipe is None:
            continue

        recipe = create_recipe(head_recipe, url)
        yield recipe


def save_recipe(recipe: Recipe):
    current_dir = os.path.dirname(os.path.realpath(__file__))
    filepath = os.path.join(current_dir, f"../recipes/data/{recipe.name}.json")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w") as f:
        f.write(recipe.model_dump_json(indent=2))


def crawl():
    print("starting crawl")
    i = 0
    for recipe in recipes_generator():
        if recipe is None:
            continue
        print(f"{i}\t{recipe.source_url}\t recipe:{recipe.name}")
        save_recipe(recipe)
        i += 1



if __name__ == "__main__":
    crawl()
