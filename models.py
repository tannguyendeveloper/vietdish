import requests
import time
import datetime

from flask import Flask, render_template, session, request, make_response, jsonify, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func, desc

db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

## Models
class User(db.Model):
    __tablename__ = 'users'
    def __repr__(self):
        return f"<User id={self.id} name={self.name} email={self.email}>"

    @staticmethod
    def is_current_user_authenticated():
        try:
            token = session.get('token')
            expiration = token.get('expires_at')
            current_time = time.time()
            if current_time > expiration:
                raise Exception(make_response(jsonify({'user': False,'message': 'Session expired'}), 00))
            url = f"https://oauth2.googleapis.com/tokeninfo?id_token={token.get('id_token')}"
            response = requests.get(url)
            user_id = response.json().get('sub')
            return user_id if response.status_code == 200 else False
        except:
            return False


    id = db.Column(db.String(255), primary_key=True, unique=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    picture = db.Column(db.String(255), nullable=False, unique=True)
    date_created = db.Column(DateTime(timezone=True), server_default=func.now())


class Review(db.Model):
    __tablename__ = 'reviews'
    def __repr__(self):
        return f"<Review id={self.id} user={self.user} recipe_id={self.recipe_id} rating={self.rating} review_text={self.review_text} date_created={self.date_created} date_updated={self.date_updated}>"

    @staticmethod
    def get_recipe_reviews(args):
        page = int(args.get('page',1))
        order_by = Review.date_created.desc() if args.get('order_by') == 'date' else Review.rating.desc()
        if args.get('rating') == 'all':
            reviews_query = Review.query.filter(Review.recipe_id == args.get('recipe_id')).order_by(order_by).paginate(page=page, max_per_page=20, error_out=False)
        else:
            reviews_query = Review.query.filter(
                Review.recipe_id == args.get('recipe_id'),
                Review.rating == args.get('rating')
            ).order_by(order_by).paginate(page=page, max_per_page=20, error_out=False)
        if len(reviews_query.items) > 0:
            reviews = Review.map_reviews_to_dict(reviews_query.items)
            response = {
                'recipe_id': args.get('recipe_id'),
                'rating': args.get('rating'),
                'order_by': args.get('order_by'),
                'total_reviews': reviews_query.total,
                'reviews': reviews,
                'current_page': reviews_query.page,
                'next': reviews_query.page + 1 if reviews_query.has_next else False,
                'pages': reviews_query.pages,
            }
        else:
            response = False
        return response

    @staticmethod
    def map_reviews_to_dict(reviews_list):
        reviews = []
        for review in reviews_list:
            reviews.append(Review.translate_review_to_dict(review))
        return reviews

    @staticmethod
    def translate_review_to_dict(review):
        return dict({
            'id': review.id,
            'user': {
                'id': review.user.id,
                'name': review.user.name,
                'picture': review.user.picture
            },
            'rating': review.rating,
            'review_text': review.review_text,
            'date_created': review.date_created.strftime("%B %d, %Y"),
            'date_updated': review.date_updated.strftime("%B %d, %Y") if review.date_updated else False
        })

    @staticmethod
    def get_recipe_reviews_count_grouped_by_ids(recipe_ids):
        reviews_query = db.session.query(
            (Review.recipe_id),
            func.avg(Review.rating),
            func.count(Review.recipe_id),
            func.count(Review.rating).filter(Review.rating == 1),
            func.count(Review.rating).filter(Review.rating == 2),
            func.count(Review.rating).filter(Review.rating == 3),
            func.count(Review.rating).filter(Review.rating == 4),
            func.count(Review.rating).filter(Review.rating == 5)
        ).group_by(
            Review.recipe_id
        ).filter(
            Review.recipe_id.in_(recipe_ids)
        ).all()

        reviews_query = (map(Review.map_review_count_list_to_dict, reviews_query))
        ratings = {}
        for rating in reviews_query:
            ratings[rating['id']] = dict(rating['data'])
        return ratings

    @staticmethod
    def map_review_count_list_to_dict(ratings_list):
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

    @staticmethod
    def user_has_review(user_id, recipe_id):
        try:
            reviews_query = Review.query.filter(
                Review.user_id == user_id,
                Review.recipe_id == recipe_id
            ).first()
            return bool(reviews_query.id)
        except:
            return False

    @staticmethod
    def get_user_review(user_id, recipe_id):
        try:
            review = Review.query.filter(
                Review.user_id == user_id,
                Review.recipe_id == recipe_id
            ).first()
            return Review.translate_review_to_dict(review) if review.id else None
        except:
            return None


    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey('users.id'))
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.String(1000), nullable=False)
    date_created = db.Column(DateTime(timezone=True), server_default=func.now())
    date_updated = db.Column(DateTime(timezone=True), onupdate=func.now())
    user = db.relationship('User', backref='reviews')


class Favorite(db.Model):
    __tablename__ = 'favorites'
    def __repr__(self):
        return f"<Favorite id={self.id} user={self.user} recipe_id={self.user_id}>"

    @staticmethod
    def filter_recipe_ids(favorites):
        return [favorite.__dict__.get('recipe_id') for favorite in favorites]

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey('users.id'))
    date = db.Column(DateTime(timezone=True), server_default=func.now())
    user = db.relationship('User', backref='favorites')

