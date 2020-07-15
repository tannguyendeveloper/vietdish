from models import db, connect_db, Review, User, Favorite
from sqlalchemy.sql import func

def get_ids_from_results(results):
    return list(result.get('id') for result in results)

def get_recipe_ids_from_favorites(favorites):
    """ returns the recipe id of a favorite"""
    return list(favorite.__dict__.get('recipe_id') for favorite in favorites)

def get_recipe_reviews_count_grouped_by_ids(recipe_ids):
    ratings_query = db.session.query(
        (Review.recipe_id),
        func.avg(Review.rating),
        func.count(Review.recipe_id),
        func.count(Review.rating).filter(Review.rating == 1),
        func.count(Review.rating).filter(Review.rating == 2),
        func.count(Review.rating).filter(Review.rating == 3),
        func.count(Review.rating).filter(Review.rating == 4),
        func.count(Review.rating).filter(Review.rating == 5))\
        .group_by(Review.recipe_id)\
        .filter(Review.recipe_id.in_(recipe_ids))\
        .all()
    ratings_query = (map(convert_review_list_to_dict, ratings_query))
    ratings = {}
    for rating in ratings_query:
        ratings[rating['id']] = dict(rating['data'])
    print(ratings)
    return ratings

def convert_review_list_to_dict(ratings_list):
    return dict({
        'id': ratings_list[0],
        'data': {
            'avg': round(ratings_list[1],1),
            'count': ratings_list[2],
            'ratings': {
                1: ratings_list[3],
                2: ratings_list[4],
                3: ratings_list[5],
                4: ratings_list[6],
                5: ratings_list[7],
            }
        }
    })