# ----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from unicodedata import name
import dateutil.parser
import sys
import babel
from datetime import datetime  #new addition  
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from sqlalchemy import or_ 
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db) 

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(120))
    city = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    name = db.Column(db.String)
    phone = db.Column(db.String(120))
    seeking_description = db.Column(db.String)
    seeking_talent = db.Column(db.Boolean, default=False)
    shows = db.relationship('Show', backref='Venue', lazy=True)
    state = db.Column(db.String(120)) 
    website = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(120))
    facebook_link = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    name = db.Column(db.String)
    phone = db.Column(db.String(120))
    seeking_description = db.Column(db.String)
    seeking_venue = db.Column(db.Boolean, default=False)
    shows = db.relationship('Show', backref='Artist', lazy=True)
    state = db.Column(db.String(120))
    website = db.Column(db.String(500)) 

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Show(db.Model): #implementing Show model 
    __tablename__ = 'Show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  alldata=[]
  venuesdata = Venue.query.all()
  for venue in venuesdata: 
    num_shows_upcoming = venue.shows.filter_by(Show.start_time > datetime.now).all()
    data = {}
    cities = []
    for city in alldata: 
     cities = venue.city
     if venue.city != cities: 
      alldata.append({
                'state':venue.state,
                'city':venue.city,
                'venues':[{
                'id': venue.id,
                'name':venue.name,
                'num_shows_upcoming': len(num_shows_upcoming)}]
                })
                      
    else: 
      citylist = cities.index(venue.city)
      venuelabel = {
        'id': venue.id, 
        'name': venue.name, 
        'num_shows_upcoming': len(num_shows_upcoming)
        }
      alldata[citylist]['venues'].append(venuelabel)

  db.session.close()   
  
  return render_template('pages/venues.html', areas=alldata)

@app.route('/venues/search', methods=['POST'])
def search_venues():

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  searchterm = request.form.get('search_term')
  formattedsearch = "%{}%".format(searchterm.lower())
  output= Venue.query.filter(or_(Venue.city.ilike(formattedsearch), Venue.name.ilike(formattedsearch),  Venue.state.ilike(formattedsearch))).all()
  response = {
    'count':len(output),
    'data':output}

  return render_template('pages/search_venues.html', results= response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue_data = {}
  venue = Venue.query.get(venue_id)
  venue_data ['id']= venue.id  
  venue_data['address']= venue.address
  venue_data['city']= venue.city
  venue_data['facebook_link']= venue.facebook_link
  venue_data['genres']= venue.genres
  venue_data['image_link']= venue.image_link
  venue_data['name']= venue.name
  venue_data['phone']= venue.phone
  venue_data['seeking_description']= venue.seeking_description
  venue_data['seeking_talent']= venue.seeking_talent
  venue_data['shows']= venue.shows
  venue_data['state']= venue.state
  venue_data['website']= venue.website
  venue_data['past_shows']= []
  venue_data['upcoming_shows']= []

  for show in venue.shows:
      showdata = {}
      showdata['artist_id'] = show.artist_id
      showdata['artist_image_link'] = show.artist.image_link
      showdata['artist_name'] = show.artist.name
      showdata['start_time'] = show.start_time.strftime('%m/%d/%Y')
      if show.start_time > datetime.datetime.now():
          venue_data['upcoming_shows'].append(showdata)
      else:
        venue_data['past_shows'].append(showdata)

  return render_template('pages/show_venue.html', venue=venue_data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False
  try: 
    newvenue=Venue()
    newvenue.address = request.form['address']
    newvenue.city = request.form['city']
    newvenue.facebook_link = request.form['facebok_link']
    newvenue.genres = request.form['genres']
    newvenue. image_link = request.form[' image_link']
    newvenue.name = request.form['name']
    newvenue.phone = request.form['phone']
    newvenue.seeking_description = request.form['seeking_description']
    newvenue.seeking_talent = request.form['seeking_talent']
    newvenue.state = request.form['state']
    newvenue.website = request.form['website']
    db.session.add(newvenue)
    db.session.commit()
    
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
    

  finally: 
    db.session.close()

  if error: 
    flash('An error occurred. Venue'  + request.form['name'] + 'could not be listed')
  
  else: 
    flash('Venue ' + request.form['name'] + ' was successfully listed!')


  return render_template('pages/home.html')

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  error=False
  try: 
    Venue.query.get(venue_id).delete()
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally: 
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artistdata=[]
  artists = Artist.query.all()
  for artist in artists: 
   artistdata.append({
      'id': artist.id,
      'name': artist.name
      })
                
                

  return render_template('pages/artists.html', artists=artistdata)

@app.route('/artists/search', methods=['POST'])
def search_artists():  

  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

   searchterm = request.form.get('search_term')
   formattedsearch = "%{}%".format(searchterm.lower())
   output= Artist.query.filter(or_(Artist.city.ilike(formattedsearch), Artist.name.ilike(formattedsearch),  Artist.state.ilike(formattedsearch))).all()
   response = {
    'count':len(output),
    'data':output}
    
   return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist_data = {} 
  artist = Artist.query.get(artist_id)
  artist_data['id'] = artist.id
  artist_data['city'] = artist.city
  artist_data['facebook_link'] = artist.facebook_link
  artist_data['genres'] = artist.genres 
  artist_data['image_link'] = artist.image_link
  artist_data['name'] = artist.name
  artist_data['phone'] = artist.phone
  artist_data['seeking_description'] = artist.seeking_description
  artist_data['seeking_venue'] = artist.seeking_venue
  artist_data['shows'] = artist.shows
  artist_data['state'] = artist.state
  artist_data['website'] = artist.website

  for show in artist.shows: 
      showdata = {}
      showdata['venue_id'] = show.venue_id
      showdata['venue_image_link'] = show.venue.image_link
      showdata['venue_name'] = show.venue.name
      showdata['start_time'] = show.start_time.strftime('%m/%d/%Y')
      if show.start_time > datetime.datetime.now():
          artist_data['upcoming_shows'].append(showdata)
      else:
        artist_data['past_shows'].append(showdata)

  return render_template('pages/show_artist.html', artist=artist_data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist =Artist.query.get(artist_id)
  formdata={}
  formdata['id']= artist.id
  formdata['city']= artist.city
  formdata['facebook_link']= artist.facebook_link
  formdata['genres']= artist.genres
  formdata['image_link']= artist.image_link
  formdata['name']= artist.name
  formdata['phone']= artist.phone
  formdata['seeking_description']= artist.seeking_description
  formdata['seeking_venue']= artist.seeking_venue
  formdata['shows']= artist.shows
  formdata["state"]= artist.state
  formdata['website']= artist.website
  
  # TODO: populate form with fields from artist with ID <artist_id>

  return render_template('forms/edit_artist.html', form=form, artist=formdata)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try: 
    artistdata =  Artist.query.get(artist_id)
    artistdata.city = request.form['city']
    artistdata.facebook_link = request.form['facebook_link']
    artistdata.genres = request.form['genres']
    artistdata.image_link = request.form['image_link']
    artistdata.name = request.form['name']
    artistdata.phone = request.form['phone']
    artistdata.seeking_description = request.form['seeking_description']
    artistdata.seeking_venue = request.form['seeking_venue']
    artistdata.state = request.form['state']
    artistdata.website = request.form['website']
    db.session.add(artistdata)
    db.session.commit()
  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.get(venue_id)
  venuedata = {}
  venuedata['id']= venue.id
  venuedata['city']= venue.city
  venuedata['facebook_link']= venue.facebook_link
  venuedata['genres']= venue.genres
  venuedata['image_link']= venue.image_link
  venuedata['name']= venue.name
  venuedata['phone']= venue.phone
  venuedata['seeking_description']= venue.seeking_description
  venuedata['seeking_venue']= venue.seeking_venue
  venuedata['shows']= venue.shows
  venuedata["state"]= venue.state
  venuedata['website']= venue.website

  # TODO: populate form with values from venue with ID <venue_id>

  return render_template('forms/edit_venue.html', form=form, venue=venuedata)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes

  try: 
    venuedata= Venue.query.get(venue_id)
    venuedata.address = request.form['address']
    venuedata.city = request.form['city']
    venuedata.facebook_link = request.form['facebok_link']
    venuedata.genres = request.form['genres']
    venuedata.image_link = request.form['image_link']
    venuedata.name = request.form['name']
    venuedata.phone = request.form['phone']
    venuedata.seeking_description = request.form['seeking_description']
    venuedata.seeking_talent = request.form['seeking_talent']
    venuedata.state = request.form['state']
    venuedata.website = request.form['website']
    db.session.add(venuedata)
    db.session.commit()

  except: 
    db.session.rollback()
    print(sys.exc_info())

  finally: 
    db.session.close

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  error = False
  try: 
    artistdata = Artist()
    artistdata.city = request.form['city']
    artistdata.facebook_link = request.form['facebook_link']
    artistdata.genres = request.form['genres']
    artistdata.image_link = request.form['image_link']
    artistdata.name = request.form['name']
    artistdata.phone = request.form['phone']
    artistdata.seeking_description = request.form['seeking_description']
    artistdata.seeking_venue = request.form['seeking_venue']
    artistdata.state = request.form['state']
    artistdata.website = request.form['website']
    db.session.add(artistdata)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()

  if error: 
    flash('An error occurred. Artist'  + request.form['name'] + 'could not be listed')
  
  else: 
    # on successful db insert, flash success 
    flash('Artist ' + request.form['name'] + ' was successfully listed!')

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():

  # displays list of shows at /shows
  # TODO: replace with real venues data.

  alldata=[]
  shows = Show.query.all()
  for show in shows: 
    showdata = {}
    alldata.append({
      'artist_id': show.artist_id,
      'artist_image_link': show.artist.image_link,
      'artist_name': show.artist.name,
      'start_time': show.start_time.strftime("%m/%d/%Y, %H:%M:%S"),
      'venue_id': show.venue.id,
      'venue_name': show.venue.name
    })
    

  return render_template('pages/shows.html', shows=alldata)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():

  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  error = False
  try: 
    showdata = Show()
    showdata.artist_id = request.form['artist_id']
    showdata.start_time = request.form['start_time']
    showdata.venue_id = request.form['venue_id']
    db.session.ass(showdata)
    db.session.commit()

  except: 
    error=True
    db.session.rollback()
    print(sys.exc_info())

  finally:   
    db.session.close()

  if error: 
    flash('An error occurred. Show could not be listed.')

  else: 
   flash('Show was successfully listed!')

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
