import requests
import time

from flask import Flask, render_template, session, request, make_response, jsonify, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import DateTime
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.sql import func

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
        return f"<Review id={self.id} user={self.user} recipe_id={self.recipe_id} rating={self.rating} date={self.created_date}>"

    @staticmethod
    def get_recipe_reviews(args):
        order_by = Review.date_created if args.get('order_by') == 'date' else Review.rating
        if args.get('rating') == 'all':
            ratings_query = Review.query.filter(Review.recipe_id == args.get('recipe_id')).order_by(order_by).all()
        else:
            ratings_query = Review.query.filter(Review.recipe_id == args.get('recipe_id')).filter(Review.rating == args.get('rating')).order_by(order_by).all()
        return True

    @staticmethod
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
        ratings_query = (map(Review.convert_review_count_list_to_dict, ratings_query))
        ratings = {}
        for rating in ratings_query:
            ratings[rating['id']] = dict(rating['data'])
        print(ratings)
        return ratings

    @staticmethod
    def convert_review_count_list_to_dict(ratings_list):
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

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    recipe_id = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(255), db.ForeignKey('users.id'))
    date = db.Column(DateTime(timezone=True), server_default=func.now())
    user = db.relationship('User', backref='favorites')

