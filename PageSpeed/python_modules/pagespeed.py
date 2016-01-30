#!/usr/bin/env python

''' This module allows us to trend stats from
    PageSpeed using Ganglia. It is great to trend
    performance over time. 

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

import urllib
import urllib2
import socket
import re
import time
import copy

web_pg = []
METRICS = {}
curr_metrics = {}
LAST_METRICS = {}
curr_time = 0
last_time = 0
cache = 5

def get_metrics():
    global web_pg, METRICS, STATSURL
    aResp = urllib2.urlopen(STATSURL);
    web_pg = aResp.readlines();
    for line in web_pg:
        line = line.rstrip("\n\r")
        match = re.search(r'\S+:\s+\d+',line)
        if match:
            #print line
            (metric,value) = line.split(':')
            METRICS[metric]=int(value)
            curr_time = time.time()
    return(METRICS,curr_time)

def get_stats(name):
    ''' Perform logic on metrics as needed '''
    global d1, curr_metrics, LAST_METRICS, curr_time, last_time
    name = re.sub('pagespeed_','',name)	# convert metric name to match Google

    if (time.time() - last_time > cache):	# Is cache expired?
        LAST_METRICS=copy.deepcopy(curr_metrics)
        last_time = time.time()
        [curr_metrics,curr_time]=get_metrics()
    else:
        print("Cache not expired..")		# do not refill cache

    if not LAST_METRICS:			# cache empty - only on first run of program
        #print("Cache Miss: filling now...")	# yep, cache miss occurred
        LAST_METRICS=copy.deepcopy(curr_metrics)	# prime cache
        last_time = time.time()			# set current timer
    else:					# if cache exists, check age of cache
        print("Cache hit")			# otherwise we have cache hit inside timer

    for k,v in curr_metrics.items():
        if k == name:
            print "Name is: %s and value is %s" % (k,v)
            d1 = int(v - LAST_METRICS.get(k,0))
            if d1 < 0:
                d1 = 0
                print "Delta for %s is: %d" % (k,d1)
            return int(d1)

def metric_init(params):
    global descriptors, STATSURL

    STATSURL = params.get('stats_url')

    descriptors = [{'name': 'pagespeed_cache_hits',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'Hits',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed memory cache hits - we are not using this at Nanigans',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_cache_misses',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'Cache Misses',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed memory cache misses over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_cache_backend_hits',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'Cache Backend Hits',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed memory cache backend hits over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_cache_expirations',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'Cache Expires',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed memory cache expires over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_cache_inserts',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'Cache Inserts',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed memory cache inserts over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_css_combine_opportunities',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'CSS Combines',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed: comining multiple css into one file to make it cacheable and minify over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_css_filter_uses',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'CSS Filter',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed CSS Filter Uses over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_javascript_blocks_minified',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'JS Blocks Minified',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed Javascript blocks minified over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_javascript_total_bytes_saved',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'JS Bytes Saved',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed JavaScript total bytes saved over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_javascript_total_original_bytes',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'JS Total Bytes',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed Javascript total original bytes over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_resource_url_domain_acceptances',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'URL Accepts',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed resource URL domain acceptances over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_resource_url_domain_rejections',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'URL Rejects',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed: server will not rewrite a resource for because foreign domain not authorized over 30 seconds ',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_rewrite_cached_output_hits',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'Rewrite Cache Output',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed: Number of times we served an optimized resource from cache over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_rewrite_cached_output_misses',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'Rewrite Cache misses',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed: Number of times we missed serving an optimized resource from cache and had to optimize it over 30 seconds.',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_file_cache_inserts',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'File Cache Inserts',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed file cache inserts over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_file_cache_hits',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'File Cache Hits',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed file cache hits over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_file_cache_misses',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'File cache Misses',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed file cache misses over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_critical_images_valid_count',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'Images Valid',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed critical images valid count over 30 seconds',
        'groups': 'PageSpeed',
        },
        {'name': 'pagespeed_critical_images_not_found_count',
        'call_back': get_stats,
        'time_max': 30,
        'value_type': 'uint',
        'units': 'Images Not Found',
        'slope': 'both',
        'format': '%u',
        'description': 'PageSpeed critical images not found count over 30 seconds',
        'groups': 'PageSpeed',
        }]

    return descriptors

def metric_cleanup():
    '''Clean up the metric module.'''
    pass

if __name__ == '__main__':
    params=0
    metric_init ({
      'stats_url':'http://localhost/pagespeed_admin'
    })
    while True:
      for d in descriptors:
        v = d['call_back'](d['name'])
        print 'value for %s is %u' % (d['name'],  v)
      time.sleep(30)
