#!/usr/bin/python

''' This module allows us to trend stats from
    Redis using Ganglia.  We use the Redis cli
    to find interesting metrics.

    see: https://github.com/dcarrollno/Ganglia-Modules

    DC, 2/2015

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE. '''

__author__ = "Dave Carroll"


import os
import socket
import time
import re
import copy

curr_time=time.time()             # current time
last_time=0                       # last update
METRICS = {}
LAST_METRICS = {}
PARAMS={}

# Get the password
conf_file = '/etc/redis.conf'

with open(conf_file, 'r') as f:
  for line in f:
    if line.startswith('requirepass'):
      (label,pw) = line.split()
cmd1 = "auth "
cmd2 = "\n"
cmd = cmd1+pw+cmd2

def get_metrics():
    global METRICS,curr_time,last_time,cachetimer,host,port,cachetimer
    port = int(port)
    cachetimer = int(cachetimer)

    # Update from Redis. 
    if (time.time() - last_time > cachetimer):
      #print "Running Redis query"
      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.connect((host, port))
      s.send(cmd)
      sec = s.recv(4096)
      #print sec 		# This should return OK meaning socket conn and auth done
      s.send("INFO\n")
      info = s.recv(4096)
      #print info
      if "$" != info[0]:
        print "not equal"
        return 0
      len = int(info[1:info.find("\n")])
      if 4096 < len:
        info += s.recv(len - 4096)
      for line in info.splitlines()[1:]:
        #print line
        if "" == line:	# blank line, skip
          continue
        if line.startswith("#"):	# skips comments
          continue
        (n,v) = line.split(":")
        #print n,v
        METRICS[n]=v
      curr_time=time.time()
      last_time=time.time()
      s.close()
    return (METRICS,curr_time)

def get_stats(name):
    global d1, curr_metrics, LAST_METRICS, curr_time, last_time

    [curr_metrics,curr_time]=get_metrics()

    if LAST_METRICS:
      '''Check the cache and prime it if not ready '''
      #print "Cache not empty nor expired - using cached items"
      next
    else:
      #print ("Cache empty or expired - running query, filling cache")
      LAST_METRICS=copy.deepcopy(curr_metrics)	# cache
      last_time=time.time()	# set the cache timer

    name = re.sub('^redis_', '', name)
    #print(name)	# debug

    for k,v in curr_metrics.items():
      ''' Show all metrics '''
      #print("The key is %s and value is %s" % (k,v))	# debug

      if k == name:
        try:
          v = int(v)
        except:
          #print("ValueError: When converting value to int but we'll try float for %s %s" % (k,v))
          if (k == 'used_cpu_sys') or (k == 'used_cpu_user') or (k == 'mem_fragmentation_ratio'):
            v = float(v)
            #print v
            return float(v)

        #print "In get_stats we find %s and %s" % (k,v)

        if (k == 'expired_keys'):
          d1 = int(v - int(LAST_METRICS.get(k,0)))

        # this block below gets deltas
        if (k == 'used_cpu_sys') or (k == 'used_cpu_user'):
          #for a,b in LAST_METRICS.items():
            #if (a == 'used_cpu_sys') or (a == 'used_cpu_user'):
              #print "Last Metric: %s %s" % (a,b)

          #print "New metric: %s,%s" % (k,v)
          d1 = float(v - float(LAST_METRICS.get(k,0)))
          #print "Delta is: %f" % d1
          return float(d1)
        else:
          return int(v)	# return non deltas

def metric_init(params):
    global descriptors,host,port,cachetimer,conf_file

    host = params.get('host')
    port = params.get('port')
    cachetimer = params.get('cachetimer')
    conf_file = params.get('conf_file')

    descriptors = [{'name': 'redis_connected_clients',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'clients connected',
        'slope': 'both',
        'format': '%u',
        'description': 'Number of connected clients excluding slaves.',
        'groups': 'Redis',
        },
        {'name': 'redis_connected_slaves',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'slaves connected',
        'slope': 'both',
        'format': '%u',
        'description': 'Number of slaves connected',
        'groups': 'Redis',
        },
        {'name': 'redis_blocked_clients',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'blocked clients',
        'slope': 'both',
        'format': '%u',
        'description': 'Number of clients pending on a blocking call',
        'groups': 'Redis',
        },
        {'name': 'redis_used_memory',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Bytes',
        'slope': 'both',
        'format': '%u',
        'description': 'The total number of bytes allocated by Redis using its allocator',
        'groups': 'Redis',
        },
        {'name': 'redis_expired_keys',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Expired Keys',
        'slope': 'positive',
        'format': '%u',
        'description': 'Expired keys over past 30 seconds',
        'groups': 'Redis',
        },
        {'name': 'redis_evicted_keys',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Evicted Keys',
        'slope': 'positive',
        'format': '%u',
        'description': 'Evicted keys over past 30 seconds due to maxmemory limit setting',
        'groups': 'Redis',
        },
        {'name': 'redis_rdb_changes_since_last_save',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Changes',
        'slope': 'both',
        'format': '%u',
        'description': 'Number of changes since the last dump',
        'groups': 'Redis',
        },
        {'name': 'redis_used_memory_rss',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Used Memory RSS',
        'slope': 'both',
        'format': '%u',
        'description': 'Used Memory RSS. If used_memory_peak and used_memory_rss are roughly equal and both significantly higher than used_memory, this indicates that external fragmentation is occurring',
        'groups': 'Redis',
        },
        {'name': 'redis_used_memory_peak',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Used Memory Peak',
        'slope': 'both',
        'format': '%u',
        'description': 'Historically largest amount of mem used by Redis.  If used_memory_peak and used_memory_rss are roughly equal and both significantly higher than used_memory, this indicates that external fragmentation is occurring',
        'groups': 'Redis',
        },
        {'name': 'redis_instantaneous_ops_per_sec',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Ops/Sec',
        'slope': 'both',
        'format': '%u',
        'description': 'Instantaneous Operations Per Sec',
        'groups': 'Redis',
        },
        {'name': 'redis_total_net_input_bytes',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Input Bytes',
        'slope': 'positive',
        'format': '%u',
        'description': 'Network Input Bytes by Redis over past 30 seconds',
        'groups': 'Redis',
        },
        {'name': 'redis_total_net_output_bytes',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Output Bytes',
        'slope': 'positive',
        'format': '%u',
        'description': 'Network Output in Bytes by Redis over past 30 seconds',
        'groups': 'Redis',
        },
        {'name': 'redis_keyspace_hits',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Keyspace Hits',
        'slope': 'positive',
        'format': '%u',
        'description': 'Keyspace Hits over past 30 seconds',
        'groups': 'Redis',
        },
        {'name': 'redis_keyspace_misses',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Keyspace Misses',
        'slope': 'positive',
        'format': '%u',
        'description': 'Keyspace Misses over past 30 seconds',
        'groups': 'Redis',
        },
        {'name': 'redis_repl_backlog_size',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Bytes',
        'slope': 'positive',
        'format': '%u',
        'description': 'Replication Backlog Size in Bytes',
        'groups': 'Redis',
        },
        {'name': 'redis_mem_fragmentation_ratio',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'float',
        'units': 'Bytes',
        'slope': 'both',
        'format': '%.4f',
        'description': 'If the fragmentation ratio is outside the range of 1 to 1.5, it is likely a sign of poor memory management by either the operating system or by your Redis instance.',
        'groups': 'Redis',
        },

        {'name': 'redis_master_last_io_seconds_ago',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Bytes',
        'slope': 'both',
        'format': '%u',
        'description': 'Number of seconds ago since last interaction with master',
        'groups': 'Redis',
        },
        {'name': 'redis_total_commands_processed',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Bytes',
        'slope': 'positive',
        'format': '%u',
        'description': 'Commands processed over 30 seconds. Watch for spikes here indicating command queue backup.',
        'groups': 'Redis',
        }]

    return(descriptors)

def metric_cleanup():
    '''Clean up the metric module.'''
    pass

#This code is for debugging and unit testing
if __name__ == '__main__':

    descriptors = metric_init ({
      'host':'127.0.0.1',
      'port':'6379',
      'cachetimer':'5',
      'conf_file':'/etc/redis.conf'
      })
    while True:
        for d in descriptors:
            v = d['call_back'](d['name'])
            print 'value for %s is %s' % (d['name'],  v)
        print 'Sleeping 30 seconds'
        ''' Add to cache '''
        LAST_METRICS=copy.deepcopy(METRICS)
        last_time=time.time()
        time.sleep(30)
