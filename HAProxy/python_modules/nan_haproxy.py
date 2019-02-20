#!/usr/bin/env python
# -*- coding: utf-8 -*-


""" Ganglia module for trending HAProxy metrics on load balancers.
    Requires yum install socat on this node """

__author__ = "Dave Carroll"


import os
import sys
import re
import threading
import time


descriptors = list()
Desc_Skel = {}
_Lock = threading.Lock()
_Worker_Thread = None
configDict = {}



""" Trending HAProxy is difficult due to the very nature of load-balancing which is a rapid action. But, we
    can poll and trend to get an idea of sessions, bytes and errors to help us understand volume and when
    things are not going well. We run HaProxy over small scale systems with 8 cores, 7 used for actual HAP
    operations. I hate flipping between HaProxy stats pages so this module sums them all under one set of metrics and if you need 
    to see per-proc metrics, pull those up in each proc stats page within HAProxy. 

    It is also tough to ask gmond to collect extensive metric stats across multiple procs in the timeframe gmond has to work with. 
    So, we background thread our collections to keep our module moving right along and not impact other modules running here.
"""


# // Below are the def mappings for HAP metrics. This could be used to provide metric descriptions below or left here as a 
#    simple quick reference. 
index = {'pxname':'proxy name', 'svname':'service name', 'qcur':'queued requests', 'qmax':'max val of qcur', 'scur':'current sessions',
         'smax':'max sessions', 'slim':'session limit', 'stot':'cumm num connections', 'bin':'bytes in', 'bout':'bytes out',
         'dreq': 'reqs denied for security', 'ereq':'request errors', 'econ':'backend conn errors', 'eresp':'response errors',
         'wretr':'num times req was retried', 'wredis':'Num reqs sent to different server', 'status':'up|down', 'weight':'weight',
         'act':'num active servers', 'bck':'backup servers','chkfail':'num failed checks', 'chkdown':'num up and down transitions',
         'lastchg':'num secs since last down', 'downtime':'total downtime in secs', 'qlimit':'maxqueue for server',
         'pid':'process id', 'sid':'server id', 'throttle':'cur throttle %', 'lbtot':'num times server selected', 'tracked':'if tracking enabled',
         'type':'0=frontend, 1=backend, 2=server, 3=socket/listener', 'rate':'number of sessions per second over last elapsed second',
         'rate_lim':'limit of new sessions per sec', 'rate_max':'max num sessions', 'check_status':'status of healthcheck',
         'hsrp_1xx':'num of hsrp 1xxx responses', 'req_rate':'http reqs per sec', 'req_tot':'total http reqs', 'cli_abrt':'num data xfer aborts',
         'srv_abrt':'num data xfers aborted by server'  }



class HaproxyMetrics(threading.Thread):
    """ Class to handle HaProxy Metrics """


    def __init__(self, params):
        # Constructor


        threading.Thread.__init__(self)
        self.running          =    False
        self.shuttingdown     =    False
        self.params           =    params
        self.refresh_rate     =    int(self.params['cache'])
        self.socketDir        =    self.params['socketDir']
        self.clusters         =    self.params['clusters']
        self.interestingItems =    self.params['interestingItems']
        self.socketCmd        =    'echo "show stat" | socat stdio '+self.socketDir
        self.sortedMetrics    =    {}
        self.metricVals       =    {}
        self.compiledMetrics  =    {}
        self.finalMetrics     =    {}


    def shutdown(self):
        """ method to shutdown threads """

        self.shuttingdown = True

        if not self.running:
            return
        self.join()


    def run(self):
        """ method to run metrics """

        self.running = True

        while not self.shuttingdown:
            _Lock.acquire()
            self.update_metrics()
            _Lock.release()
            time.sleep(self.refresh_rate)

        self.running = False


    def update_metrics(self):
        """ method to update metrics from HAP """

        # // here we poll the sockets, collect metrics, clean, sort, filter

        try:
            self.sockets = [f for f in os.listdir(self.socketDir) if f.startswith('stats')]
        except:
            print("ERROR: Unable to read HaProxy Metric stats")
            sys.exit(1)

        for n in self.sockets:
            self.poll_haproxy(n)

        self.parse_data()
        self.combine_metrics()
        return()



    def poll_haproxy(self,proc):
        """ Poll HAP for metrics """

        self.proc = proc

        try:
            p1 = os.popen(self.socketCmd+self.proc,'r')
        except Exception, e:
            print("HAPROXY Unable to poll socket %s" % e)

        while True:
            line = p1.readline().strip()
            if not line: break

            if line.startswith('#'):
                line = line.replace('# ','')
                metric_defs = line.split(',')
                continue

            self.metricvals = line.split(',')

            # // We use an abnormal number of exception checking to
            #    help debug our data asset - this can probably be
            #    reverted later.

            try:
                cluster = self.metricvals[0]
                node = self.metricvals[1]
            except:
                print("HAPROXY Error in poll_haproxy")
                pass

            try:
                self.metricVals.setdefault(self.proc+'_'+cluster, {})[node]=self.metricvals[2:]
                self.metric_defs = metric_defs[2:]
            except Exception, f:
               print("HAPROXY error in poll_haproxy was %s" % f)



    def parse_data(self):
        ''' process stats '''

        for x,y in self.metricVals.items():
            for a,b in y.items():
                g = x+'_'+a
                self.compiledMetrics[g]=b

        for n,m in self.compiledMetrics.items():
            self.myMetrics = dict(zip(self.metric_defs,m))
            self.compiledMetrics[n]=self.myMetrics

        for h,i in self.compiledMetrics.items():
            farm  = h.split('_',2)[1]
            if farm in self.clusters:
                if not 'BACKEND' in h:
                    for c,v in i.items():
                        if c in self.interestingItems:
                            d = h+'_'+c
                            self.finalMetrics[d]=v
            else:
                continue



    def combine_metrics(self):
        """ Combine each HAP process by host into a grouped sum """


        self.sortedMetrics = {}

        for k,v in sorted(self.finalMetrics.items()):
            (proc,cluster,host,metric) = k.split('_')


            if cluster not in self.sortedMetrics:
                self.sortedMetrics[cluster]={}
            if host not in self.sortedMetrics[cluster]:
                self.sortedMetrics[cluster][host]={}
            if metric not in self.sortedMetrics[cluster][host]:
                self.sortedMetrics[cluster][host][metric]=v
            else:
                r = self.sortedMetrics[cluster][host][metric]
                try:
                    s = int(r) + int(v)
                except ValueError, a:
                    if not r:
                        r = int(0)
                    if not v:
                        v = int(0)
                    s = int(r) + int(v)
                self.sortedMetrics[cluster][host][metric]=s



    def get_stats(self,name):
        """ Method to manage stats gathering for Ganglia. On our first
            run we won't have stats but need to set up our metrics so
            we prepopulate with zero values to pass. """

        (cluster,hname,metric) = name.split('_')

        try:
            if hname in self.sortedMetrics[cluster]:
                if metric in self.sortedMetrics[cluster][hname]:
                    _Lock.acquire()
                    val = self.sortedMetrics[cluster][hname][metric]
                    _Lock.release()
                    return(int(val))

        except Exception as g:
            #print("HAPROXY Error in get_stats: Error thrown was %s" % g)
            return(int(0))



def build_descriptor(cluster,node,metric):
    """ Since we are dynamically building our descriptors
        we need to do some up front definitions on first run. """

    global descriptors

    # name should be like stats.1_webserver-nodes_web1_bout
    #(sname,cname,hname,metric) = name.split('_')

    name = cluster+'_'+node+'_'+metric

    if metric.endswith('bin') or metric.endswith('bout'):
      units = 'Bytes'
      slope = 'positive'
      description = 'Bytes In/Out'
    elif metric.endswith('rate') or metric.endswith('scur'):
      units = 'Requests'
      slope = 'both'
      description = 'Request Rate - requests per second'
    elif metric.endswith('rate_max'):
      units = 'Rate Max'
      slope = 'both'
      description = 'Max No. Requests'
    elif metric.endswith('dreq'):
      units = 'Deny Errors'
      slope = 'positive'
      description = 'Denied Errors'
    elif metric.endswith('chkfail'):
      units = 'Check Fails'
      slope = 'positive'
      description = 'Number of failed checks against servers'
    elif metric.endswith('eresp') or metric.endswith('econ') or metric.endswith('ereq'):
      units = 'Errors'
      slope = 'positive'
      description = 'Request Connection or Response Errors'
    else:
      units = 'Number'
      slope = 'both'
      description = 'HAProxy Metric'


    d = {     'name'        : name,
              'call_back'   : get_stats,
              'time_max'    : 30,
              'value_type'  : 'uint',
              'units'       : units,
              'slope'       : slope,
              'format'      : '%u',
              'description' : description,
              'groups'      : 'haproxy_'+cluster,
              }

    try:
        #print d   # // debug
        descriptors.append(d)

    except Exception as e:
        #print('Build descriptor failed for %s with %s' % (name,e))
        pass



def metric_init(params):
    """ Required load-time function for Ganglia """

    global _Worker_Thread, descriptors

    # // Parameters

    """ We can work with lists from our pyconf to define
        and build our data assets """

    try:
        METRIC_GROUP = params.get('metric_group')
        cache = params.get('cache')
        socketDir = params.get('socketDir')

        clusters = params.get('clusters')
        if type(clusters) is str:
            clusters = clusters.split(',')

        interestingItems = params.get('interestingItems')
        if type(interestingItems) is str:
            interestingItems = interestingItems.split(',')

        for cluster in clusters:
            if cluster in params:
                nodes = params.get(cluster)
                nodelist = nodes.split(',')
                configDict[cluster]=nodelist


    except Exception, e:
        print("WARN: Incorrect parameters in nan_haproxy2. Error thrown was %s" % e)


    # //  Thread out

    _Worker_Thread = HaproxyMetrics(params)
    _Worker_Thread.start()


    # Build descriptors
    # The Key is webserver-nodes and the Val is {'web1': {'scur': 171}, 'web2': {'scur': 79}}  etc..

    for metric in interestingItems:
        for cluster,nodes in configDict.items():
            for node in nodes:
                build_descriptor(cluster,node,metric)


    return(descriptors)


def get_stats(name):
    """ This function runs outside of our class and is called by
        gmond to check the instance for the latest stats. """

    return _Worker_Thread.get_stats(name)


def metric_cleanup():
    _Worker_Thread.shutdown()


if __name__ == '__main__':
    """ Debug and test 
        Removed extensive Puppet erb entries below and replaced
        with examples 
    """

    try:
        params = {}
        params['metric_group']='haproxy'
        params['socketDir']='/var/lib/haproxy/'
        params['cache']=15
        params['clusters']= "webserver-nodes"
        params['webserver-nodes']="web1, web2, web3"
        params['interestingItems']="scur,bin,bout,dreq,ereq,econ,eresp,chkfail,rate"

        metric_init(params)
        while True:
            for d in descriptors:
                v = d['call_back'](d['name'])
                print ('value for %s is '+d['format']) % (d['name'],  v)
            time.sleep(15)

    except KeyboardInterrupt:
        time.sleep(0.2)
        os._exit(1)
    except StandardError:
        print sys.exc_info()[0]
        os._exit(1)
