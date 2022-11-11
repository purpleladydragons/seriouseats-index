import os
import requests
import logging

def fetch_calories(ingredient: str, quantity: str) -> int:
    """
    Given an ingredient like "2 tbsp butter", determine the calories

    :param ingredient: str representing ingredient and quantity
    :return: number of calories in ingredient
    """

    ingredient = quantity + ' ' + ingredient

    url = 'https://api.edamam.com/api/food-database/v2/parser'
    params = {
        'app_id': '6fabbd61',
        'app_key': os.environ['EDAMAM_API_KEY'],
        'ingr': ingredient,
    }
    resp = requests.get(url, params)
    if resp.status_code > 300:
        logging.warning('failed request', resp.text)
    resp = resp.json()

    parsed_ingredients = []
    try:
        food_id = resp['parsed'][0]['food']['foodId']
        quantity = resp['parsed'][0]['quantity']
        measure = resp['parsed'][0]['measure']['label']
        parsed_ingredients.append((ingredient, quantity, measure, food_id))

        app_id = '6fabbd61'
        app_key = os.environ['EDAMAM_API_KEY']

        url = f'https://api.edamam.com/api/food-database/v2/nutrients?app_id={app_id}&app_key={app_key}'

        for ingredient, quantity, measure, food_id in parsed_ingredients:
            params = {
                'ingredients': [
                    {
                        'quantity': quantity,  # TODO parse number from ingredient span
                        'measureURI': measure,  # TODO parse measure
                        'foodId': food_id
                    }
                ]
            }
            headers = {'Content-type': 'application/json'}
            resp = requests.post(url, json=params, headers=headers)
            calories = resp.json()['calories']
            return calories

    except Exception as e:
        logging.warning(repr(e))
        return 0


