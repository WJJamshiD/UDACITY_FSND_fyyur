import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from fyyur.models import Artist,Venue,Show
from fyyur.forms import *
from fyyur import app,db
import datetime


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
	date = dateutil.parser.parse(value)
	if format == 'full':
			format="EEEE MMMM, d, y 'at' h:mma"
	elif format == 'medium':
			format="EE MM, dd, y h:mma"
	return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
	return render_template('/pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
	# TODO: replace with real venues data.
	#       num_shows should be aggregated based on number of upcoming shows per venue.
	data = []
	venues = Venue.query.distinct(Venue.city, Venue.state).all()
	if venues:
		for venue in venues:
			print(venue.city)
			area_venues=[]
			for ven in Venue.query.filter_by(city=venue.city,state=venue.state).all():
				upcoming_shows = len(Show.query.filter(Show.start_time > datetime.datetime.now(),Show.venue_id == ven.id).all())
				area_venues.append({
										"id": ven.id,
										"name": ven.name,
										"upcoming_shows": upcoming_shows
									})
			data.append({
						"city": venue.city,
						"state": venue.state,
						"venues":area_venues,
					})


	return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
	# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
	# seach for Hop should return "The Musical Hop".
	# search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
	search_term = request.form.get("search_term", "")
	results = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
	data = []
	for venue in results:
		data.append({
				"id": venue.id,
				"name": venue.name,
				"upcoming_shows": len(Show.query.filter(Show.start_time > datetime.datetime.now(), Show.venue_id == venue.id).all())
			})
		print(data)
	return render_template('pages/search_venues.html', results={'data':data,'count':len(results)}, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
	# shows the venue page with the given venue_id
	# TODO: replace with real venue data from the venues table, using venue_id
	venue = Venue.query.get(venue_id)
	shows = Show.query.filter(Show.venue_id == venue.id).all()
	upcoming_shows = []
	past_shows = []
	for show in shows:
		artist = Artist.query.filter_by(id=show.artist_id).first()
		start_time = format_datetime(str(show.start_time))
		venue_show = {
					"artist_id": artist.id,
					"artist_name": artist.name,
					"artist_image_link": artist.image_link,
					"start_time": start_time
		}
		if show.start_time >=datetime.datetime.now():
			upcoming_shows.append(venue_show)
		elif show.start_time < datetime.datetime.now():
			past_shows.append(venue_show)

	data={
		"id": venue.id,
		"name": venue.name,
		"genres": venue.genres,
		"address": venue.address,
		"city": venue.city,
		"state": venue.state,
		"phone": venue.phone,
		"website": venue.website,
		"facebook_link": venue.facebook_link,
		"seeking_talent": venue.seeking_talent,
		"seeking_description": venue.seeking_description,
		"image_link": venue.image_link,
		"past_shows": past_shows,
		"upcoming_shows": upcoming_shows,
		"past_shows_count": len(past_shows),
		"upcoming_shows_count": len(upcoming_shows),
	}
	return render_template('pages/show_venue.html', venue=data)

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
	form = VenueForm()
	has_error=False
	if form.validate_on_submit():
		try:
			venue = Venue(name=form.name.data, state=form.state.data, city=form.city.data, 
										address=form.address.data, phone=form.phone.data, 
										image_link=form.image_link.data,facebook_link=form.facebook_link.data, 
										website=form.website.data, seeking_description=form.seeking_description.data,
										seeking_talent=form.seeking_talent.data, genres=form.genres.data)

			db.session.add(venue)
			db.session.commit()
			flash('Venue ' + request.form['name'] + ' was successfully listed!')
			return render_template('pages/home.html')
		except Exception as e:
			print(e)
			has_error=True
	else:
		print(form.errors)
		has_error=True
	if has_error:
		flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
	return render_template('forms/new_venue.html',form=form)

@app.route('/venues/<venue_id>', methods=['POST'])
def delete_venue(venue_id):
	try:
		Venue.query.filter_by(id=venue_id).delete()
		db.session.commit()
	except:
		db.session.rollback()
	finally:
		db.session.close()
	return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
	# TODO: replace with real data returned from querying the database
	data=Artist.query.all()
	return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
	# TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
	# seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
	# search for "band" should return "The Wild Sax Band".
	search_term = request.form.get("search_term", "")
	finded_artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
	data = []
	for artist in finded_artists:
		data.append({
					"id": artist.id,
					"name": artist.name,
					"num_upcoming_shows": len(Show.query.filter(Show.start_time > datetime.datetime.now(), Show.artist_id == artist.id).all())
			})
	response={
		"count": len(finded_artists),
		"data": data
	}
	return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	# shows the venue page with the given venue_id
	# TODO: replace with real venue data from the venues table, using venue_id
	artist=Artist.query.get(artist_id)
	shows = Show.query.filter(Show.artist_id == artist.id).all()
	upcoming_shows = []
	past_shows = []
	for show in shows:
		venue = Venue.query.filter_by(id=show.venue_id).first()
		start_time = format_datetime(str(show.start_time))
		artist_show = {
					"venue_id": artist.id,
					"venue_name": artist.name,
					"venue_image_link": artist.image_link,
					"start_time": start_time
		}
		if show.start_time >= datetime.datetime.now():
			upcoming_shows.append(artist_show)
		elif show.start_time < datetime.datetime.now():
			past_shows.append(artist_show)

	
	data={
		"id": artist.id,
		"name": artist.name,
		"genres": artist.genres,
		"city": artist.city,
		"state": artist.state,
		"phone": artist.phone,
		"website": artist.website,
		"facebook_link": artist.facebook_link,
		"seeking_venue": artist.seeking_venue,
		"seeking_description": artist.seeking_description,
		"image_link": artist.image_link,
		"past_shows":past_shows,
		"upcoming_shows": upcoming_shows,
		"past_shows_count": len(past_shows),
		"upcoming_shows_count": len(upcoming_shows),
	}
	return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
	
	form = ArtistForm()
	artist=Artist.query.get(artist_id)
	form.name.data = artist.name
	form.genres.data = artist.genres
	form.city.data = artist.city 
	form.state.data = artist.state 
	form.phone.data = artist.phone
	form.image_link.data = artist.image_link
	form.facebook_link.data = artist.facebook_link
	form.website.data = artist.website 
	form.seeking_venue.data = artist.seeking_venue
	form.seeking_description.data = artist.seeking_description
	# TODO: populate form with fields from artist with ID <artist_id>
	return render_template('forms/edit_artist.html', form=form, artist=artist)

# DELETE
#-----------------------------------------
@app.route('/artists/<artist_id>', methods=['POST'])
def delete_artist(artist_id):
	try:
		Artist.query.filter_by(id=artist_id).delete()
		db.session.commit()
	except:
		db.session.rollback()
	finally:
		db.session.close()
	return redirect(url_for('index'))


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
	# TODO: take values from the form submitted, and update existing
	# artist record with ID <artist_id> using the new attributes
	form = ArtistForm()
	has_error=False
	if form.validate_on_submit():
		try:
			artist = Artist.query.get(artist_id)
			artist.name = form.name.data
			artist.genres = form.genres.data
			artist.city = form.city.data
			artist.state = form.state.data
			artist.phone = form.phone.data
			artist.website = form.website.data
			artist.facebook_link = form.facebook_link.data
			artist.image_link=form.facebook_link.data
			artist.seeking_venue=form.seeking_venue.data
			artist.seeking_description=form.seeking_description.data

			db.session.add(artist)
			db.session.commit()
			flash('Artist edited succesfully!')
			return redirect(url_for('show_artist', artist_id=artist_id))
		except:
			has_error=True
			flash('Error happened try again!')
			pass
	else:
		has_error=True
		flash('Form is not valid, try again!')
		print(form.errors)
	if has_error:
		return redirect(url_for('edit_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
	form = VenueForm()
	venue = Venue.query.get(venue_id)
	form.name.data = venue.name
	form.genres.data = venue.genres
	form.city.data = venue.city 
	form.state.data = venue.state 
	form.address.data = venue.address
	form.phone.data = venue.phone
	form.image_link.data=venue.image_link
	form.facebook_link.data = venue.facebook_link
	form.website.data = venue.website 
	form.seeking_talent.data = venue.seeking_talent
	form.seeking_description.data = venue.seeking_description
	# TODO: populate form with values from venue with ID <venue_id>
	return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
	# TODO: take values from the form submitted, and update existing
	# venue record with ID <venue_id> using the new attributes
	form = VenueForm()
	has_error=False
	if form.validate_on_submit():
		try:
			venue = Venue.query.get(venue_id)
			venue.name = form.name.data
			venue.genres = form.genres.data
			venue.city = form.city.data
			venue.state = form.state.data
			venue.address = form.address.data
			venue.phone = form.phone.data
			venue.image_link=form.image_link.data
			venue.facebook_link = form.facebook_link.data
			venue.website = form.website.data
			venue.seeking_talent=form.seeking_talent.data
			venue.seeking_description=form.seeking_description.data

			db.session.add(venue)
			db.session.commit()
			flash('Venue succesfully edited!')
			return redirect(url_for('show_venue', venue_id=venue_id))
		except:
			has_error=True
			flash('Error happened try again!')
			pass
	else:
		has_error=True
		flash('Form is not valid, try again!')
		print(form.errors)
	if has_error:
		return redirect(url_for('edit_venue', venue_id=venue_id))
	

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
	form = ArtistForm()
	has_error=False
	if form.validate_on_submit():
		try:
			artist = Artist(name=form.name.data, state=form.state.data, city=form.city.data, 
												phone=form.phone.data,image_link=form.image_link.data, 
												seeking_description=form.seeking_description.data, 
												website=form.website.data,facebook_link=form.facebook_link.data, 
												seeking_venue=form.seeking_venue.data, genres=form.genres.data)

			db.session.add(artist)
			db.session.commit()
			flash('Artist ' + request.form['name'] + ' was successfully listed!')
			return render_template('pages/home.html')
		except Exception as e:
			print(e)
			has_error=True
	else:
		print(form.errors)
		has_error=True
	if has_error:
		flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
		return render_template('forms/new_artist.html',form=form)


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
	# displays list of shows at /shows
	data=[]
	for show in Show.query.all():
		artist=Artist.query.get(show.artist_id)	
		venue=Venue.query.get(show.venue_id)	
		data.append({
			"venue_id": venue.id,
			"venue_name": venue.name,
			"artist_id": artist.id,
			"artist_name": artist.name,
			"artist_image_link": artist.image_link,
			"start_time": format_datetime(str(show.start_time))
		})
	
	return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
	# renders form. do not touch.
	form = ShowForm()
	return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
	# called to create new shows in the db, upon submitting new show listing form
	# TODO: insert form data as a new Show record in the db, instead
	form = ShowForm()
	has_error=False
	if form.validate_on_submit():
		try:
			show = Show( artist_id=form.artist_id.data, 
									venue_id=form.venue_id.data, start_time=form.start_time.data)
			db.session.add(show)
			db.session.commit()
			flash('Show was successfully listed!')
			return render_template('pages/home.html')
		except Exception as e:
			print(e)
			has_error=True
	else:
		print(form.errors)
		has_error=True
	if has_error:
		flash('An error occurred. Show  could not be listed.')
		return render_template('forms/new_show.html',form=form)

