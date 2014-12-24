import sys
file = 'cross.tmp'
def compute_idle(plen, rate):
    x = (plen) * 10 / rate - plen

    x = (int(x) & ~3) + ((4 - plen %4) & 3)

    #print('{} {} {}'.format(plen, rate, x))

    return x
r=float(sys.argv[1])

t=sys.argv[2]
x= str(compute_idle(1472,r))+'\n'
with open(file, 'w') as f:
	for i in range (0, 3000000):
		text = str(i) + " 1 1472 "+x
		f.write(text)

