#!/usr/bin/python
import sys, os, getopt, math, argparse, string, pickle
import numpy as np

def gen_sent_gaps(gap, cnt):
    sent_gap = []
    for i in range(0, cnt):
        sent_gap.append(gap)
    return sent_gap

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
    parser = argparse.ArgumentParser(description='Analyzing captured data')
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
	dummy = f.readline()
        content = f.readlines()

    #generate gap array
    tmp = []
    stats = [] 
    data_val=[]
    cross_index = []
    probe_len=args.pkt_cnt;
    cnt=0
    #extract received packet gap
    for line in content:
	cnt+=1
	data_val.append(int(line.split()[3]))
	if cnt == probe_len:
		tmp.append(data_val)
		data_val=[]
		cnt=0
    arr = np.asarray(tmp)
    if len(arr) != len(gaps):
        print "lossed packet in sample, quit!"
       

    np.savetxt(args.input+".processed", np.asarray(tmp), "%d")

if __name__ == "__main__":
    main()
