# udp-file-transfer
CS 457 Project 4 - Reliable File Transfer over UDP

4/5/2016 NOTES:
-implement a "sliding window" - how reliability is implemented
-say we have packets we want to send 
 1 2 3 4 5 6 7 8 9 10
|_________|_ window is 5 packets long
 starts to send packets in the window
 - got ack for 1. window now becomes 2-6. 
 - got ack for 3(w/o ack for 2). window should stay the same.
 - got ack for 2. window now becomes 4-8.

-using regular udp sockets
-using mininet b/c we want to simulate packet loss. To effectively test this thing.

Demoing mininet:
sudo mn -x
default configuration: h1--s1--h2
run on switch: tc qdisc add dev s1-eth1 root netem loss 30%
                        change // if anything has changed
to make sure prgm is losing packets: ping and look at icmp_seq

run on switch: tc qdisc add dev s1-eth1 root netem delay 1000ms reorder 20%

run on switch: tc qdisc add dev s1-eth1 root netem delay 1000ms reorder 20% loss 10%

sudo mn -x --controller=remote

on controller: cd pox/
               ./pox.py packetcorrupt
