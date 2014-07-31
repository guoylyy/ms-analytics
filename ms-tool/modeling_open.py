#!/ms/dist/python/PROJ/core/2.7.3-64/bin/python
# _*_ coding: utf-8 _*_

#import ms.version
#ms.version.addpkg('numpy', '1.7.1-mkl-py27-64')
import os
import csv
import math
import random
import datetime
import calendar
import traceback
import numpy as np

############################## Internal Functions ############################
def _next_year_month(year_month):
    dt = datetime.datetime(year=year_month[0],month=year_month[1],day=28) + datetime.timedelta(days=10)
    return (dt.year,dt.month)


def _str2date(string):
    return datetime.datetime.strptime(string, '%m/%d/%Y')

def _date2str(date):
    return date.strftime('%m/%d/%Y')

def _medate(year, month, weekend=False):
    tmp = calendar.monthrange(year, month)
    medate = _str2date('%d/%d/%d' % (month, tmp[1], year))
    if not weekend:
        weekday = medate.date().weekday()
        if weekday in [5, 6]:
            medate -= datetime.timedelta(days=weekday-4)
    return medate

def _premonth(year_month, N=1):
    year, month = year_month
    year, month = year, month-N
    while month <= 0:
        year, month = year-1, month+12
    return year, month

def _postmonth(year_month, N=1):
    year, month = year_month
    year, month = year, month+N
    while month > 12:
        year, month = year+1, month-12
    return year, month

def _preworkday(currdate):
    # Return datetime of previous workday
    predate = currdate - datetime.timedelta(days=1)
    weekday = predate.date().weekday()
    if weekday in [5, 6]:
        predate -= datetime.timedelta(days=weekday-4)
    return predate

def _postworkday(currdate):
    # Return datetime of post workday
    postdate = currdate + datetime.timedelta(days=1)
    weekday = postdate.date().weekday()
    if weekday in [5, 6]:
        postdate += datetime.timedelta(days=7-weekday)
    return postdate


############################## Class Maths ###################################

class Maths:
    def score_lm(self, beta, x):
        """Calculate prediction by multiplying x(vector) and beta(vector).
        Args:
            beta: list of floats (1*N).
            x: list of floats (1*N).
        Returns:
            float
        """
        if len(beta) != len(x):
            raise Exception('[ERROR] Length of beta and x are not equal.')
        return sum(map(lambda a,b:a*b, beta, x))

    def recursive_lm(self, beta_old, p_old, ff, x_new, y_new):
        """Calcualte recursive linear model.
        Args:
            beta_old: list of floats (1*N).
            p_old: list of float lists (N*N).
            ff: float. forgetting factor.
            x_new: list of floats (1*N).
            y_new: float.
        Returns:
            Dict of result which looks like:
            {
              'beta': list of floats (1*N).
              'P': list of float lists (N*N).
            }
        """
        x_new = np.matrix(x_new, dtype=float)
        beta_old = np.matrix(beta_old, dtype=float).T
        p_old = np.matrix(p_old, dtype=float)
        eye = np.matrix(np.eye(len(x_new)))
        l = p_old * x_new.T / (ff + x_new * p_old * x_new.T)
        p_new = (eye - l * x_new) / ff * p_old
        beta_new = beta_old + l * (y_new - x_new * beta_old)
        return {
            'beta': beta_new.T.tolist()[0],
            'p': p_new.tolist()
        }

    def ape(self, actual, forecast):
        """Calculate APE for each pair of data.
        Args:
            actual: list of floats (1*N).
            forecast: list of floats (1*N).
        Returns:
            list.
        """
        func = lambda a,f: math.fabs((a - f) / a)
        return map(func, actual, forecast)


############################## Class Model ###################################

class Model(Maths):

    def predict(self, beta, data, year_month, para=None):
        """Do prediction for a single model.
        Args:
            beta: {0.95: list, 0.97: list, 0.99: list} (3*1*N).
            data: [[str_date, float], ...] (2*M).
            year_month: (int, int). 
            para: dict. It depends.
        Returns:
            {
                'x': list (1*N),
                'y': {0.95: float, 0.97: float, 0.99: float}
            }
            values of 'x' and 'y' will be None if prediction has error.
        """
        data = [(_str2date(i[0]), float(i[1])) for i in data]
        result = {'x': None, 'y': None}
        try:
            result['x'] = self._x_cal(year_month, data, para)
        except:
            print traceback.format_exc()
            return result
        result['y'] = {}
        for i in [0.95, 0.97, 0.99]:
            result['y'][i] = self.score_lm(beta[i], result['x'])
        return result

    def revise(self, beta_old, p_old, x_new, y_pred, y_new):
        """Do revision for a single model.
        Args:
            beta_old: {0.95: list, 0.97: list, 0.99: list} (3*1*N).
            p_old: {0.95: list*list, 0.97: list*list, 0.99: list*list} (3*N*N)
            x_new: list of floats (1*N).
            y_pred: float.
            y_new: float.
        Returns:
            {
                'beta': {0.95: list, 0.97: list, 0.99: list} (3*1*N).
                'p': {0.95: list*list, 0.97: list*list, 0.99: list*list}
                'ape': {0.95: float, 0.97: float, 0.99: float}
            }
        """
        for i in [beta_old, p_old, x_new, y_pred, y_new]:
            if i is None:
                print i
                return {
                    'beta': None,
                    'p': None,
                    'ape': None
                }
        beta_old = beta_old[0.95]
        p_old = p_old[0.95]
        result = {}
        for ff in [0.95, 0.97, 0.99]:
            result[ff] = self.recursive_lm(beta_old, p_old, ff, x_new, y_new)
        beta_new, p_new, ape = {}, {}, {}
        for i in [0.95, 0.97, 0.99]:
            beta_new[i] = result[i]['beta']
            p_new[i] = result[i]['p']
            ape[i] = self.ape([y_new], [y_pred[i]])[0]
        return {
            'beta': beta_new,
            'p': p_new,
            'ape': ape
        }

    def _checkdata(self, currdate, data, pre=True):
        month = currdate.month
        data = dict(data)
        while not data.has_key(currdate) and currdate.month == month:
            if pre: currdate = _preworkday(currdate)
            else: currdate = _postworkday(currdate)
        return currdate if currdate.month == month else None

    def _x_cal(self, year_month, data, para=None):
        """Must be override in inherited class."""
        pass

    def _x_5dayaver(self, year_month, data):
        """
        Args:
            year_month: (int, int).
            data: list of rows ([[date, x], ...]).
        """
        year, month = year_month
        me = self._checkdata(_medate(year, month), data)
        me_m1 = self._checkdata(_preworkday(me), data)
        currdate = self._checkdata(_preworkday(me_m1), data) # me-2
        value = 0.0
        for i in range(5):
            value += dict(data)[currdate]
            currdate = self._checkdata(_preworkday(currdate), data)
        return value / 5

    def _x_week2date(self, year_month, data):
        """Average value of rest of days(same week) before ME-1.
        """
        year, month = year_month
        me = self._checkdata(_medate(year, month), data)
        me_m1 = self._checkdata(_preworkday(me), data)
        currdate = self._checkdata(_preworkday(me_m1), data) # me-2
        N = currdate.date().weekday()
        count, data = 1, dict(data)
        value = data[currdate]
        for i in range(N):
            currdate -= datetime.timedelta(days=1)
            if data.has_key(currdate):
                value += data[currdate]
                count += 1
        return value / count

    def _x_monthaver(self, year_month, data):
        """Average value from ME+2 to ME-2."""
        year, month = year_month
        me = self._checkdata(_medate(year, month), data)
        me_m1 = self._checkdata(_preworkday(me), data) # me-1
        me_p1 = self._checkdata(_str2date('%d/1/%d'%(month, year)), data, 
                                False) # me+1
        currdate = self._checkdata(_postworkday(me_p1), data, False) # me+2
        count, value, data = 0, 0.0, dict(data)
        while currdate < me_m1:
            if data.has_key(currdate):
                value += data[currdate]
                count += 1
            currdate = self._checkdata(_postworkday(currdate), data, False)
        return value / count

    def _x_lastqtme(self, year_month, data):
        year, month = year_month
        qyear, qmonth = year, month-3
        if qmonth <= 0:
            qyear, qmonth = year-1, qmonth+12
        me = self._checkdata(_medate(qyear, qmonth), data)
        return dict(data)[me]

    def _x_mem4(self, year_month, data):
        """ME-4."""
        year, month = year_month
        me = self._checkdata(_medate(year, month), data)
        currdate = me
        for i in range(4):
            currdate = self._checkdata(_preworkday(currdate), data)
        if currdate.month != month:
            raise Exception('ME-4(%d%d) not exists in data.'%year_month)
        return dict(data)[currdate]

    def _x_initialpred(self, year_month, data):
        """Calculate initial-pred value of ME+1 of month k."""
        # ME+1(k), ME+1(k-1), ME+1(k-2)
        t = year_month, _premonth(year_month), _premonth(year_month, 2)
        # m(k), m(k-1), m(k-2)
        mep1 = []
        for i in range(3):
            firstday = _str2date('%d/1/%d' % (t[i][1], t[i][0]))
            d = self._checkdata(firstday, data, False)
            mep1.append(dict(data)[d] if d else 0)
        if mep1 == [0, 0, 0]:
            raise Exception('Cannot calcualte intial pred.')
        # d(k), d(k-1)
        diff = []
        for i in range(2):
            if mep1[i] == 0 or mep1[i+1] == 0:
                diff.append(0)
            else:
                diff.append(mep1[i]-mep1[i+1])
        # p(k+1)
        if diff[1] == 0:
            pdiff = diff[0]
        else:
            pdiff = 0.3*diff[0] + 0.7*diff[1]
        return mep1[0] + pdiff
        

class TMem1Model(Model):

    def _x_cal(self, year_month, data, para=None):
        return [
            1,
            self._x_5dayaver(year_month, data),
            self._x_week2date(year_month, data)
        ]

class TMemeanModel(Model):
    
    def _x_cal(self, year_month, data, para=None):
        return [
            1,
            self._x_monthaver(year_month, data),
            self._x_5dayaver(year_month, data)
        ]

class TMeModel(Model):
    
    def _x_cal(self, year_month, data, para=None):
        """
        Args:
            para: { 0.95: float, 0.97: float, 0.99: float }
        """
        return [
            1,
            self._x_lastqtme(year_month, data),
            para[0.95]
        ]

class TMep1Model(Model):
    
    def _x_cal(self, year_month, data, para=None):
        return [
            1,
            self._x_5dayaver(year_month, data),
            self._x_mem4(year_month, data),
            self._x_initialpred(year_month, data)
        ]

class MMem1Model(Model):
      
    def _x_cal(self, year_month, data, para=None):
        """
        Args:
            para: [
                float (trans me-1 week2date),
                float (trans me-1 5dayaver)
            ]
        """
        return [
            1,
            self._x_week2date(year_month, data),
            para[2],
            para[1]
        ]
        
class MMeModel(Model):
    
    def _x_cal(self, year_month, data, para=None):
        return [
            1,
            self._x_5dayaver(year_month, data)
        ]

class MMep1Model(Model):
      
    def _x_cal(self, year_month, data, para=None):
        """
        Args:
            para: { 0.95: float, 0.97: float, 0.99: float }
        """
        return [
            1,
            self._x_5dayaver(year_month, data),
            self._x_mem4(year_month, data),
            para[0.95]
        ]

class Modeling:
    
    def do_predict(self, beta, data, year_month):
        """
        Args:
            beta: {
                'tmem1': {0.95: list, 0.97: list, 0.99: list},
                'tmemean': ...
                'tme': ...
                'tmep1': ...
                'mmem1': ...
                'mme': ...
                'mmep1': ...
            }
            data: [
                [str_date, trans_value, memo_value],
                ...
            ]  that is M rows data
            year_month: (int_year, int_month)
        Returns:
            {
                'tmem1': {
                    'x': list
                    'y': {0.95: float, 0.97: float, 0.99: float}
                },
                ... // 6 other models
            }
        """
        result = {}
        tdata = [(i[0], i[1]) for i in data]
        result['tmem1'] = TMem1Model().predict(beta['tmem1'], tdata, year_month)
        result['tmemean'] = TMemeanModel().predict(beta['tmemean'], tdata, 
                year_month)
        result['tme'] = TMeModel().predict(beta['tme'], tdata, year_month,
                result['tmemean']['y'])
        result['tmep1'] = TMep1Model().predict(beta['tmep1'], tdata, year_month)
        mdata = [(i[0], i[1]) for i in data]
        result['mmem1'] = MMem1Model().predict(beta['mmem1'], mdata, 
                year_month, result['tmem1']['x'])
        result['mme'] = MMeModel().predict(beta['mme'], mdata, year_month)
        result['mmep1'] = MMep1Model().predict(beta['mmep1'], mdata, 
                year_month, result['mme']['y'])
        return result

    def do_revise(self, beta, p, x, y_pred, y):
        """
        Args:
            beta: {
                'tmem1': {0.95: list, 0.97: list, 0.99: list},
                'tmemean': ...
                'tme': ...
                'tmep1': ...
                'mmem1': ...
                'mme': ...
                'mmep1': ...
            }
            p: {
                'tmem1': {0.95: list*list, 0.97: list*list, 0.99: list*list},
                ... // other 6 models
            }
            x: {
                'tmem1': list,
                ... // other 6 models
            }
            y_pred: similar to x
            y: actual value, similar to x
            year_month: (int_year, int_month)
        """
        func = {
            'tmem1': TMem1Model().revise, 
            'tmemean': TMemeanModel().revise, 
            'tme': TMeModel().revise, 
            'tmep1': TMep1Model().revise, 
            'mmem1': MMem1Model().revise, 
            'mme': MMeModel().revise, 
            'mmep1': MMep1Model().revise
        }
        result = {}
        for i in func.keys():
            f = func[i]
            result[i] = f(beta[i], p[i], x[i], y_pred[i], y[i])
        return result



################################### TEST ######################################
class Test(object):
    
    FF = [0.95, 0.97, 0.99] #this is forget factor
    
    def generate_data(self, month, mu=10, sigma=4):
        tmp = calendar.monthrange(2014, month)
        data = []
        for i in range(1, tmp[1]+1):
            d1 = '%d/%d/2014' % (month, i)
            d2 = random.normalvariate(mu, sigma)
            d3 = random.normalvariate(mu, sigma)
            data.append([d1, d2, d3])
        return data

    def generate_beta(self, size, mu=0, sigma=1):
        beta = {}
        for i in Test.FF:
            beta[i] = []
            for j in range(0, size):
                beta[i].append(random.normalvariate(mu, sigma))
        return beta

    def generate_p(self, size, mu=0, sigma=1):
        p = {}
        for i in Test.FF:
            p[i] = [[0 for m in range(0, size)] for k in range(0, size)]
            for j in range(0, size):
                p[i][j][j] = random.normalvariate(mu, sigma)
        return p
        
    def test_model(self):
        data = self.generate_data(1)
        beta = self.generate_beta(3)
        p = self.generate_p(3)       
        print beta
        print p

    def test_tmem1(self):
        print '=============== trans me-1 ==============='
        data = self.generate_data(1)
        beta = self.generate_beta(3)
        p = self.generate_p(3)       
        m = TMem1Model()
        rp = m.predict(beta, data, (2014, 1))
        rr = m.revise(beta, p, rp['x'], rp['y'], 11)
        return rp

    def test_tmemean(self):
        print '=============== trans me mean ==============='
        data = self.generate_data(1)
        beta = self.generate_beta(3)
        p = self.generate_p(3)       
        m = TMemeanModel()
        rp = m.predict(beta, data, (2014, 1))
        rr = m.revise(beta, p, rp['x'], rp['y'], 11)
        return rp

    def test_tme(self, memean):
        print '=============== trans me ==============='
        data = self.generate_data(1)
        data.extend(self.generate_data(2))
        data.extend(self.generate_data(3))
        data.extend(self.generate_data(4))
        beta = self.generate_beta(3)
        p = self.generate_p(3)       
        m = TMeModel()
        rp = m.predict(beta, data, (2014, 4), memean)
        rr = m.revise(beta, p, rp['x'], rp['y'], 11)
        print rp
        print rr

    def test_tmep1(self):
        print '=============== trans me+1 ==============='
        data = self.generate_data(1)
        data.extend(self.generate_data(2))
        data.extend(self.generate_data(3))
        data.extend(self.generate_data(4))
        beta = self.generate_beta(4)
        p = self.generate_p(4)       
        m = TMep1Model()
        rp = m.predict(beta, data, (2014, 4))
        rr = m.revise(beta, p, rp['x'], rp['y'], 11)
        print rp
        print rr

    def test_mmem1(self, mem1):
        print '=============== memo me-1 ==============='
        data = self.generate_data(1)
        beta = self.generate_beta(4)
        p = self.generate_p(4)
        m = MMem1Model()
        rp = m.predict(beta, data, (2014, 1), mem1)
        rr = m.revise(beta, p, rp['x'], rp['y'], 11)
        print rp
        print rr

    def test_mme(self):
        print '=============== memo me ==============='
        data = self.generate_data(1)
        beta = self.generate_beta(2)
        p = self.generate_p(2)
        m = MMeModel()
        rp = m.predict(beta, data, (2014, 1))
        rr = m.revise(beta, p, rp['x'], rp['y'], 11)
        return rp

    def test_mmep1(self, mme):
        print '=============== memo me+1 ==============='
        data = self.generate_data(1)
        beta = self.generate_beta(4)
        p = self.generate_p(4)
        m = MMep1Model()
        rp = m.predict(beta, data, (2014, 1), mme)
        rr = m.revise(beta, p, rp['x'], rp['y'], 11)
        print rp
        print rr

    def test_modeling(self):
        print '=============== modeling ==============='
        data = self.generate_data(1)
        data.extend(self.generate_data(2))
        data.extend(self.generate_data(3))
        data.extend(self.generate_data(4))
        
        beta = {
            'tmem1': self.generate_beta(3),
            'tmemean': self.generate_beta(3),
            'tme': self.generate_beta(3),
            'tmep1': self.generate_beta(4),
            'mmem1': self.generate_beta(4),
            'mme': self.generate_beta(2),
            'mmep1': self.generate_beta(4),
        }
        p = {
            'tmem1': self.generate_p(3),
            'tmemean': self.generate_p(3),
            'tme': self.generate_p(3),
            'tmep1': self.generate_p(4),
            'mmem1': self.generate_p(4),
            'mme': self.generate_p(2),
            'mmep1': self.generate_p(4),
        }

        result1 = Modeling().do_predict(beta, data, (2014, 4))
        for k in result1:
            print k
            print 'x:' + ' ' * 2 + str(result1[k]['x'])
            print 'y:' + ' ' * 2 + str(result1[k]['y'])

        x, y_pred, y = {}, {}, {}
        for i in result1.keys():
            x[i] = result1[i]['x']
            y_pred[i] = result1[i]['y']
            y[i] = 10

        result2 = Modeling().do_revise(beta, p, x, y_pred, y)
        for k in result2:
            print k
            print 'beta:' + ' ' * 2 + str(result2[k]['beta'])
            print 'p:' + ' ' * 2 + str(result2[k]['p'])


class DataPrepare(object):
    def __init__(self, filepath):
        self.filepath = filepath
        self.__loadfile()

    def __loadfile(self):
        reader = csv.reader(file(self.filepath, 'r'))
        data_list = []
        date_list = []
        data_map = {}
        for i in reader:
            data = []
            date_list.append(_str2date(i[0]))
            data.append(i[0])
            data.append(float(i[2]))
            data.append(float(i[3]))
            data_list.append(data)
            data_map[i[0]] = i
        self.data_list = data_list
        self.date_list = sorted(date_list)
        self.data_map = data_map
        
    def get_data(self):
        return self.data_list

    def get_data_map(self):
        return self.data_map    

    def get_start_date(self):
        return self.date_list[0]

    def get_end_date(self):
        return self.date_list[len(self.date_list)-1]

    def test(self):
        print 'data map key: %s' % self.data_map.keys()
        print 'start date: %s ' % self.get_start_date()
        print 'end date: %s ' % self.get_end_date()

class NewTest(object):
    def __init__(self):
        print '=====Start New Test'

    def generate_beta(self, size, mu=0, sigma=1):
        beta = {}
        for i in Test.FF:
            beta[i] = []
            for j in range(0, size):
                beta[i].append(random.normalvariate(mu, sigma))
        #print beta
        return beta

    def generate_p(self, size, mu=0, sigma=1):
        p = {}
        for i in Test.FF:
            p[i] = [[0 for m in range(0, size)] for k in range(0, size)]
            for j in range(0, size):
                p[i][j][j] = random.normalvariate(mu, sigma)
        return p

    def run(self,data,months,me_facts):
        #filepath = "uploads/data.csv"
        data = data
        beta = {
            'tmem1': self.generate_beta(3),
            'tmemean': self.generate_beta(3),
            'tme': self.generate_beta(3),
            'tmep1': self.generate_beta(4),
            'mmem1': self.generate_beta(4),
            'mme': self.generate_beta(2),
            'mmep1': self.generate_beta(4),
        }
        p = {
            'tmem1': self.generate_p(3),
            'tmemean': self.generate_p(3),
            'tme': self.generate_p(3),
            'tmep1': self.generate_p(4),
            'mmem1': self.generate_p(4),
            'mme': self.generate_p(2),
            'mmep1': self.generate_p(4),
        }
        months = months[4:]
        index = 0 
        final_list = []
        for year_month in months:
            index = index + 1
            print "%s-%s" %(year_month)
            next_month = _next_year_month(year_month)
            print next_month
            result1 = Modeling().do_predict(beta, data, year_month)
            for k in result1:
                #print k
                #print 'x:' + ' ' * 2 + str(result1[k]['x'])
                print 'y:' + ' ' * 2 + str(result1[k]['y'])
                for key in result1[k]['y'].keys():
                    m = {}
                    m['year'] = next_month[0]
                    m['month'] = next_month[1]
                    m['model_type'] = k
                    m['value'] = (float)("%0.2f"%result1[k]['y'][key])
                    m['ff'] = key
                    final_list.append(m)

            if(index==len(months)):
                break
            x, y_pred, y = {}, {}, {}
            for i in result1.keys():
                x[i] = result1[i]['x']
                y_pred[i] = result1[i]['y']

            y = self.get_real(me_facts,months[index])
            
            result2 = Modeling().do_revise(beta, p, x, y_pred, y)
            for k in result2:
                beta[k] = result2[k]['beta']
                p[k] = result2[k]['p']
                #print k
                #print 'beta:' + ' ' * 2 + str(result2[k]['beta'])
                #print 'p:' + ' ' * 2 + str(result2[k]['p'])        
            print '==========='
        return final_list
    
    def get_real(self,me_facts,year_month):
        key = "%s-%s" % year_month
        y = {}
        all_me = 0
        for f in me_facts[key]:
            all_me = all_me + f.trasaction
            if f.me == 'ME':
                y['mme'] = f.memos
                y['tme'] = f.trasaction
            elif f.me == 'ME+1':
                y['mmep1'] = f.memos
                y['tmep1'] = f.trasaction
            elif f.me == 'ME-1':
                y['mmem1'] = f.memos
                y['tmem1'] = f.trasaction
        y['tmemean'] = all_me/3
        return y


#def main():
    #t = Test()
    #t.test_model()
    #tmem1 = t.test_tmem1()['x']
    #tmemean = t.test_tmemean()['y']
    #t.test_tme(tmemean)
    #t.test_tmep1()
    #t.test_mmem1(tmem1)
    #mme = t.test_mme()['y']
    #t.test_mmep1(mme)
    #t.test_modeling()
    
    #tt = NewTest()
    #tt.run()
    #filepath = 'uploads/data.csv'
    #DataPrepare(filepath).test()



if __name__ == '__main__':
    main()

