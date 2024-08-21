from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_restful import Api
from configparser import ConfigParser

conffile = 'app.conf'

def ParseConfig(section, param, filename=conffile):
	# create a parser
	parser = ConfigParser()
	
	# read config file
	parser.read(filename)

	# get section, default to postgresql
	if parser.has_section(section):
		params = parser.items(section)
		for p in params:
			if p[0] == param:
				return p[1]
	else:
		raise Exception('Section {0} not found in the {1} file'.format(section, filename))

	return None

app = Flask(__name__)

#allows cross-domain call
CORS(app)

marshmallow = Marshmallow(app)

FlaskAPI = Api(app)

