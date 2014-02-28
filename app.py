import os, datetime
import re
from flask import Flask, request, render_template, redirect, abort, flash, json

from unidecode import unidecode

# mongoengine database module
from flask.ext.mongoengine import MongoEngine


app = Flask(__name__)   # create our flask app
app.config['CSRF_ENABLED'] = False
#app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

# --------- Database Connection ---------
# MongoDB connection to MongoLab's database
app.config['MONGODB_SETTINGS'] = {'HOST':os.environ.get('MONGOLAB_URI'),'DB': 'GowanusFlora'}
app.logger.debug("Connecting to MongoLabs")
db = MongoEngine(app) # connect MongoEngine with Flask App

# import data models
import models

# hardcoded categories for the checkboxes on the form
species = ['Wild Madder', 'Mugwort', 'Lambs Quarters', 'Shepherds Purse', 'Storksbill', 'White Clover', 'Bittersweet Nightshade', 'Black Medick', 
'Rough Fruitted Cinquefoil', 'Common Groundsel', 'Garlic Mustard']
# --------- Routes ----------
# this is our main pagex
@app.route("/", methods=['GET','POST'])
def index():

	# if form was submitted and it is valid...
	if request.method == "POST":

		# get form data - create new user
		flora = models.Flora()
		
	
		flora.point = [float(request.form.get('lon')), float(request.form.get('lat'))]
		flora.near = request.form.get('near')
	
		flora.species = request.form.get('species') # getlist will pull multiple items into a list

		flora.save() # save it

		# redirect to the report list
		return redirect('/allflora')
		

	else:

		# render the template
		templateData = {
		'flora' : models.Flora.objects(),
		'species' : species,
		
		}
		return render_template("main.html", **templateData)

@app.route("/allflora")
def allflora():

	templateData = {
		'flora' : models.Flora.objects()
		}
	return render_template('allflora.html', **templateData)
#__________________________________________________________________

from flask import jsonify


####################################
@app.route('/data/flora')
def data_flora():
 
	# query for the users - return oldest first, limit 10
	flora = models.Flora.objects().order_by('-timestamp')
 
	if flora:
 
		# list to hold users
		public_flora = []
 
		#prep data for json
		for f in flora:
			
			tmpFlora= {
				'type':'feature',
				'properties' :{
				
				
				'species':f.species,
				
				'reported' : str( f.timestamp )
				},
				'geometry':{
				'type': 'point',
				'coordinates' : f.point
				}
				
				
			}
 
 
			# insert user dictionary into public_users list
			public_flora.append( tmpFlora )
 
		# prepare dictionary for JSON return
		data = {
			
			'flora' : public_flora
		}
 
		# jsonify (imported from Flask above)
		# will convert 'data' dictionary and set mime type to 'application/json'
		return jsonify(data)
 
	else:
		error = {
			'status' : 'error',
			'msg' : 'unable to retrieve species list'
		}
		return jsonify(error)


####################################

@app.errorhandler(404)
def page_not_found(error):
	return render_template('404.html'), 404


# slugify the title 
# via http://flask.pocoo.org/snippets/5/
_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')
def slugify(text, delim=u'-'):
	"""Generates an ASCII-only slug."""
	result = []
	for word in _punct_re.split(text.lower()):
		result.extend(unidecode(word).split())
		return unicode(delim.join(result))



# --------- Server On ----------
# start the webserver
if __name__ == "__main__":
	app.debug = True
	
	port = int(os.environ.get('PORT', 5000)) # locally PORT 5000, Heroku will assign its own port
	app.run(host='0.0.0.0', port=port)



	