from datetime import datetime
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Serializer, fields, pprint
from werkzeug import secure_filename
import os

app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)

class Fact(db.Model):
	__tablename__ = 'fact'
	datetime = db.Column(db.DateTime,primary_key=True)
	me = db.Column(db.String)
	trasaction = db.Column(db.Float)
	memos = db.Column(db.Float)

	def __init__(self, datetime, me, trasaction, memos):
		self.datetime = datetime
		self.me = me
		self.memos = memos
		self.trasaction = trasaction

class Prediction(db.Model):
	__tablename__ = 'prediction'
	year_month = db.Column(db.Integer, primary_key=True)
	me_type = db.Column(db.String, primary_key=True)
	model_type = db.Column(db.String, primary_key=True)
	value = db.Column(db.Float)

	def __init__(self, year_month, me_type, value, model_type):
		self.year_month = year_month
		self.me_type = me_type
		self.value = value
		self.model_type = model_type

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class PredictionSerializer(Serializer):
	year_month = fields.Integer()
	me_type = fields.String()
	model_type = fields.String()
	value = fields.Float()

class MediaParamter(db.Model):
	__tablename__ = 'media_parameter'
	year_month = db.Column(db.Integer, primary_key=True)
	model_type = db.Column(db.String, primary_key=True)
	me_type = db.Column(db.String, primary_key=True)
	beta = db.Column(db.String)

	def __init__(self, year_month, model_type, me_type, beta):
		self.year_month = year_month
		self.model_type = model_type
		self.me_type = me_type
		self.beta = beta

class MeType(db.Model):
	__tablename__ = 'me_type'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)

	def __init__(self, name):
		self.name = name

class ModelType(db.Model):
	__tablename__ = 'model_type'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)

	def __init__(self, name):
		self.name = name

class Files(db.Model):
	__tablename__ = 'files'
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String)
	path = db.Column(db.String)

	def __init__(self):
		pass

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def show_index():
	predicts = Prediction.query.first()
	serial = PredictionSerializer(predicts)
	pprint(serial.data)
	return render_template('index.html',
			metypes = MeType.query.all()
		)

@app.route('/upload',methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		f = request.files['file']
		if f and allowed_file(f.filename):
			filename = secure_filename(f.filename)
			f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return render_template('index.html')
	else:
		return render_template('index.html')

@app.route('/get_predict')
def predict_data():
	"""Get all Predictions in database
	return:
		json
	"""
	return render_template('index.html'
		)

@app.route('/update_model')
def update_model():
	#get data from csv	

	#update model if necessary

	#refresh interface
	return render_template('index.html'
		)

def init_db():
	db.create_all()

def drop_db():
	db.drop_all()

if __name__ == '__main__':
	app.run()
