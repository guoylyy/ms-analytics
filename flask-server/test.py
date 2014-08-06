from app import *
import pickle


def get_real(real_data, year_month):
	key = "%s-%s" % year_month
	y_list = real_data[key]
	y = {}
	all_me = 0
	for f in y_list:
	    all_me = all_me + f[1]
	    if f[0] == 'ME':
	        y['mme'] = f[2]
	        y['tme'] = f[1]
	    elif f[0] == 'ME+1':
	        y['mmep1'] = f[2]
	        y['tmep1'] = f[1]
	    elif f[0] == 'ME-1':
	        y['mmem1'] = f[2]
	        y['tmem1'] = f[1]
	y['tmemean'] = all_me/3	
	print y


if __name__ == '__main__':
	#pq = PredictionQuery()
	#print pq.get_lastest_date()
	fq = FactQuery()
	nt = NewTest()

	#print fq.get_months()
	#results = nt.run(fq.get_data(),fq.get_months(),fq.get_me_facts())
	#-----------------------
	# Dump data to outsite
	#-----------------------
	facts = fq.get_me_facts()
	real_data = {}
	for key in facts.keys():
		fs = facts[key]
		l = []
		for f in fs:
			tf = [f.me, f.trasaction,f.memos]
			l.append(tf)
		real_data[key] = l
	#print real_data 
	pickle.dump(fq.get_data(), open('test', 'w'))
	pickle.dump(real_data, open('real_data', 'w'))
	#get_real(real_data,(2014,3))


	
