#!/usr/bin/env python

""" This module allows us to trend stats from
    Aerospike using Ganglia.  The Aerospike dashboard
    is nice but we do like to trend over time in Ganglia.

    DC, 8/2014 """

import os
import time
import re
import copy
import socket

PARAMS={}
METRICS={}
LAST_METRICS={}
METRICS_CACHE_MAX=5
thishost=socket.gethostname()

cmd1="/usr/bin/asinfo -h "
cmd2=" -v statistics"
cmd = cmd1+thishost+cmd2

def get_metrics():
    """Aerospike Metrics"""
    global METRICS
    p=os.popen(cmd, "r")
    while 1:
      line=p.readline()
      if not line: break
      list=line.split(';')
      for item in list:
        m=re.match("(\S+)=(\d+)",item)
        if m:
          parts=re.match('(\S+)=(\d+)',item).groups()
          k,v=parts[0], int(parts[1])
          METRICS[k]= v
    return (METRICS)

def get_delta(name):
    """ Perform logic on metrics as needed"""
    global d1, curr_metrics

    curr_metrics=get_metrics()
    for k,v in curr_metrics.items():
      if k == name:
        # Uncomment lines below for debugging
        #print k
        #print "Current Metrics value is %d" % v
        #for a,b in LAST_METRICS.items():
          #if a == name:
            #print a
            #print "Last Metrics value is %d" % b
        if (k == 'client_connections') or (k == 'objects'):
          return(v)
        elif (k == 'used-bytes-memory') or (k == 'used-bytes-disk'):
          d1 = 1024 * v
        else:
          d1 = v - LAST_METRICS.get(k,0)
    return(d1)

def metric_init(params):
    """Required by Ganglia"""
    global descriptors, LAST_METRICS

    descriptors = [{'name': 'client_connections',
        'call_back': get_delta,
        'time_max': 20,
        'value_type': 'uint',
        'units': 'clients',
        'slope': 'both',
        'format': '%u',
        'description': 'Client Connections',
        'groups': 'Aerospike',
        },

     {'name': 'stat_read_reqs',
        'call_back': get_delta,
        'time_max': 20,
        'value_type': 'uint',
        'units': 'read_reqs',
        'slope': 'both',
        'format': '%u',
        'description': 'Read Requests',
        'groups': 'Aerospike',
        },

     {'name': 'stat_read_success',
        'call_back': get_delta,
        'time_max': 20,
        'value_type': 'uint',
        'units': 'read_success',
        'slope': 'both',
        'format': '%u',
        'description': 'Read Success',
        'groups': 'Aerospike',
        },

     {'name': 'stat_write_reqs',
        'call_back': get_delta,
        'time_max': 20,
        'value_type': 'uint',
        'units': 'write_reqs',
        'slope': 'both',
        'format': '%u',
        'description': 'Write Requests',
        'groups': 'Aerospike',
        },

     {'name': 'stat_write_success',
        'call_back': get_delta,
        'time_max': 20,
        'value_type': 'uint',
        'units': 'write_success',
        'slope': 'both',
        'format': '%u',
        'description': 'Write Success',
        'groups': 'Aerospike',
        },

     {'name': 'transactions',
        'call_back': get_delta,
        'time_max': 20,
        'value_type': 'uint',
        'units': 'transactions',
        'slope': 'both',
        'format': '%u',
        'description': 'Transactions',
        'groups': 'Aerospike',
        },

     {'name': 'used-bytes-memory',
        'call_back': get_delta,
        'time_max': 20,
        'value_type': 'uint',
        'units': 'used-bytes-memory',
        'slope': 'both',
        'format': '%u',
        'description': 'Used Bytes Memory',
        'groups': 'Aerospike',
        },

     {'name': 'used-bytes-disk',
        'call_back': get_delta,
        'time_max': 20,
        'value_type': 'uint',
        'units': 'used-bytes-disk',
        'slope': 'both',
        'format': '%u',
        'description': 'Used Bytes Disk',
        'groups': 'Aerospike',
        },

     {'name': 'stat_evicted_objects',
        'call_back': get_delta,
        'time_max': 20,
        'value_type': 'uint',
        'units': 'evictions',
        'slope': 'both',
        'format': '%u',
        'description': 'Evicted Objects',
        'groups': 'Aerospike',
        },

     {'name': 'objects',
        'call_back': get_delta,
        'time_max': 20,
        'value_type': 'uint',
        'units':'objects',
        'slope': 'both',
        'format': '%u',
        'description': 'Objects',
        'groups': 'Aerospike',
        },

     {'name': 'stat_rw_timeout',
        'call_back': get_delta,
        'time_max': 20,
        'value_type': 'uint',
        'units': 'ReadWrite TimeOut',
        'slope': 'both',
        'format': '%u',
        'description': 'ReadWrite TimeOut',
        'groups': 'Aerospike',
        }]

    return(descriptors)

def metric_cleanup():
    '''Clean up the metric module.'''
    pass

#This code is for debugging and unit testing
if __name__ == '__main__':
    descriptors = metric_init(PARAMS)
    while True:
        for d in descriptors:
            v = d['call_back'](d['name'])
	    print 'value for %s is %u' % (d['name'],  v)
        print 'Sleeping 15 seconds'
        """ Add to cache """
        LAST_METRICS=copy.deepcopy(METRICS)
        time.sleep(15)
