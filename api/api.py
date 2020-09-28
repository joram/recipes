#!/usr/bin/env python
import json

from flask import request
from flask_cors import CORS
import os

import flask as flask

from utils import load_recipes, load_categories

global recipes
app = flask.Flask(__name__, static_folder='./build')
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/api/v0/recipes')
def recipes_list():
    return flask.jsonify(list(recipes.keys()))


@app.route('/api/v0/recipes/search')
def recipes_search():
    results = {}

    title = request.args.get('title')
    category = request.args.get('category')
    for recipe in recipes.values():
        if category is not None and category in recipe.get("category", []):
            results[recipe.get("title")] = recipe
        elif title is not None and title.lower() in recipe.get("title").lower():
            results[recipe.get("title")] = recipe

    results = list(results.values())
    print(f"{len(results)} recipes found")
    return flask.jsonify(results)


@app.route('/api/v0/meta')
def meta():
    response = {
        "categories": load_categories(),
    }
    return flask.jsonify(response)


@app.route('/api/v0/recipe/<pub_id>')
def recipe(pub_id):
    if pub_id not in recipes:
        return flask.abort(404)
    return flask.jsonify(recipes[pub_id])


# Serve React App
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(app.static_folder + '/' + path):
        return flask.send_from_directory(app.static_folder, path)
    return flask.send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        recipes = load_recipes()
    app.run(host="0.0.0.0", debug=True)
