import os
import random
import json
from datetime import datetime,timedelta
from flask import Flask, request, flash, url_for, redirect, \
     render_template, abort
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Serializer, fields, pprint
from werkzeug import secure_filename
from modeling_open import DataPrepare,NewTest

app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv'])
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)

def _str2date(string):
    return datetime.strptime(string, '%m/%d/%Y')

def _date2str(date):
    return date.strftime('%m/%d/%Y')

class FactQuery(object):
	mes = ['ME-1','ME+1','ME']
	def __init__(self):
		self.load()

	def load(self):
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
			data.append(f.memos)
			data.append(f.trasaction)
			fact_list.append(data)
			if f.me in self.mes:
				dt = f.datetime
				if f.me == 'ME-1' or f.me == 'ME':
					dt = dt + timedelta(days=10)
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
		db_fact_keys = self.fact_date_keys
		for key in data_map.keys():
			data = data_map[key]
			fact = Fact(_str2date(data[0]),data[1],data[2],data[3])
			if _date2str(fact.datetime) not in db_fact_keys:
				db.session.add(fact)
		flag =  db.session.commit()
		self.load()
		return flag

	def get_data(self):
		return self.fact_list

	def get_period_data(self, froms, end):
		pass

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
		for predict in predicts:
			key = "%s-%s" %(predict.year,predict.month)
			if key in m.keys():
				m[key].append(predict)
			else:
				m[key] = [predict]
		self.predict_map = m

	def get_predictions(self):
		return self.predict_map

class Fact(db.Model):
	__tablename__ = 'fact'
	datetime = db.Column(db.DateTime, primary_key=True)
	me = db.Column(db.String)
	trasaction = db.Column(db.Float)
	memos = db.Column(db.Float)

	def __init__(self, datetime, me, memos, trasaction):
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

class Files(db.Model):
	__tablename__ = 'files'
	name = db.Column(db.String, primary_key=True)
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
	"""Upload lastest month data file and update models based on this file
	input:
		CSV file with trasaction and memos data
	return:
		html 
	"""
	if request.method == 'POST':
		f = request.files['file']
		if f and allowed_file(f.filename):
			filename = secure_filename(f.filename)
			prefix = datetime.now().strftime("%S-%M-%y-")
			path = os.path.join(app.config['UPLOAD_FOLDER'], prefix + filename)
			f.save(path)

			try:
				query = FactQuery()
				dp = DataPrepare(path)
				query.insert_from_map(dp.get_data_map())
				#predict and save into database,do it every month

				return render_template('index.html', msg='')
			except Exception, e:
				print(e)
				return render_template('index.html',  msg='Error happen')
		else:
			return render_template('index.html')
	else:
		return render_template('index.html')

@app.route('/get_predict')
def predict_data():
	"""Get all Predictions in database
	return:
		json
	"""
	pjs =  make_predict_json()
	reals =  make_real_json()
	m = [pjs[0],pjs[1],reals[0],reals[1]]
	return render_template('json.html',msg=json.dumps(m)
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

class InitialParameters(object):
	"""Initalize Media Paramter of beginning time
	"""
	FF = [ 0.95, 0.97, 0.99 ]

	def __init__(self, start_year, start_month):
		self.start_year = start_year
		self.start_month = start_month

	def __generate_beta(self, size, mu=0, sigma=1):
		beta = {}
		for i in self.FF:
			beta[i] = []
			for j in range(0, size):
				beta[i].append(random.normalvariate(mu, sigma))
		return beta

	def __generate_p(self, size, mu=0, sigma=1):
		p = {}
		for i in self.FF:
			p[i] = [[0 for m in range(0, size)] for k in range(0, size)]
			for j in range(0, size):
				p[i][j][j] = random.normalvariate(mu, sigma)
		return p

	def __generate_mps(self):
                mps = []
                betas = {
                    'tmem1': self.__generate_beta(3),
                    'tmemean': self.__generate_beta(3),
                    'tme': self.__generate_beta(3),
                    'tmep1': self.__generate_beta(4),
                    'mmem1': self.__generate_beta(4),
                    'mme': self.__generate_beta(2),
                    'mmep1': self.__generate_beta(4),
                } # generate beta of each model
                ps = {
                    'tmem1': self.__generate_p(3),
                    'tmemean': self.__generate_p(3),
                    'tme': self.__generate_p(3),
                    'tmep1': self.__generate_p(4),
                    'mmem1': self.__generate_p(4),
                    'mme': self.__generate_p(2),
                    'mmep1': self.__generate_p(4),
                } # generate p of each model
                for ff in self.FF:
                	for key in betas.keys():
                		mps.append(MediaParamter(self.start_year, self.start_month,\
                			key, str(betas[key]), str(ps[key]), ff))
                return mps

    	def run(self):
    		for mp in self.__generate_mps():
    			print mp.year
    			db.session.add(mp)
    		db.session.commit()

def init_db():
	db.create_all()
	init_dict_tables()
	InitialParameters(app.config['START_YEAR'], app.config['START_MONTH']).run()

def drop_db():
	db.drop_all()

def year_month_sort(year_months):
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

def make_real_json():
	#get real
	fq = FactQuery()
	me_facts = fq.get_me_facts()

	memos_values = []
	trasaction_values = []
	keys = year_month_sort(me_facts.keys())
	for key in keys:
		memos = {}
		trasaction = {}
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
	keys = year_month_sort(pre_facts.keys())
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

def _get_data_map(dlist,dtype,is_predict):
	m = {}
	m['endMonth'] = dlist[0]['month']
	m['startMonth'] = dlist[len(dlist)-1]['month']
	m['isPredict'] = is_predict;
	m['type'] = dtype
	m['values'] = dlist
	return m

def predict():
	fq = FactQuery()
	nt = NewTest()
	results = nt.run(fq.get_data(),fq.get_months(),fq.get_me_facts())
	for p in results:
		predict = Prediction(p['year'],p['month'],p['value'],p['model_type'],p['ff'])
		db.session.add(predict)
	db.session.commit()

if __name__ == '__main__':
	app.run()

	
