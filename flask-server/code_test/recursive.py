import numpy as np
import math 

def cal(x, y, beta, p, ff=0.95):
    dim = len(x)
    x = np.matrix(x, dtype=float)
    beta = np.matrix(beta, dtype=float).T
    p = np.matrix(p, dtype=float)
    eye = np.matrix(np.eye(dim))
    l = p * x.T / (ff + x * p * x.T)
    p_new = ((eye - l * x) / ff) * p
    b_new = beta + l * (y - x * beta)
    return {
        'p': p_new.tolist(),
        'beta': b_new.T.tolist()[0]
    }

def cal2(x1, y1, beta0, P0, ff=0.95):
    dim = len(x1)
    x1 = np.matrix(x1, dtype=float)
    beta0 = np.matrix(beta0, dtype=float).T
    P0 = np.matrix(P0, dtype=float)
    I = np.matrix(np.eye(dim))
    L1 = P0 * x1.T / (ff + x1 * P0 * x1.T)
    P1 = (I - L1 * x1) / ff * P0
    beta1 = beta0 + L1 * (y1 - x1 * beta0)
    return {
        'p': P1.tolist(),
        'beta': beta1.T.tolist()[0]
    }

def main():
    x1, y1 = [1, 33507808.48, 34516428.95], 77843252.6
    x2, y2 = [1, 31827967.9, 34854129.45], 72410697.1
    x3, y3 = [1, 36186621.62, 39448870.8], 77937740.8
    x4, y4 = [1, 32325407.38, 32325407.38], 79387821.2
    x5,y5 =  [1,33235066.36,34994154.65], 73378609.9
    x6,y6 = [1,42532014.66,44011060.43], 86096332.9
    x7,y7 = [1,32893451.14,34800686.9],79619328.9
    x8,y8 = [1,27317438.18,27661118.83], 74089124.7



    beta0 = [49370077.5454166, 1.66201325669058, -0.794196017693839]
    p0 = [[1e12, 0, 0], [0, 1e12, 0], [0, 0, 1e12]]

    r1 = cal(x1, y1, beta0, p0)
    #print score(beta0, x1)
    print cal_ape(y1,score(beta0, x1))

    for index in range(2,10):
        print '---%s---' % index

        x = 'r'+ str(index)
        pre_x = 'r' + str(index-1)
        exec(x + '=cal(x'+str(index)+', y'+ str(index)+', '+pre_x+'[\'beta\'], '+pre_x+'[\'p\'])')
        exec('print score('+pre_x+'[\'beta\'], x'+str(index)+')')
        exec('print cal_ape(y'+str(index)+', score('+pre_x+'[\'beta\'], x'+str(index)+'))')


    #r1 = cal2(x1, y1, beta0, p0)
    #print '== 1 ==', r1['beta']
    #r2 = cal2(x2, y2, r1['beta'], r1['p'])
    #print '== 2 ==', r2['beta']

def score(beta, x):
    return sum(map(lambda a,b: a*b, beta, x))


def cal_ape(real, predict):
    return math.fabs(real-predict)/real

if __name__ == '__main__':
    main()
