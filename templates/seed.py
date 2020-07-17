from models import db
from aoo import app

db.drop_all()
db.create_all()