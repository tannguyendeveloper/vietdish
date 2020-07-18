import os
import requests
import math
from api_key import GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET


from flask import Flask, render_template, session, request, make_response, jsonify, url_for, redirect
from authlib.integrations.flask_client import OAuth
from sqlalchemy.sql import func

from spoonacular import Spoonacular, OFFSET
from recipe import Recipe
from models import db, connect_db, Review, User, Favorite

app = Flask(__name__)
app.config['ENV'] = 'development'
# app.config['DEBUG'] = True
# app.config['TESTING'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'vietdishsecret')

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL','postgresql:///vietdish_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)

# Google OAuth
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    client_kwargs={'scope': 'openid profile email'}
)

spoonacularConnection = Spoonacular()

@app.route('/')
def root():
    """ Renders the homepage """
    response = spoonacularConnection.get_recipes('1')
    if response.status_code == 200:
        response_json = response.json()
        recipes = response_json.get('results', [])
        recipe_ids = Recipe.filter_ids(recipes)
        reviews = Review.get_recipe_reviews_count_grouped_by_ids(recipe_ids)
        pages = spoonacularConnection.num_of_pages(response_json.get('totalResults'))
        base_url = '/page/'
        return render_template(
            'list-recipes.html',
            recipes = recipes,
            page = 1,
            pages = pages,
            base_url = base_url,
            args = {},
            session = session,
            reviews=reviews
        )
    else:
        return render_template('error.html', session = session)


@app.route('/page/<page>')
def page(page):
    """ Renders page of recipes """
    response = spoonacularConnection.get_recipes(str(page))
    if response.status_code == 200:
        response_json = response.json()
        recipes = response_json.get('results', [])
        recipe_ids = Recipe.filter_ids(recipes)
        reviews = Review.get_recipe_reviews_count_grouped_by_ids(recipe_ids)
        pages = spoonacularConnection.num_of_pages(response_json.get('totalResults'))
        base_url = '/page/'
        return render_template(
            'list-recipes.html',
            recipes = recipes,
            page = page,
            pages = pages,
            base_url = base_url,
            args = {},
            session = session,
            reviews=reviews
        )
    else:
        return render_template('error.html', session = session)

@app.route('/search/')
def search():
    """ Renders search results """
    query = request.args.get('query')
    query_type = request.args.get('query_type')
    page = request.args.get('page', 1)
    response = spoonacularConnection.search(query, query_type, page)
    if response.status_code == 200:
        response_json = response.json()
        recipes = response_json.get('results', [])
        recipe_ids = Recipe.filter_ids(recipes)
        reviews = Review.get_recipe_reviews_count_grouped_by_ids(recipe_ids)
        pages = spoonacularConnection.num_of_pages(response_json.get('totalResults'))
        base_url = f'/search/?query={query}&query_type={query_type}&page='
        return render_template(
            'list-recipes.html', 
            recipes = recipes,
            page = page,
            pages = pages,
            base_url = base_url,
            args = request.args,
            session = session,
            reviews=reviews
        )
    else:
        return render_template('error.html', session = session)

@app.route('/recipes/<id>')
def recipe(id):
    """ Renders recipe """
    recipe_id = int(id)
    response = spoonacularConnection.get_recipe(recipe_id)
    if response.status_code == 200:
        recipe = Recipe(response.json())
        reviews = Review.get_recipe_reviews_count_grouped_by_ids([recipe_id])
        user_id = session['user']['id'] if session.get('user') else False
        user_has_reviewed_recipe = Review.if_user_has_review(user_id, recipe_id) if user_id and recipe_id else False
        return render_template(
            'recipe.html',
            recipe = recipe,
            session = session,
            reviews = reviews,
            user_review = user_has_reviewed_recipe
        )
    else:
        return render_template('error.html', session = session)

@app.route('/recipes/<id>/print')
def recipe_print(id):
    """ Renders printable recipe """
    response = spoonacularConnection.get_recipe(id)
    if response.status_code == 200:
        recipe = Recipe(response.json())
        return render_template('print-recipe.html', recipe = recipe)
    else:
        return render_template('error.html', session = session)

@app.errorhandler(404)
def handle_404(self):
    return render_template('error_404.html', session = session)


#### API Routes ####


@app.route('/favorites/', methods=['GET'])
def favorites():
    """ Renders users favorites page """
    try:
        user_id = session['user']['id']
    except:
        return redirect('/')

    user_id = session['user']['id']
    page = int(request.args.get('page', 1))
    base_url = '/favorites/?page='

    favorites = Favorite.query.filter_by(user_id=user_id).all()
    all_recipe_ids = Favorite.filter_recipe_ids(favorites)

    pages = math.ceil(len(all_recipe_ids) / OFFSET) if len(all_recipe_ids) > 0 else 1

    if page == 1:
        offset_end = (OFFSET * page)
        recipe_ids = all_recipe_ids[0:offset_end]
    elif page > 1:
        offset_begin = (page - 1) * OFFSET - 1
        offset_end = (OFFSET * page)
        recipe_ids = all_recipe_ids[offset_begin:offset_end]

    response = spoonacularConnection.get_recipes_by_ids(recipe_ids)
    if response.status_code == 200:
        favorite_recipes = response.json() if recipe_ids and len(recipe_ids) > 0 else []
        
        reviews = Review.get_recipe_reviews_count_grouped_by_ids(recipe_ids)
        return render_template('list-favorites.html', 
            session = session,
            title='Favorites',
            base_url = base_url,
            args = {},
            pages = pages,
            page = page,
            recipes = favorite_recipes,
            favorites = all_recipe_ids,
            reviews = reviews
        )
    else:
        return render_template('error.html', session = session)

@app.route('/api/favorites/', methods = ['POST'])
def toggle_favorite():
    """ Add a user favorite """
    try:
        authenticated_user_id = User.is_current_user_authenticated()
        recipe_id = request.json.get('recipe_id')
        existing_favorite = Favorite.query.filter_by(user_id=authenticated_user_id, recipe_id=recipe_id).first()
        # add if a favorite with the same user_id and recipe_id doesn't exist
        if authenticated_user_id and recipe_id and not existing_favorite:
            new_favorite = Favorite(user_id=authenticated_user_id, recipe_id=recipe_id)
            db.session.add(new_favorite)
            db.session.commit()
            db.session.flush()
            session['favorites'].append(int(recipe_id))
            session.modified = True
            return make_response(jsonify({'data': True, 'message': 'Favorite added.'}), 200)

        # remove favorite if it already exists
        elif authenticated_user_id and recipe_id and existing_favorite:
            Favorite.query.filter_by(user_id=authenticated_user_id, recipe_id=recipe_id).delete()
            db.session.commit()
            db.session.flush()
            session['favorites'].remove(int(recipe_id))
            session.modified = True
            return make_response(jsonify({'data': False, 'message': 'Favorite removed'}), 200)

        else:
            return make_response(jsonify({'data': False, 'message': 'Missing required data'}), 400)
    except:
        return make_response(jsonify({'message': 'User not logged in'}), 400)

@app.route('/api/reviews/', methods = ['POST'])
def add_review():
    """ Add a user review for a recipe """
    try:
        authenticated_user_id = User.is_current_user_authenticated()
        user_id = session['user']['id']
        recipe_id = request.json.get('recipe_id')
        rating = request.json.get('rating')
        review_text = request.json.get('review_text')

        existing_review = Review.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
        if user_id == authenticated_user_id and recipe_id and review_text and not existing_review:
            new_review = Review(user_id=user_id, recipe_id=recipe_id, rating=rating, review_text=review_text)
            db.session.add(new_review)
            db.session.commit()
            db.session.rollback()
            return make_response(jsonify(
                {'data': {
                    'id': new_review.id,
                    'user_id': user_id,
                    'recipe_id': recipe_id,
                    'rating': rating,
                    'review_text': review_text
                    },
                'message': 'Review added successfully.'}), 200)

        # update review if it already exists
        elif user_id == authenticated_user_id and recipe_id and review_text and existing_review:
            existing_review.rating = rating
            existing_review.review_text = review_text
            db.session.add(existing_review)
            db.session.commit()
            db.session.rollback()
            return make_response(jsonify(
                {'review': {
                    'id': existing_review.id,
                    'user_id': user_id,
                    'recipe_id': recipe_id,
                    'rating': rating,
                    'review_text': review_text
                    },
                'message': 'Review updated.'}), 200)
        else:
            return make_response(jsonify({'data': False, 'message': 'Missing required data.'}), 400)
    except:
        return make_response(jsonify({'data': False, 'message': 'User not logged in.'}), 400)


@app.route('/api/reviews/<recipe_id>/', methods = ['GET'])
def get_reviews(recipe_id):
    """ Get reviews by recipe id """
    if not request.args.get('count') == 'true' and not request.args.get('current_user') == 'true':
        args = dict(request.args)
        args['recipe_id'] = recipe_id
        reviews = Review.get_recipe_reviews(args)
        if reviews:
            return make_response(jsonify(reviews), 200)
        else:
            return make_response(jsonify({'data': False, 'message': 'No reviews found.'}), 200)
    elif request.args.get('current_user') == 'true' and not request.args.get('count'):
        user_id = session['user']['id']
        review = Review.get_user_review(user_id, recipe_id)
        return make_response(jsonify({'data': review }), 200)
    else:
        reviews = Review.get_recipe_reviews_count_grouped_by_ids([int(recipe_id)])
        if reviews and reviews[int(recipe_id)]:
            return make_response(jsonify({'data': reviews[int(recipe_id)] if reviews[int(recipe_id)] else False }), 200)
        else:
            return make_response(jsonify({'data': False, 'message': 'No reviews found.' }), 200)

### User Sign In, Auhorize, Logout routes ###

@app.route('/login')
def login():
    """ renders the login page """
    for key in list(session.keys()):
        session.pop(key)
    google = oauth.create_client('google')
    redirect_uri = url_for('authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    """ renders the authorization page """
    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()

    ### Check the database for a user by id ##
    user = User.query.get(user_info['id'])

    # if the user does not resist
    if not User.query.get(user_info['id']):
        ### Add the user to the database
        user = User(id=user_info['id'], name=user_info['name'], email=user_info['email'], picture=user_info['picture'])
        db.session.add(user)
        db.session.commit()
    
    session['token'] = token
    session['user'] = user_info
    session['favorites']  = Favorite.filter_recipe_ids(user.favorites)
    db.session.rollback()
    # Save the user to the session

    return redirect('/')

@app.route('/authenticate', methods = ['GET'])
def authenticate_current_user():
    """ Check if the current user session is authenticated, returns the a json object """
    user_id = User.is_current_user_authenticated()
    return make_response(jsonify({'authenticated': bool(user_id), 'user': user_id if user_id else ''}), 200 if user_id else 400)

@app.route('/logout')
def logout():
    """ logout the user """
    for key in list(session.keys()):
        session.pop(key)
    return redirect('/')
