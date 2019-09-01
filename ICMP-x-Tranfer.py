#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import os
import struct
import time
from socket import *

# From /usr/include/linux/icmp.h; your milage may vary.
ICMP_ECHO_REQUEST = 8 # Seems to be the same on Solaris.

if sys.platform == "win32":
    # On Windows, the best timer is time.clock()
    default_timer = time.clock
else:
    # On most other platforms the best timer is time.time()
    default_timer = time.time

def show_usage ():
    print """
      USAGE:
        icmp.py <file to transfer> <remote address>
    """
    exit()
            
def send_file(s_filename, dst_addr):
    _file = open(s_filename, 'r')
    seq_n = 0
    while True: 
        data = _file.read(56)
        CODE=0
        ID = os.getpid() & 0xffff
        my_checksum = 0
        if not data:
            ###################################### Send finish ping ##########################################
            # Header is type (8), code (8), checksum (16), id (16), sequence (16)
            CODE=2
            # Make a dummy heder with a 0 checksum.
            header_fmt = 'bbHHh'
            payload_fmt = '%ds' % (56)
            packet_fmt = '!' + header_fmt + payload_fmt
            packet = struct.pack(packet_fmt, ICMP_ECHO_REQUEST, CODE, my_checksum, ID, seq_n,str(data))

            # Calculate the checksum on the data and the dummy header.
            my_checksum = checksum(packet)

            # Now that we have the right checksum, we put that in. It's just easier
            # to make up a new header than to stuff it into the dummy.
            packet = struct.pack(packet_fmt, ICMP_ECHO_REQUEST, CODE, my_checksum, ID, seq_n,str(data))
            
            my_socket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP) 
            my_socket.sendto(packet, (dst_addr, 1)) # Don't know about the 1
            # packet = IcmpPacket(ECHO_REQUEST, seq_n=seq_n, payload=data, code=2)            
            ##################################################################################################
            break
        #############################################################################################
        # Header is type (8), code (8), checksum (16), id (16), sequence (16)
        # Make a dummy heder with a 0 checksum.
        header_fmt = 'bbHHh'
        payload_fmt = '%ds' % (56)
        packet_fmt = '!' + header_fmt + payload_fmt
        packet = struct.pack(packet_fmt, ICMP_ECHO_REQUEST, CODE, my_checksum, ID, seq_n,str(data))

        # Calculate the checksum on the data and the dummy header.
        my_checksum = checksum(packet)

        # Now that we have the right checksum, we put that in. It's just easier
        # to make up a new header than to stuff it into the dummy.
        packet = struct.pack(packet_fmt, ICMP_ECHO_REQUEST, CODE, my_checksum, ID, seq_n,str(data))
        
        my_socket = socket(AF_INET, SOCK_RAW, IPPROTO_ICMP) 
        my_socket.sendto(packet, (dst_addr, 1)) # Don't know about the 1
        # packet = IcmpPacket(ECHO_REQUEST, seq_n=seq_n, payload=data, code=0)
        ############################################################################################

        seq_n += 1
    _file.close()
        

def checksum(source_string):
    """
    I'm not too confident that this is right but testing seems
    to suggest that it gives the same answers as in_cksum in ping.c
    """
    sum = 0
    countTo = (len(source_string)/2)*2
    count = 0
    while count<countTo:
        thisVal = ord(source_string[count + 1])*256 + ord(source_string[count])
        sum = sum + thisVal
        sum = sum & 0xffffffff # Necessary?
        count = count + 2

    if countTo<len(source_string):
        sum = sum + ord(source_string[len(source_string) - 1])
        sum = sum & 0xffffffff # Necessary?

    sum = (sum >> 16)  +  (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff

    # Swap bytes. Bugger me if I know why.
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer

if __name__ == '__main__':
    try:
        s_filename = sys.argv[1]
        dst_addr = sys.argv[2]
    except IndexError:
        show_usage()
    send_file(s_filename,dst_addr)
