

import sys
import os
import socket
import math
import logging
import logging.handlers


def write_pid(filename):
    """ Write process id to /var/run """
    pid = os.getpid()
    fpid = open(filename, "w")
    fpid.write(str(pid))
    fpid.close()
    return pid

def remove_pid(pidfile):
    os.unlink(pidfile)


def set_logging(logfile, level):
    '''
        set logging handler for logging output to logfile
    '''
    if level == 'debug':
        loglevel = logging.DEBUG
    elif level == 'warning':
        loglevel = logging.WARNING
    elif level == 'error':
        loglevel = logging.ERROR
    else:
        loglevel = logging.INFO
    
    log = logging.getLogger() # get root logger
    log.setLevel(loglevel)
    loghandler = logging.handlers.WatchedFileHandler(filename=logfile)
    frm = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", "%Y-%m-%d %H:%M:%S")
    loghandler.setFormatter(frm)
    log.addHandler(loghandler)

    return log


ether_type_description = { 0x0800 : 'IP',
                           0x0806 : 'ARP',
                           0x8100 : '802.1Q(VLAN)',
                           0x86DD : 'IPv6' }

def ether_type_to_string(ether_type):
    if ether_type in ether_type_description:
        return ether_type_description[ether_type]
    else:
        return 'unknown(0x' + str(ether_type) + ')'
#        return 'unknown(%04X)' % int(ether_type)


def mac_to_string(mac):
    """Returns an Ethernet MAC address in the form
    XX:XX:XX:XX:XX:XX."""

    return ('%02X:%02X:%02X:%02X:%02X:%02X' %
            (mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]))


def ip_to_string(ip):
    """Returns ip as a string in dotted quad notation.
    
        should be replaced by socket.inet_aton or inet_pton
    """
    #ip = socket.ntohl(ip)              # network byte order is big-endian
    return '%d.%d.%d.%d' % (ip & 0xff,
                            (ip >> 8) & 0xff,
                            (ip >> 16) & 0xff,
                            (ip >> 24) & 0xff)


ip_proto_name = { 0 : 'ip',
                  1 : 'icmp',
                  2 : 'igmp',
                  3 : 'ggp',
                  4 : 'ipencap',
                  5 : 'st',
                  6 : 'tcp',
                  8 : 'egp',
                  9 : 'igp',
                  12 : 'pup',
                  14 : 'emcon',
                  17 : 'udp',
                  18 : 'mux',
                  20 : 'hmp',
                  22 : 'xns-idp',
                  27 : 'rdp',
                  29 : 'iso-tp4',
                  31 : 'mfe-nsp',
                  36 : 'xtp',
                  37 : 'ddp',
                  38 : 'idpr-cmtp',
                  41 : 'ipv6',
                  43 : 'ipv6-route',
                  44 : 'ipv6-frag',
                  45 : 'idrp',
                  46 : 'rsvp',
                  47 : 'gre',
                  50 : 'esp',
                  51 : 'ah',
                  57 : 'skip',
                  58 : 'ipv6-icmp',
                  59 : 'ipv6-nonxt',
                  60 : 'ipv6-opts',
                  62 : 'cftp',
                  73 : 'rspf',
                  78 : 'wb-mon',
                  81 : 'vmtp',
                  88 : 'eigrp',
                  89 : 'ospf',
                  93 : 'ax.25',
                  94 : 'ipip',
                  97 : 'etherip',
                  98 : 'encap',
                  103 : 'pim',
                  108 : 'ipcomp',
                  112 : 'vrrp',
                  115 : 'l2tp',
                  118 : 'st',
                  124 : 'isis',
                  128 : 'sscopmce',
                  129 : 'iplt',
                  132 : 'sctp',
                  133 : 'fc',
                  136 : 'udplite' }

def ip_proto_to_string(proto):
    if proto in ip_proto_name:
        return ip_proto_name[proto]
    else:
        return 'unknown(%d)' % proto


def sampletype_to_string(val):
    sampletypes = {
                   1: 'FlowSample',
                   2: 'CountersSample'}
    if val in sampletypes:
        return sampletypes[val]
    else:
        return str(val)


def speed_to_string(speed):
    speed_name = { 10000000 : '10Mb',
                   100000000 : '100Mb',
                   1000000000 : '1Gb',
                   10000000000 : '10Gb' }

    if speed in speed_name:
        return speed_name[speed]
    else:
        return str(speed)


def hexdump_escape(c):
    """Returns c if its ASCII code is in [32,126]."""
    if 32 <= ord(c) <= 126:
        return c
    else:
        return '.'


def hexdump_bytes(buf, stream=sys.stdout):
    """Prints a 'classic' hexdump, ie two blocks of 8 bytes per line,
    to stream."""

    # Various values that determine the formatting of the hexdump.
    # - col_fmt is the format used for an individual value
    # - col_width gives the width of an individual value
    # - off_fmt determines the formatting of the byte offset displayed
    #   on the left.
    # - sep1_width determines how much whitespaces is inserted between
    #   columns 8 and 9.
    # - sep2_width determines the amount of whitespace between column
    #   16 and the ASCII column on the right

    col_fmt = '%02X '
    col_width = 3
    off_fmt = '%%0%dX    ' % int(math.ceil(math.log(len(buf), 16)))
    sep1_width = 3
    sep2_width = 5
    
    # Print all complete 16-byte chunks.
    for blk_idx in range(len(buf) // 16):
        stream.write(off_fmt % (blk_idx * 16))

        for offset in range(8):
            stream.write(col_fmt % buf[blk_idx * 16 + offset])

        stream.write(' ' * sep1_width)

        for offset in range(8, 16):
            stream.write(col_fmt % buf[blk_idx * 16 + offset])

        stream.write(' ' * sep2_width)

        for offset in range(16):
            c = chr(buf[blk_idx * 16 + offset])
            stream.write('%c' % hexdump_escape(c))

        stream.write('\n')

    # Print the remaining bytes.
    if len(buf) % 16 > 0:
        stream.write(off_fmt % (len(buf) - (len(buf) % 16)))

        blk_off = len(buf) - len(buf) % 16

        for offset in range(min(len(buf) % 16, 8)):
            stream.write(col_fmt % buf[blk_off + offset])

        stream.write(' ' * sep1_width)

        for offset in range(8, len(buf) % 16):
            stream.write(col_fmt % buf[blk_off + offset])

        stream.write(' ' * ((16 - len(buf) % 16) * col_width))
        stream.write(' ' * sep2_width)

        for offset in range(len(buf) % 16):
            c = chr(buf[len(buf) - (len(buf) // 16) * 16 + offset])
            stream.write('%c' % hexdump_escape(c))

        stream.write('\n')
