#!/usr/bin/python
import sys, os, getopt, argparse
import numpy as np

verbose=False

def dprint(s):
    if verbose:
	print s

# Approximately compute number of idles required to meet target rate
def compute_idle(plen, rate):
    x = (plen + 8) * 10.0 / rate - plen - 8

    x = (int(x) & ~3) + ((4 - plen %4) & 3)

    dprint('{} {} {}'.format(plen, rate, x))

    return x
def new_calc(d):
    sum=0;
    for x in d:
        if x > 0 :
            sum= sum + x*x
        else :
            sum= sum - x*x
    return sum
  
def generate_chirp_packets(args):
    cur_rate=args.first_rate

    #f=open(args.output, 'w')

    c=0

    chirp_dist = 12
    gaps = []

    for s in range(0, args.sample_cnt):
        cur_rate = args.first_rate
        delta = 12 if chirp_dist <= 12 else chirp_dist
        chirp_dist = args.sample_freq

        while(1):
            for i in range (0, args.repeat):
                idle = compute_idle(args.len, cur_rate)
                if idle < 12 :
                    print '{} Gbps: Not possible'.format(cur_rate)
                    break

                gaps.append(idle)
                
                distance = args.idle

                dprint("{} Gbps: Generating {} {}B packets with {} idles, distance from previous chain is {}".format(cur_rate, args.pkt_cnt, args.len, idle, distance))

            delta = idle if distance < idle else distance

            chirp_dist = chirp_dist - (args.len * args.pkt_cnt + idle * (args.pkt_cnt - 1))
            
            cur_rate += args.delta
            if cur_rate > args.end_rate:
                break

    return gaps
def main():
    parser = argparse.ArgumentParser(description='Analyzing queueing delay')
    parser.add_argument('-a', '--input', type=str,
            help='input file', required=True)
    parser.add_argument('-o', '--output', type=str, default="tmp.info",
            help='Output file, default is tmp.info')
    parser.add_argument('-l', '--len', type=int,
            help='Chirp Packet Length', default='792')
    parser.add_argument('-n', '--pkt_cnt', type=int, default=20,
            help='# of packets in a single chirp chain')
    parser.add_argument('-i', '--idle', type=int,
            help='Distance between the first packets of two chirp chains in # of bytes', default='10000000000')
    parser.add_argument('-f', '--first_rate', type=float, default=0.5,
	    help='The data rate of the first chirp chain')
    parser.add_argument('-e', '--end_rate', type=float, default=9.5,
	    help='The data rate of the last chirp chain')
    parser.add_argument('-d', '--delta', type=float, default=.5,
	    help='The delta rate between ajacent chirp chains')
    parser.add_argument('-r', '--repeat', type=int, default=1,
	    help='Number of repeats for each data rate')
    parser.add_argument('-s', '--sample_cnt', type=int, default=1,
	    help='Number of samples to collect.')
    parser.add_argument('-g', '--sample_freq', type=int, default='10000000000',
	    help='Distance between the first two packets of two samples, in terms of bytes.')
    parser.add_argument('-v', '--verbose', action='store_true', default=False)

    args = parser.parse_args()

    if args.verbose:
        print args

    gaps = generate_chirp_packets(args)
    
    with open(args.input) as f:
        content = f.readlines()

    pct = []
    pdt = []
    diff = []
    stats = []
    phase_plot = []
    cnt = []
    cur_probe_data = []
    cur_probe_data_mean = []
    graph= []
    for idx, line in enumerate(content):
        data = map(lambda x: int(x), line.split(" "))
        #print data
        for _data in data[1:]:
            phase_plot.append([gaps[idx], _data])
        d = map(lambda x: x - gaps[idx], data)
        abs_d = map(lambda x: abs(x - gaps[idx]), data)
        #sum of total gap change
        _sum_d = reduce(lambda x, y: x + y, d[1:])
        _sum_dx= new_calc(d[1:])
        _sum_gap = len(d[1:]) * gaps[idx]
        #print d
        pd = [x-d[i-1] for i, x in enumerate(d)][1:]  # compute pairwise comparison for pathload
        #print pd[1:i]
        _pct = len(filter(lambda x: x > 0, pd[1:])) / float(len(pd)-1) #compute pct
        _dk_d1 = reduce(lambda x, y: x + y, pd[1:])
        _sum_dk = reduce(lambda x, y: abs(x) + abs(y), pd[1:])
        if (_sum_dk == 0):
            _sum_dk = 0.001 #work around, fix later
        _pdt = (float)(_dk_d1) / (float)(_sum_dk) #compute pdt
        
        #count captured cross traffic
        #_cnt = len(filter(lambda x: x > args.size, data[1:]))
        #s = [np.median(d[1:]), np.mean(d[1:]), np.var(d[1:]), _pct, _pdt, np.sum(_cnt), _sum_d, _sum_gap]
        cur_rate = args.first_rate + args.delta * (int(idx / args.repeat) % int((args.end_rate - args.first_rate) / args.delta + 1))
        s = [cur_rate, np.median(d[1:]), np.mean(d[1:]), np.var(d[1:]), np.var(abs_d[1:]), _pct, _pdt, 0, _sum_d, _sum_gap]
        
        diff.append(d)
        stats.append(s)
        pct.append(_pct)
        pdt.append(_pdt)
        #cnt.append(_cnt)
        graph.append([cur_rate,_sum_dx])
        cur_probe_data.append([cur_rate, np.median(d[1:]), np.mean(d[1:]), np.var(d[1:]), np.var(abs_d[1:]), _pct, _pdt, 0, _sum_d, _sum_gap])
        # compute mean over the same probe rate
        if ((idx+1) % args.repeat == 0):
            cur_probe_data_mean.append(np.mean(cur_probe_data, axis=0))
            cur_probe_data = []

    np.savetxt(args.input+".stats", np.asarray(stats), "%10.2f")
    np.savetxt(args.input+".data", np.asarray(diff), "%5d")
    np.savetxt(args.input+".pct", np.asarray(pct), "%.2f")
    np.savetxt(args.input+".pdt", np.asarray(pdt), "%10.2f")
    #np.savetxt(args.input+".cnt", np.asarray(cnt), "%d")
    np.savetxt(args.input+".phaseplot", np.asarray(phase_plot), "%5d")
    np.savetxt(args.input+".stats.mean", np.asarray(cur_probe_data_mean), "%10.2f")
    np.savetxt(args.input+".graph", np.asarray(graph), "%10.2f")
if __name__ == "__main__":
    main()
