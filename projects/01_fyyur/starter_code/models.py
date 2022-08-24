# -----------------------------------------------------------------
# imports
# ----------------------------------------------------------------
from datetime import datetime
from email.policy import default
from time import timezone
from flask import Flask
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
import config

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class Venue(db.Model):
    __tablename__ = "venues"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=True)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(150))
    shows = db.relationship(
        "Show", backref="venues", lazy=True, cascade="all, delete-orphan"
    )

    def venue_details(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "address": self.address,
            "genres": self.genres,
            "phone": self.phone,
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website_link": self.website_link,
            "seeking_artist": self.seeking_artist,
            "seeking_description": self.seeking_description,
        }

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = "artists"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    genres = db.Column(db.String(120), nullable=False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(150))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(200), nullable=False)
    shows = db.relationship(
        "Show", backref="artists", lazy=True, cascade="all, delete-orphan"
    )

    def artist_info(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "state": self.state,
            "phone": self.phone,
            "genres": self.genres,
            "image_link": self.image_link,
            "facebook_link": self.facebook_link,
            "website_link": self.website_link,
            "seeking_venue": self.seeking_venue,
            "seeking_description": self.seeking_description,
        }

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Show(db.Model):
    __tablename__ = "shows"
    id = db.Column(db.Integer, primary_key=True)
    start_time = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
    artist_id = db.Column(db.Integer, db.ForeignKey(Artist.id), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(Venue.id), nullable=False)

    def show_details(self):
        return {
            "id": self.id,
            "start_time": self.start_time,
            "artist_id": self.artist_id,
            "venue_id": self.venue_id,
        }

    def artist_info(self):
        return {
            "artist_id": self.venue_id,
            "artist_name": self.Artist.name,
            "artist_image_link": self.Artist.image_link,
            "start_time": self.start_time,
        }

    def show_info(self):
        return {
            "venue_id": self.venue_id,
            "venue_name": self.Venue.name,
            "artist_id": self.artist_id,
            "artist_name": self.Artist.name,
            "artist_image_link": self.Artist.image_link,
            "start_time": self.start_time,
        }

    def venue_info(self):
        return {
            "venue_id": self.venue_id,
            #'venue_name' :self.Venue.name,
            #'venue_image_link' :self.Venue.image_link,
            "start_time": self.start_time,
        }


# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
