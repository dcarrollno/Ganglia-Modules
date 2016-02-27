#!/usr/bin/python

import os
import json
import time
import re
import urllib, urllib2
import socket

''' This module pulls Apache Traffic Server metrics
    via json and trends them in Ganglia. 

see: https://github.com/dcarrollno/Ganglia-Modules

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE. 


NOTE: Change the URL under get_json function to your server IP or name '''

__author__ = "Dave Carroll"


last_time = 0
cache = 5
json_data = {}

def get_json():
    global last_time,json_data

    try:
        json_data.clear()
    except:
        print("Unable to clear json_data")

    # if we have a local file, use the following
    #json_data = json.loads(open('ats_stats.json').read())
    #return(json_data)

    try:
        aResp = urllib2.urlopen("http://<YOUR_IP_HERE>/_stats");
        json_data = json.loads(aResp.read())
        last_time = time.time()
    except:
        print("Unable to download json")

    return(json_data)

def get_stats(name):
    global json_data,last_time

    if (time.time() - last_time > cache):
        try:
            json_data.clear()
            json_data = get_json()
        except:
            print("unable to call get_json")

    name = re.sub('ats_','',name)
    metric = json_data['global'][name]
    return int(metric)


def metric_init(params):
    global descriptors


    descriptors = [{'name': 'ats_proxy.process.http.cache_hit_fresh',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Hits',
        'slope': 'positive',
        'format': '%u',
        'description': 'Number cache hits every 60 seconds',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_hit_mem_fresh',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Hits',
        'slope': 'positive',
        'format': '%u',
        'description': 'Number of cache hits from memory every 60 seconds',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_hit_revalidated',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Hits',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS Process httpd cache hit revalidated. This means we had a stale representation of the object in our cache, but we revalidated it by checking using an If-Modified-Since header.',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_hit_ims',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Hits',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS cache hits ims',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_hit_stale_served',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Hits',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS number of stale cache hits served over 60 seconds',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_miss_cold',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Misses',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS cold cache misses',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_miss_changed',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Misses',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS cache misses changed',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_miss_client_no_cache',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Miss',
        'slope': 'positive',
        'format': '%u',
        'description': 'Cache misses by client no cache',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_miss_client_not_cacheable',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Miss',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS cache misses client not cacheable',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.cache_miss_ims',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Miss',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS http cache miss ims',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.cache.ram_cache.hits',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Hits',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS cache hits from memory every 60 seconds. ',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.cache.ram_cache.misses',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Cache Miss',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS cache misses from cache memory',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.cache.bytes_used',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Bytes',
        'slope': 'positive',
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
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS total bytes in use for memory cache',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.cache.gc_bytes_evacuated',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Bytes',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS Cache bytes purged or evacuated. Large numbers here may mean we need a larger cache size setting',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.cache.gc_frags_evacuated',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Bytes',
        'slope': 'positive',
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
        'description': 'ATS Current Server HTTP Conns. Watch this for overload',
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
        {'name': 'ats_proxy.process.http.2xx_responses',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': '2xx',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS current 2xx HTTP response codes over 60 seconds',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.3xx_responses',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': '3xx',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS current 3xx HTTP response codes over 60 seconds',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.4xx_responses',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': '4xx',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS current 4xx HTTP response codes over 60 seconds',
        'groups': 'ATS',
        },
        {'name': 'ats_proxy.process.http.5xx_responses',
        'call_back': get_stats,
        'time_max': 60,
        'value_type': 'uint',
        'units': '5xx',
        'slope': 'positive',
        'format': '%u',
        'description': 'ATS current 5xx HTTP response codes over 60 seconds',
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
