import requests
import requests_cache
import math
from api_key import API_KEY

requests_cache.install_cache(cache_name='spoonacular_cache', backend='sqlite', expire_after=3600)
PER_PAGE = 12
OFFSET = 12

class Spoonacular:

    def get_recipes(self, page):
        offset = int(page) * OFFSET
        url = f"https://api.spoonacular.com/recipes/complexSearch?cuisine=vietnamese&number={PER_PAGE}&apiKey={API_KEY}&offset={offset}"
        response = requests.get(url)
        return response

    def get_recipes_by_ids(self, ids):
        string_ids = ','.join(map(str, ids)) 
        url = f"https://api.spoonacular.com/recipes/informationBulk/?ids={string_ids}&apiKey={API_KEY}"
        response = requests.get(url)
        return response


    def get_recipe(self, id):
        url = f"https://api.spoonacular.com/recipes/{id}/information?includeNutrition=true&apiKey={API_KEY}"
        response = requests.get(url)
        return response

    def num_of_pages(self, total_recipes):
        # print(total_recipes, OFFSET)
        # print(total_recipes / OFFSET)
        # print(math.floor(total_recipes / OFFSET))
        return math.floor(total_recipes / OFFSET)

    def search(self, query, query_type, page):
        offset = int(page) * OFFSET
        url = f"https://api.spoonacular.com/recipes/complexSearch?{query_type}={query}&cuisine=vietnamese&number={PER_PAGE}&apiKey={API_KEY}&offset={offset}"
        response = requests.get(url)
        return response