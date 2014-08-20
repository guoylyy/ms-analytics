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
