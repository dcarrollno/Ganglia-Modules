#!/usr/bin/python

import os
import json
import time
import re
import urllib, urllib2
import socket
import copy

''' This module pulls Apache Traffic Server metrics
    via json and trends them in Ganglia.

    You must enable the stats modile in ATS.  We maintain a
    list of metrics that we calc deltas on between runs. I
    think this is cleaner than a series of conditionals.  We
    could set a positive slope on these but I don't like that
    as much as performing the deltas myself.

    Set your local IP for stats.  '''

__author__ = "Dave Carroll"


last_time = 0
cache = 5
json_data = {}
METRICS = {}
LAST_METRICS = {}
delta_list = [ 'proxy.process.http.cache_hit_fresh','proxy.process.http.cache_hit_mem_fresh',
               'proxy.process.http.cache_hit_revalidated', 'proxy.process.http.cache_hit_ims',
               'proxy.process.http.cache_hit_stale_served', 'proxy.process.http.cache_miss_cold',
	       'proxy.process.http.cache_miss_changed', 'proxy.process.http.cache_miss_client_no_cache',
               'proxy.process.http.cache_miss_client_not_cacheable ', 'proxy.process.http.cache_miss_ims',
               'proxy.process.cache.ram_cache.hits', 'proxy.process.cache.ram_cache.misses',
               'proxy.process.cache.gc_bytes_evacuated', 'proxy.process.cache.gc_frags_evacuated',
               'proxy.process.http.2xx_responses', 'proxy.process.http.3xx_responses',
               'proxy.process.http.4xx_responses',  'proxy.process.http.5xx_responses' ]

STATS_URL = 'http://10.132.227.145/_stats'


def get_json():
    global last_time,json_data,last_time,METRICS

    ''' Here we poll the json output and dict our metrics '''

    if (time.time() - last_time > cache):

        try:
            json_data.clear()
        except:
            print("Unable to clear json_data")

        # if we have a local file, use the following
        #json_data = json.loads(open('ats_stats.json').read())
        #for value in json_data['global']:
        #    METRICS[value]=json_data['global'][value]

        #return(json_data)

        try:
            aResp = urllib2.urlopen(STATS_URL);
            json_data = json.loads(aResp.read())
            for value in json_data['global']:
                METRICS[value]=json_data['global'][value]

        except:
            print("Unable to download json")

        return(METRICS)

    else:
        return


def get_stats(name):
    global json_data, LAST_METRICS

    METRICS = get_json()
    if LAST_METRICS:
        ''' check if cache primed '''
        next
    else:
        LAST_METRICS = copy.deepcopy(METRICS)
        last_time = time.time()

    name = re.sub('ats_','',name)
    for k,v in METRICS.items():
        if k == name:
  	    if name in delta_list:
                v = int(v)
                oldv = int(LAST_METRICS.get(k,0))
                d1 = int(v - oldv)
                #print("Delta is %s for metric %s" % (d1,name))
                return int(d1)
            else:
                return int(v)



def metric_init(params):
    global descriptors


    descriptors = [{'name': 'ats_proxy.process.http.cache_hit_fresh',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Hits',
        'slope': 'both',
        'format': '%u',
        'description': 'Number cache hits every 30 seconds that were served from local cache as fresh.',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_hit_mem_fresh',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Hits',
        'slope': 'both',
        'format': '%u',
        'description': 'Number of cache hits from memory every 30 seconds served from local cache in memory.',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_hit_revalidated',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Hits',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS Process httpd cache hit revalidated. This means we had a potentially stale representation of the object in our cache, but we revalidated it by calling the origin server and checking whether we need to pull a new item into cache or can revalidate and contiue using the existing item.',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_hit_ims',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Hits',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS cache hits ims',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_hit_stale_served',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Hits',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS number of stale cache hits served over 30 seconds',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_miss_cold',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Misses',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS cold cache misses that could not be served from local cache',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_miss_changed',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Misses',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS cache misses changed',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_miss_client_no_cache',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Miss',
        'slope': 'both',
        'format': '%u',
        'description': 'Cache misses by client sending a no-cache header.',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_miss_client_not_cacheable',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Miss',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS cache misses client not cacheable',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_miss_ims',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Miss',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS http cache miss ims',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.cache.ram_cache.hits',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Hits',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS cache hits from memory every 30 seconds. ',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.cache.ram_cache.misses',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Miss',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS cache misses from cache memory',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.cache.bytes_used',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Bytes',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS cache bytes used',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.cache.bytes_total',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Bytes',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS total cache bytes',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.cache.ram_cache.total_bytes',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Bytes',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS total bytes used for memory cache',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.cache.ram_cache.bytes_used',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Bytes',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS total bytes in use for memory cache',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.cache.gc_bytes_evacuated',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Bytes',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS Cache bytes purged or evacuated. Large numbers here may mean we need a larger cache size setting',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.cache.gc_frags_evacuated',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Bytes',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS cache purged or evacuated. Large numbers here may mean we need a larger cache size setting.',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.current_client_connections',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Client Conns',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS Current client HTTP Conns to our cache server. Watch this for overload',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.current_server_connections',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Server Conns',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS Current Server HTTP Conns. Watch this for overload',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.node.http.origin_server_current_connections_count',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Origin Conns',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS Current Origin Server HTTP Conns. These are connections back to our origin server asking for objects or revalidation etc.. Watch this for overload',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.2xx_responses',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': '2xx',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS current 2xx HTTP response codes over 30 seconds',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.3xx_responses',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': '3xx',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS current 3xx HTTP response codes over 30 seconds',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.4xx_responses',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': '4xx',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS current 4xx HTTP response codes over 30 seconds',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.5xx_responses',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': '5xx',
        'slope': 'both',
        'format': '%u',
        'description': 'ATS current 5xx HTTP response codes over 30 seconds',
        'groups': 'ATS',
        }]


    return descriptors

def metric_cleanup():
        '''Clean up the metric module.'''
        pass

if __name__ == '__main__':
    #metric_init({})
    params=0
    metric_init ({
    })
    while True:
        for d in descriptors:
            v = d['call_back'](d['name'])
            print 'value for %s is %s' % (d['name'],  v)
  	time.sleep(30)
