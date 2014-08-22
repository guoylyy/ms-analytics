
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

if __name__ == '__main__':
    main()