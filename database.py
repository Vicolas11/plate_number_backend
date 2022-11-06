
from flask import Flask, jsonify, request, redirect
from flask.templating import render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, migrate

app = Flask(__name__)
app.debug = True
 
# adding configuration for using a sqlite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

# Settings for migrations
migrate = Migrate(app, db)

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.String, unique=True, nullable=False)
    platenum = db.Column(db.String, unique=True, nullable=False)
    model = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f"{self.platenum}"
