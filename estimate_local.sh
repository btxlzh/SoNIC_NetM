#! /bin/bash
sender_user="yicheng"
sender_host="sonic2.cs.cornell.edu" 
sender_sonic_path="~/sonic/driver"

receiver_user="yicheng"
receiver_host="sonic3.cs.cornell.edu"
receiver_sonic_path="~/sonic/driver"

probe=1472
srate=1
erate=96
step=1
gap=120000
chirp=20
repeat=10
sfreq=50000000
scnt=5
cut=5
linear_err=2
mac_src="00:60:dd:45:39:0d"
src_mac=$(echo $mac_src | tr -d ":")
mac_dst="00:60:dd:45:39:5a"
dst_mac=$(echo $mac_dst | tr -d ":")
ip_src="192.168.4.12"
ip_dst="192.168.4.13"
port_src=5000
port_dst=5008
send_dur=9
recv_dur=12
send_mode=pkt_rpt,pkt_cap
recv_mode=pkt_cap,pkt_cap

srate_r=$(echo "$srate/10.0" | bc -l )
erate_r=$(echo "$erate/10.0" | bc -l )
step_r=$(echo "$step/10.0" | bc -l )
probe_file="probe"
file=probe_${probe}_srate_${srate}_erate_${erate}_step_${step}_gap_${gap}_chirp_${chirp}_run_${repeat}_sfreq_${sfreq}_scnt_${scnt}.log
process_file="raw_pkts"

ssh $sender_user@$sender_host python $sender_sonic_path/bin/chirp.py -o $probe_file -l $probe -n $chirp -i $gap -f $srate_r -e $erate_r -d $step_r -r $repeat -s $scnt -g $sfreq 

 
ssh $sender_user@$sender_host sh $sender_sonic_path/bin/run_sonic.sh -m $send_mode -d $send_dur -r $probe_file --ip_src $ip_src --ip_dst $ip_dst --mac_src $mac_src --mac_dst $mac_dst --port_src $port_src --port_dst $port_dst &

ssh $receiver_user@$receiver_host sh $receiver_sonic_path/bin/run_sonic.sh -m $recv_mode -p $process_file --mac_src $mac_src --mac_dst $mac_dst -d $recv_dur

scp $receiver_user@$receiver_host:~/$process_file.info $file

srate=$(echo "$srate/10.0" | bc -l )
erate=$(echo "$erate/10.0" | bc -l )
step=$(echo "$step/10.0" | bc -l )

python process.py -a $file -l $probe -n $chirp -i $gap -f $srate -e $erate -d $step -r $repeat -s $scnt -g $sfreq

python calc_q_delay.py -a $file.processed -l $probe -n $chirp -i $gap -f $srate -e $erate -d $step -r $repeat -s $scnt -g $sfreq

mean_file=$file.processed.stats.mean

python graph.py $mean_file $cut $linear_err
