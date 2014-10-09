#!/usr/bin/env python

''' This module allows us to trend stats from
    Aerospike using Ganglia.  The Aerospike dashboard
    is nice but we do like to trend over time in Ganglia.

    see: https://github.com/dcarrollno/Ganglia-Modules 

    DC, 8/2014 

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE. '''

import os
import time
import re
import copy
import socket

PARAMS={}
METRICS={}			  # metrics
LAST_METRICS={}			  # last metrics
thishost=socket.gethostname()	  # hostname
curr_time=time.time()	          # current time
last_time=0		          # last update
ascache=5			  # metric cache time


cmd1="/usr/bin/asinfo -h "
cmd2=" -v statistics"
cmd = cmd1+thishost+cmd2

def get_metrics():
    ''' Aerospike Metrics '''
    global METRICS, curr_time, last_time

    if (time.time() - last_time > ascache):
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
            curr_time=time.time()
            last_time=time.time()
      stat=p.close()
    return (METRICS,curr_time)

def get_delta(name):
    ''' Perform logic on metrics as needed '''
    global d1, curr_metrics, LAST_METRICS, curr_time, last_time

    [curr_metrics,curr_time]=get_metrics()
    if LAST_METRICS:
      '''Check the cache and prime it if not ready '''
      next
    else:
      #print ("Empty - adding to cache")
      LAST_METRICS=copy.deepcopy(METRICS)
      last_time=time.time()
    for k,v in curr_metrics.items():
      if k == name:
        # Uncomment lines below for debugging
        #print k
        #print "Current Metrics value is %d" % v
	    #print curr_time
        #for a,b in LAST_METRICS.items():
          #if a == name:
            #print a
            #print "Last Metrics value is %d" % b
        if (k == 'client_connections') or (k == 'objects'):
          return int(v)
        elif (k == 'used-bytes-memory') or (k == 'used-bytes-disk'):
          d1 = int(1024 * v)
	  return(d1)
        else:
          #if v < LAST_METRICS.get(k,0):
           # v += 4294967296
          #d1 = int(v - LAST_METRICS.get(k,0)/curr_time - last_time)
	  d1 = int(v - LAST_METRICS.get(k,0))
	  #print "Delta is: %d" % d1
          return int(v)

def metric_init(params):
    """Required by Ganglia"""
    global descriptors, LAST_METRICS

    descriptors = [{'name': 'client_connections',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'clients',
        'slope': 'both',
        'format': '%u',
        'description': 'If client_connections are at or near proto_fd_max configuration value then Aerospike may soon or currently is unable to accept new connections. We set proto_fd_max to 15000 at Nanigans.',
        'groups': 'Aerospike',
        },

        {'name': 'stat_read_reqs',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'read_reqs',
        'slope': 'positive', 
        'format': '%u',
        'description': 'The number of read requests over a 30 second time period',
        'groups': 'Aerospike',
        },

        {'name': 'stat_read_success',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'read_success',
        'slope': 'positive',
        'format': '%u',
        'description': 'The number of read successes over a 30 second time period.',
        'groups': 'Aerospike',
        },

        {'name': 'waiting_transactions',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'waiting tx',
        'slope': 'positive',
        'format': '%u',
        'description': 'The number of waiting transactions over a 30 second period',
        'groups': 'Aerospike',
        },

        {'name': 'stat_read_errs_notfound',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'read_notfound',
        'slope': 'positive',
        'format': '%u',
        'description': 'The number of times a read request resulted in a not found response',
        'groups': 'Aerospike',
        },

        {'name': 'stat_write_reqs',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'write_reqs',
        'slope': 'positive',
        'format': '%u',
        'description': 'The number of client write requests over a 30 second period',
        'groups': 'Aerospike',
        },

        {'name': 'stat_write_success',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'write_success',
        'slope': 'positive',
        'format': '%u',
        'description': 'The nummber of write successes over a 30 second period.',
        'groups': 'Aerospike',
        },

        {'name': 'stat_write_errs_other',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'write_errs_other',
        'slope': 'positive',
        'format': '%u',
        'description': 'The number of write errors. This should be close to zero.',
        'groups': 'Aerospike',
        },

        {'name': 'stat_delete_success',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'delete_success',
        'slope': 'positive',
        'format': '%u',
        'description': 'The number of successful delete requests',
        'groups': 'Aerospike',
        },

        {'name': 'transactions',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'transactions',
        'slope': 'positive',
        'format': '%u',
        'description': 'The total number of transactions over a 30 second period. Includes all reads, writes and info requests',
        'groups': 'Aerospike',
        },

        {'name': 'used-bytes-memory',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'used-bytes-memory',
        'slope': 'both',
        'format': '%u',
        'description': 'Trending used-bytes-memory provides operations insight into how memory usage changes over time for this namespace.',
        'groups': 'Aerospike',
        },

        {'name': 'data-used-bytes-memory',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'data-used-bytes-memory',
        'slope': 'both',
        'format': '%u',
        'description': 'The amount of memory used for data, only if we are serving out of memory vs disk. For RTB we are using on-disk.',
        'groups': 'Aerospike',
        },

        {'name': 'index-used-bytes-memory',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'index-used-bytes-memory',
        'slope': 'both',
        'format': '%u',
        'description': 'The amount of memory the index is using',
        'groups': 'Aerospike',
        },

        {'name': 'used-bytes-disk',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'used-bytes-disk',
        'slope': 'both',
        'format': '%u',
        'description': 'Trending used-bytes-disk provides operations insight into how disk usage changes over time for this namespace.',
        'groups': 'Aerospike',
        },

        {'name': 'stat_evicted_objects',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'evictions',
        'slope': 'positive',
        'format': '%u',
        'description': 'We evict non-zero TTL data if we reach 50% of available storage or 60% of 60GB memory. Note this 60GB is our current company hardware standard for Aerospike nodes so adjust this accordingly if yours differs.',
        'groups': 'Aerospike',
        },

        {'name': 'stat_expired_objects',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'expired',
        'slope': 'positive',
        'format': '%u',
        'description': 'Trending stat_expired_objects provides operations insight into system expiration behavior over time.',
        'groups': 'Aerospike',
        },

        {'name': 'objects',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units':'objects',
        'slope': 'both',
        'format': '%u',
        'description': 'Trending objects provides operations insight into object fluctuations over time',
        'groups': 'Aerospike',
        },
  
        {'name': 'free-pct-disk',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units':'%',
        'slope': 'both',
        'format': '%u',
        'description': 'Percentage of raw device free',
        'groups': 'Aerospike',
        },
  
        {'name': 'free-pct-memory',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units':'%',
        'slope': 'both',
        'format': '%u',
        'description': 'Percentage memory free',
        'groups': 'Aerospike',
        },

        {'name': 'stat_rw_timeout',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'ReadWrite TimeOut',
        'slope': 'positive',
        'format': '%u',
        'description': 'The number of read/write timeouts server side over a 30 second period. This should be close to zero at all times.',
        'groups': 'Aerospike',
        },

        {'name': 'stat_read_reqs_xdr',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'XDR Read Reqs',
        'slope': 'positive',
        'format': '%u',
        'description': 'The number of cross-data-center read requests handled by this node.',
        'groups': 'Aerospike',
        },

        {'name': 'stat_write_reqs_xdr',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'XDR Write Reqs',
        'slope': 'positive',
        'format': '%u',
        'description': 'The number of cross-data-center write requests handled by this node',
        'groups': 'Aerospike',
        },

        {'name': 'migrate_msgs_recv',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Migrate msgs recvd',
        'slope': 'positive',
        'format': '%u',
        'description': 'The number of migrate messages received by this node over 30 seconds',
        'groups': 'Aerospike',
        },

        {'name': 'migrate_msgs_sent',
        'call_back': get_delta,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Migrate msgs sent',
        'slope': 'positive',
        'format': '%u',
        'description': 'The number of migrate messages sent by this node over 30 seconds',
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
        print 'Sleeping 30 seconds'
        """ Add to cache """
        LAST_METRICS=copy.deepcopy(METRICS)
	last_time=time.time()
        time.sleep(30)
