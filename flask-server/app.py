import os
import random
import json
import csv
import xlrd as excel
import simplejson as json
from datetime import datetime,timedelta
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import or_ 
from flask.ext import restful
from marshmallow import Serializer, fields, pprint
from werkzeug import secure_filename
from modeling import NewTest,DataPrepare

app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['txt','csv','xls','xlsx'])
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)
api = restful.Api(app)

"""
	=================================================================
	*  Start of routes
	=================================================================
"""
@app.route('/')
def show_index():
	return render_template('index.html', msg='success')

@app.route('/upload',methods=['GET', 'POST'])
def upload_file():
	"""Upload lastest month data file and update models based on this file
	input:
		CSV file with trasaction and memos data
	return:
		html 
	"""
	if request.method == 'POST':
		f = request.files['file']
		if f and _allowed_file(f.filename):
			# Save file to upload folder
			filename = secure_filename(f.filename)
			prefix = datetime.now().strftime("%S-%M-%y-")
			path = os.path.join(app.config['UPLOAD_FOLDER'], prefix + filename)
			f.save(path)
			nfile = File(prefix+filename, path)
			db.session.add(nfile)
			db.session.commit()
			try:
				# Parse uploaded file
				query = FactQuery()
				dp = DataPrepare(path)
				query.insert_from_map(dp.get_data_map())
				#predict and save into database,do it every month

				return render_template('upload.html', msg='success')
			except Exception, e:
				return render_template('upload.html',  msg='Error happen')
		else:
			return render_template('upload.html')
	else:
		return render_template('upload.html')

@app.route('/pre_upload',methods=['GET', 'POST'])
def pre_upload():
	""" Upload excel file, write back file id and list of sheet names
	"""
	if request.method == 'POST':
		f = request.files['file']
		if f and _allowed_file(f.filename):
			#print f.filename
			# TO-DO: write a save file function
			filename = secure_filename(f.filename)
			prefix = datetime.now().strftime("%S-%M-%y-")
			path = os.path.join(app.config['UPLOAD_FOLDER'], prefix + filename)
			f.save(path)
			nfile = File(prefix+filename, path)
			db.session.add(nfile)
			db.session.commit()

			data = excel.open_workbook(path)
			sheets = data.sheets()
			names = [s.name for s in sheets]
			return redirect('/pre_upload_data/'+",".join(names)+"/"+ prefix + filename+"/"+filename)
		else:
			return render_template('json.html',msg="None2")
	else:
		names = {'aa':'dsada','bb':'dsada'}
		return render_template('json.html',msg=names)

@app.route('/update', methods = ['POST'])
def update():
	"""Update me table for each year
	"""
	filename = request.form['filename']
	sheetname = request.form['sheetname']
	f = File.query.filter(File.name == filename).first()
	# update me
	workbook = excel.open_workbook(f.path)
	sheet =workbook.sheet_by_name(sheetname)
	col_index = [ 0, 1, 2, 3]
	dates = sheet.col_values(col_index[0])
	mes = sheet.col_values(col_index[1])
	memos = sheet.col_values(col_index[2])
	transactions = sheet.col_values(col_index[3])
	
	facts = [Fact(_str2date(dates[i]),mes[i],memos[i],transactions[i]) for i in range(1,len(dates))]
	mes = [ME(_str2date(dates[i]),mes[i]) for i in range(1,len(dates))]

	# update me
	mq = MeQuery()
	mq.insert_mes(mes)
	
	#update data
	fq = FactQuery()
	insert_fact_count = fq.insert_from_facts(facts)

	# run prediction process	
	if insert_fact_count > 0:
		predict()
	return render_template('json.html',msg="success"
		)


@app.route('/need_update')
def need_update():
	"""Check if model need update or not
	"""
	pq = PredictionQuery()
	year, month = pq.get_lastest_date()
	# Get this month End date time
	end_datetime = datetime(year=year, month=month, day=31)
	now = datetime.now()
	if now > end_datetime:
		msg = "true"
	else:
		msg = "false"	
	return render_template('json.html',msg=msg
		)

def init_dict_tables():
	"""Initialize the values of dict table
	"""
	model_types = ['tmem1','tmemean','tme','tmep1','mmem1','mme','mmep1']
	me_types = ['me-1','me','me+1']
	ff = [0.95, 0.97, 0.99]
	for model_name in model_types:
		db.session.add(ModelType(model_name))
	for me_name in me_types:
		db.session.add(MeType(me_name))
	for number in ff:
		db.session.add(ForgetFact(number))
	db.session.commit()


class PredictionData(restful.Resource):
    def get(self):
    	pjs =  make_predict_json()
    	reals =  make_real_json()
    	m = [pjs[0],pjs[1],reals[0],reals[1]]
    	mes =  MeQuery().get_all_me()
    	return {"mes" : mes, "predictions" : m}

class PreUpload(restful.Resource):
	def get(self, listStr, filename, realname):
		strs = listStr.split(',')
		return [strs, filename, realname]

class MEsApi(restful.Resource):
	def get(self):
		return MeQuery().get_all_me()

api.add_resource(PredictionData, '/predict_data')
api.add_resource(MEsApi, '/mes')
api.add_resource(PreUpload, '/pre_upload_data/<string:listStr>/<string:filename>/<string:realname>')

"""
	End of routes
"""

"""
	=============================================
	*  Start of model query
	=============================================
"""
class FactQuery(object):
	""" Query methods about Fact object
	"""
	mes = ['ME-1','ME+1','ME']
	def __init__(self):
		self.load()

	def load(self):
		""" Load and format required data
		"""
		facts = Fact.query.all()
		fact_keys = []
		fact_list = []
		fact_date_keys = []
		me_facts = {}
		for f in facts:
			fact_date_keys.append(f.datetime)
			fact_keys.append(_date2str(f.datetime))
			data = []
			data.append(_date2str(f.datetime))
			data.append(f.trasaction)
			data.append(f.memos)
			fact_list.append(data)
			if f.me in self.mes:
				dt = f.datetime
				#if f.me == 'ME-1' or f.me == 'ME':
				#	dt = dt + timedelta(days=10)
				if f.me == 'ME+1':
					dt = dt - timedelta(days=10)
				key = "%s-%s" % (dt.year,dt.month)
				if key in me_facts.keys():
					me_facts[key].append(f)
				else:
					me_facts[key] = [f]
		self.me_facts = me_facts
		self.fact_keys = fact_keys
		self.fact_list = fact_list
		self.fact_date_keys = sorted(fact_date_keys)

	def get_me_facts(self):
		return self.me_facts

	def get_start_date(self):
		return self.fact_date_keys[0]

	def get_end_date(self):
		return self.fact_date_keys[len(self.fact_date_keys)-1]

	def get_dates(self):
		return self.fact_date_keys

	def get_months(self):
		month_list = []
		for dt in self.fact_date_keys:
			key = (dt.year,dt.month)
			if key not in month_list:
				month_list.append(key)
		return month_list

	def insert_from_map(self, data_map):
		""" Insert Fact data to database
		"""
		db_fact_keys = self.fact_date_keys
		for key in data_map.keys():
			data = data_map[key]
			fact = Fact(_str2date(data[0]),data[1],data[2],data[3])
			if _date2str(fact.datetime) not in db_fact_keys:
				db.session.add(fact)
		flag =  db.session.commit()
		self.load()
		return flag

	def insert_from_facts(self, facts):
		db_fact_keys = self.fact_date_keys
		count = 0
		for fact in facts:
			if fact.datetime not in db_fact_keys and fact.memos != '' and fact.trasaction != '':
				db.session.add(fact)
				count = count + 1
		flag = db.session.commit()
		self.load()
		return count

	def get_data(self):
		return self.fact_list

	def get_period_data(self, froms, end):
		pass

class MeQuery(object):
	def __init__(self):
		pass

	def insert_mes(self, mes):
		all_me = ME.query.all()
		dts = [m.datetime for m in all_me]
		count = 0
		for me in mes:
			if me.datetime not in dts:
				db.session.add(me)
				count = count + 1
		db.session.commit()
		print "count%d" %count

	def get_all_me(self):
		mes = ME.query.filter(or_( ME.me=='ME',\
								   ME.me == 'ME-1',\
							       ME.me == 'ME+1'))
		dt_map = {}
		for me in mes:
			tmp_dtstr = _date2str(me.datetime)
			if me.me == 'ME+1':
				me.datetime = me.datetime - timedelta(days=10)
			key = '%s-%02d-%s' %(me.datetime.year, me.datetime.month, me.me)
			dt_map[key] = tmp_dtstr
		return dt_map


class MediaParamterQuery(object):
	def __init__(self):
		pass

	def get_mp(self, year_month):
		return MediaParamter.query.filter(year=year_month[0], month=year_month[1])


class PredictionQuery(object):
	def __init__(self):
		self.load()

	def load(self):
		predicts = Prediction.query.filter(Prediction.ff==0.95)
		m = {}
		year_month_list = []
		for predict in predicts:
			ym_tuple = (predict.year, predict.month)
			key = "%s-%s" % ym_tuple
			if ym_tuple not in year_month_list:
				year_month_list.append(key) 
			if key in m.keys():
				m[key].append(predict)
			else:
				m[key] = [predict]
		self.predict_map = m
		self.date_list = _year_month_sort(year_month_list)

	def get_lastest_date(self):
		ym = self.date_list[0].split('-')
		return (int(ym[0]), int(ym[1]))

	def get_keys(self):
		return [prd.get_key_str() for prd in Prediction.query.all()]

	def get_predictions(self):
		return self.predict_map

	def insert_from_results(self, results):
		pass

"""
	=============================================
	*  End of model query
	=============================================
"""

"""
	================================
	*  Model Definition
	================================
"""
class Fact(db.Model):
	__tablename__ = 'fact'
	datetime = db.Column(db.DateTime, primary_key=True)
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
	year = db.Column(db.Integer, primary_key=True)
	month = db.Column(db.Integer, primary_key=True)
	model_type = db.Column(db.String, primary_key=True)
	value = db.Column(db.Float)
	ff = db.Column(db.Float, primary_key=True)

	def __init__(self, year, month, value, model_type, ff):
		self.year = year
		self.month = month
		self.value = value
		self.model_type = model_type
		self.ff = ff

	def as_dict(self):
		return {c.name: getattr(self, c.name) for c in self.__table__.columns}

	def get_key_str(self):
		return "%s-%s-%s-%s" % (self.year, self.month, self.model_type, self.ff)


class PredictionSerializer(Serializer):
	year = fields.Integer()
	month = fields.Integer()
	model_type = fields.String()
	value = fields.Float()
	ff = fields.Float()

class MediaParamter(db.Model):
	__tablename__ = 'media_parameter'
	year = db.Column(db.Integer, primary_key=True)
	month = db.Column(db.Integer, primary_key=True)
	model_type = db.Column(db.String, primary_key=True)
	beta = db.Column(db.String)
	ff = db.Column(db.Float, primary_key=True)
	p = db.Column(db.String)

	def __init__(self, year, month, model_type, beta, p, ff):
		self.year = year
		self.month = month
		self.model_type = model_type
		self.beta = beta
		self.p = p
		self.ff = ff

class ForgetFact(db.Model):
	__tablename__ = 'forget_fact'
	value = db.Column(db.Float, primary_key=True)

	def __init__(self, value):
		self.value = value

class MeType(db.Model):
	__tablename__ = 'me_type'
	name = db.Column(db.String, primary_key=True)

	def __init__(self, name):
		self.name = name

class ModelType(db.Model):
	__tablename__ = 'model_type'
	name = db.Column(db.String, primary_key=True)

	def __init__(self, name):
		self.name = name

class File(db.Model):
	__tablename__ = 'file'
	name = db.Column(db.String, primary_key=True)
	path = db.Column(db.String)

	def __init__(self, name, path):
		self.path = path
		self.name = name

class ME(db.Model):
	__tablename__ = 'me'
	datetime = db.Column(db.DateTime, primary_key=True)
	me = db.Column(db.String)

	def __init__(self, datetime, me):
		self.datetime = datetime
		self.me = me

"""
	End of Model Definition
"""


def init_db():
	db.create_all()
	init_dict_tables()
	#InitialParameters(app.config['START_YEAR'], app.config['START_MONTH']).run()

def drop_db():
	db.drop_all()

def make_real_json():
	#get real
	fq = FactQuery()
	me_facts = fq.get_me_facts()

	memos_values = []
	trasaction_values = []
	keys = _year_month_sort(me_facts.keys())
	for key in keys:
		memos = {}
		trasaction = {}
		if len(me_facts[key]) < 3: # swap if there exist
			continue
		for fact in me_facts[key]:
			if fact.me == 'ME':
				memos['me'] = fact.memos
				trasaction['me'] = fact.trasaction
			elif fact.me == 'ME-1':
				memos['me-1'] = fact.memos
				trasaction['me-1'] = fact.trasaction
			elif fact.me == 'ME+1':
				memos['me+1'] = fact.memos
				trasaction['me+1'] = fact.trasaction
		memos['month'] = _print_year_month(key)
		trasaction['month'] = _print_year_month(key)
		memos_values.append(memos)
		trasaction_values.append(trasaction)
	return (_get_data_map(memos_values,'memos',False),_get_data_map(trasaction_values,'transaction',False))

def make_predict_json():
	me_couple = {'mme':'me','mmem1':'me-1','mmep1':'me+1',\
				 'tme':'me','tmem1':'me-1','tmep1':'me+1'}
	p = PredictionQuery()
	pre_facts = p.get_predictions()
	pre_memos_values = []
	pre_trasaction_values = []
	keys = _year_month_sort(pre_facts.keys())
	for key in keys:
		mm = {'month':_print_year_month(key)}
		tm = {'month':_print_year_month(key)}
		for fact in pre_facts[key]:
			if fact.model_type not in me_couple.keys():
				continue
			if fact.model_type[0]=='m':
				mm[me_couple[fact.model_type]] = fact.value
			elif fact.model_type[0]=='t':
				tm[me_couple[fact.model_type]] = fact.value
		pre_trasaction_values.append(tm)
		pre_memos_values.append(mm)

	return (_get_data_map(pre_memos_values,'memos',True),_get_data_map(pre_trasaction_values,'transaction',True))	

def predict():
	fq = FactQuery()
	nt = NewTest()
	results = nt.run(fq.get_data(),fq.get_months(),fq.get_me_facts())
	rq = PredictionQuery()
	keys = rq.get_keys()
	for p in results:
		predict = Prediction(p['year'],p['month'],p['value'],p['model_type'],p['ff'])
		if predict.get_key_str() not in keys:
			db.session.add(predict)
	try:
		db.session.commit()
	except Exception, e:
		print "Prediction insert error happen!"
	

def _str2date(string):
    return datetime.strptime(string, '%m/%d/%Y')

def _date2str(date):
    return date.strftime('%m/%d/%Y')

def _get_data_map(dlist, dtype, is_predict):
	m = {}
	m['endMonth'] = dlist[0]['month']
	m['startMonth'] = dlist[len(dlist)-1]['month']
	m['isPredict'] = is_predict;
	m['type'] = dtype
	m['values'] = dlist
	return m

def _year_month_sort(year_months):
	""" Sort a list of year_month 
	Input:
		['2014-6','2014-5'....]
	Output:
		A list of year_month str but sorted as time 
	"""
	date_list = []
	for d in year_months:
		l = d.split('-')
		year,month = (int(l[0]),int(l[1]))
		date_list.append(datetime(year=year, month=month, day=1))
	date_list = sorted(date_list, reverse=True)
	return [ str(x.year)+'-'+str(x.month) for x in date_list]

def _print_year_month(year_month):
	l = year_month.split('-')
	year,month = (int(l[0]),int(l[1]))
	month = "%02d"%month
	return str(year)+'-'+month


def _allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


if __name__ == '__main__':
	app.run()
	#predict()
	#MeQuery().get_all_me()
