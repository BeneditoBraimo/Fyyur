# ----------------------------------------------------------------------------#
# Imports
# -------------------------------------------------------------------------
import json
from socket import SHUT_WR
import sys
import dateutil.parser
import babel
from flask import (
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for,
    session,
)
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
import config
from models import Artist, Venue, Show, db, app

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

moment = Moment(app)
app.config.from_object("config")

# TODO: connect to a local postgresql database
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

migrate = Migrate(app, db)
# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    system_current_time = datetime.now().strftime("%Y-%m-%d %H:%S:%M")
    venues_data = Venue.query.group_by(Venue.id, Venue.state, Venue.city).all()
    venue_by_state_and_city = ""
    data = []

    # discover information about upcoming shows, city, states and venues
    for venue in venues_data:
        upcoming_shows = Show.query.filter(Show.start_time > system_current_time).all()
        if venue_by_state_and_city == venue.city + venue.state:
            data[len(data) - 1]["venues"].append(
                {
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": len(upcoming_shows),
                }
            )
        else:
            #venue_by_state_and_city == venue.city + venue.state
            data.append(
                {
                    "city": venue.city,
                    "state": venue.state,
                    "venues": [
                        {
                            "id": venue.id,
                            "name": venue.name,
                            "num_upcoming_shows": len(upcoming_shows),
                        }
                    ],
                }
            )

        return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_key = request.form.get("search_term")
    venue_data = Venue.query.filter(Venue.name.ilike('%' + search_key + '%')).all()
    #venue_list = list(map(Venue.shows, venue_data)) 
    response = {
    "count":len(venue_data),
    "data": venue_data,
    }
    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=search_key,
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = Venue.query.filter(Venue.id == venue_id).first()
    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    name = request.form.get("name")
    city = request.form.get("city")
    state = request.form.get("state")
    address = request.form.get("address")
    phone = request.form.get("phone")
    image_link = request.form.get("image_link")
    facebook_link = request.form.get("facebook_link")
    website_link = request.form.get("website_link")
    seeking_artist = request.form.get("seeking_artist")
    seeking_description = request.form.get("seeking_description")
    genres = request.form.get("genres")

    if seeking_artist == "y":
        seeking_artist = True
    else:
        seeking_artist = False
    data = Venue(
        name=name,
        city=city,
        state=state,
        address=address,
        phone=phone,
        image_link=image_link,
        facebook_link=facebook_link,
        website_link=website_link,
        seeking_artist=seeking_artist,
        seeking_description=seeking_description,
        genres=genres,
    )
    try:
        db.session.add(data)
        db.session.commit()
        flash("Venue " + request.form["name"] + " was successfully listed!")
    except:
        db.session.rollback()
        flash("An error occurred. Venue " + data.name + " could not be listed.")
    finally:
        db.session.close()

    # on successful db insert, flash success
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        venue_to_remove = Venue.query.filter(Venue.id == venue_id).all()
        db.session.delete(venue_to_remove)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database
    data = Artist.query.all()
    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_key = request.form.get("search_term")
    artist = Artist.query.filter(Artist.name.ilike(f"%{search_key}%")).all()
    response = {
        "count": len(artist),
        "data": artist,
    }
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=request.form.get("search_term", ""),
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist_data = Artist.query.filter(Artist.id == artist_id).first()
    if artist_data:
        data = Artist.artist_info(artist_data)
        system_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_shows = (
            Show.query.filter(Show.artist_id == artist_id)
            .join(Artist)
            .filter(Show.start_time > system_time)
            .all()
        )
        new_shows_data = list(map(Show.venue_info, new_shows))
        data["upcoming_shows"] = new_shows_data
        data["upcoming_shows_count"] = len(new_shows_data)
        past_shows = (
            Show.query.filter(Show.artist_id == artist_id)
            .join(Artist)
            .filter(Show.start_time <= system_time)
            .all()
        )
        past_shows_data = list(map(Show.venue_info, past_shows))
        data["past_shows_count"] = len(past_shows_data)
    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    artist_data = Artist.query.filter(Artist.id == artist_id).first()
    form = ArtistForm()
    artist = {
        "id": artist_data.id,
        "name": artist_data.name,
        "genres": artist_data.genres,
        "city": artist_data.city,
        "state": artist_data.state,
        "phone": artist_data.phone,  # "326-123-5000",
        "website": artist_data.website_link,
        "facebook_link": artist_data.facebook_link,
        "seeking_venue": artist_data.seeking_venue,
        "seeking_description": artist_data.seeking_description,
        "image_link": artist_data.image_link,
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    artist = Artist.query.filter(Artist.id == artist_id).first()
    try:
        artist.name = request.form.get("name")
        artist.city = request.form.get("city")
        artist.state = request.form.get("state")
        artist.phone = request.form.get("phone")
        artist.genres = request.form.get("genres")
        artist.image_link = request.form.get("image_link")
        artist.facebook_link = request.get("facebook_link")
        artist.website_link = request.form.get("website_link")
        artist.seeking_venue = request.form.get("seeking_venue")
        artist.seeking_description = request.form.get("seeking_description")
        db.session.commit()
    except:
        db.session.rollback()
        flash(f"artist {artist.name} data could not be updated")
    finally:
        db.session.close()
    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    form = VenueForm()
    venue_data = Venue.query.filter(Venue.id == venue_id).first()

    venue = {
        "id": venue_data.id,
        "name": venue_data.name,
        "genres": venue_data.genres,
        "address": venue_data.address,
        "city": venue_data.city,
        "state": venue_data.state,
        "phone": venue_data.phone,
        "website": venue_data.website_link,
        "facebook_link": venue_data.facebook_link,
        "seeking_talent": venue_data.seeking_talent,
        "seeking_description": venue_data.seeking_description,
        "image_link": venue_data.image_link,
    }
    # TODO: populate form with values from venue with ID <venue_id>
    return render_template("forms/edit_venue.html", form=form, venue=venue)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    venue_data = Venue.query.filter(Venue.id == venue_id).first()
    try:
        venue_data.name = request.form.get("name")
        venue_data.genres = request.form.get("genres")
        venue_data.address = request.form.get("address")
        venue_data.city = request.form.get("city")
        venue_data.state = request.form.get("state")
        venue_data.phone = request.form.get("phone")
        venue_data.website_link = request.form.get("website_link")
        venue_data.facebook_link = request.form.get("facebook_link")
        venue_data.seeking_talent = request.form.get("seeking_talent")
        venue_data.seeking_description = request.form.get("seeking_description")
        venue_data.image_link = request.form.get("image_link")

        # save the changes in the database
        db.session.commit()
    except:
        db.session.rollback()
        flash(f"Venue data could not be updated!")
    finally:
        db.session.close()

    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    name = request.form.get("name")
    city = request.form.get("city")
    state = request.form.get("state")
    phone = request.form.get("phone")
    image_link = request.form.get("image_link")
    genres = request.form.get("genres")
    facebook_link = request.form.get("facebook_link")
    website_link = request.form.get("website_link")
    seeking_venue = request.form.get("seeking_venue")
    seeking_description = request.form.get("seeking_description")

    # somehow, the form returns a String from "seeking venue" field
    # this checks if the string returned is 'y' and assigns the seeking_artist to "True"
    if seeking_venue == "y":
        seeking_venue = True
    else:
        seeking_venue = False
    # create artist object
    data = Artist(
        name=name,
        city=city,
        state=state,
        phone=phone,
        genres=genres,
        image_link=image_link,
        facebook_link=facebook_link,
        website_link=website_link,
        seeking_venue=seeking_venue,
        seeking_description=seeking_description,
    )
    try:

        db.session.add(data)
        db.session.commit()
        flash("Artist " + request.form["name"] + " was successfully listed!")
    except:
        db.session.rollback()
        flash("An error occurred. Artist " + data.name + " could not be listed.")
    finally:
        db.session.close()
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = [
        {
            "venue_id": 1,
            "venue_name": "The Musical Hop",
            "artist_id": 4,
            "artist_name": "Guns N Petals",
            "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
            "start_time": "2019-05-21T21:30:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 5,
            "artist_name": "Matt Quevedo",
            "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
            "start_time": "2019-06-15T23:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-01T20:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-08T20:00:00.000Z",
        },
        {
            "venue_id": 3,
            "venue_name": "Park Square Live Music & Coffee",
            "artist_id": 6,
            "artist_name": "The Wild Sax Band",
            "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
            "start_time": "2035-04-15T20:00:00.000Z",
        },
    ]
    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    artist_id = request.form.get("artist_id")
    venue_id = request.form.get("venue_id")
    start_time = request.form.get("start_time")
    start_time = dateutil.parser.parse(start_time)

    show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    try:
        db.session.add(show)
        db.session.commit()
        flash("Show created successfull!")
    except:
        db.session.rollback()
        flash("Show could not be created")
    finally:
        db.session.close()
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.debug = True
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
