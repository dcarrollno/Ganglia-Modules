#!/usr/bin/python

import os
import sys
import re
import web
import signal
import netifaces as ni
import get_metric_value as gmv
from check_redis import Check_Redis_GangliaRest
from loglib import loglib

''' /* This module requires:
       easy_install web.py
       pip install netifaces

       FYI: This requires classes not included that are
       part of packages I am unable to share so you will
       need to disable loglib, or substitute your own in.

       Of course, this is meant to run inside of a protected
       network, not exposed to the public. 

   */
'''

logfile = '/var/log/GangliaRest.log'
web.config.debug = False
statefile = '/tmp/gangliaRest.state'

class GangliaRest(object):
    ''' Here we prime the web api to accept specific requests for
        metrics. Requests must match the urls section '''


    def __init__(self,host='0.0.0.0',port=8659):

        self.host = host
        self.port = port


        # Specific requets assigned to class

        urls = ( '/node/(.*)/get_metric/(.*)', 'GetMetric',
                 '/test(.*)', 'Test' )

        app = web.application(urls,globals())
        web.httpserver.runsimple(app.wsgifunc(), (host,port))

        loglib(logfile,"INFO: Started GangliaRest on IP %s and port %s" % (self.host,self.port))

    def printit(self):

        print("Listening on %s with port %s" % (self.host,self.port))


class Test(object):
    ''' Quick testing '''

    def GET(self,arg):
        resp = "Hello"+arg
        return(resp)


class GetMetric(object):
    ''' Responsible for getting the requested Ganglia
        metric last val '''


    ''' We like to trend how busy our Ganglia API is '''
    reqsCount = 0
    respCount = 0
    errorCount = 0


    def __init__(self):
        ''' constructor '''


    def printit(self):
        print("Reqs %s" % reqsCount)
        print("Resp %s" % respCount)
        print("Error %s" % errorCount)


    def locate_file(self,node,file):
        ''' We no longer use the locate_file method as we now prefer
            using our Redis cache powered locator instead.  Leaving this
            in place as an example for those without Redis.  


            Here we need to find where the metric lives in the Ganglia
            tree. We also need to account for nodes that are named
            fully-qualified vs. not. '''

        rootDir = '/var/lib/ganglia/rrds/'	# fairly typical

        for dirName, subdirList, fileList in os.walk(rootDir):

            if node in subdirList or node+'.domain.com' in subdirList:
                loglib(logfile,"Node %s found in dirName %s" % (node,dirName))
                metric = [i for i in os.listdir(dirName+'/'+node) if i == file]
                loglib(logfile,"Metric match %s" % metric)
                location = os.path.abspath(dirName+'/'+node+'/')
                loglib(logfile,'Path is %s' % location)


            else:
                #loglib(logfile,"Node %s NOT found in dirName %s" % (node,dirName))
                pass


        return(location)



    def GET(self,node='None',req='None'):
        ''' pass metric req list to get_metric_value '''


        self.metric_list = []
        self.node = node
        self.req = req+'.rrd'


        loglib(logfile,'REQUEST: request for metric %s on node %s' % (self.req,self.node))

        locateDir = Check_Redis_GangliaRest(self.node)
        self.hostLocation = locateDir.redis_lookup()
        self.metric = [i for i in os.listdir(self.hostLocation) if i == self.req]

        #loglib(logfile,'INFO: Found location as %s' % self.hostLocation)
        #loglib(logfile,'INFO: Checking metric %s' % self.metric)

        GetMetric.reqsCount +=1

        self.metric_list.append(self.req)

        #loglib(logfile,'Appending %s to metric_list' % self.metric)
        #loglib(logfile,'Sending %s and %s to gmv' % (self.hostLocation,self.metric_list))

        ans = gmv.GetMetricValue(self.hostLocation,self.metric_list)

        try:
            for k,v in ans.to_sort.items():
                print k,v
                loglib(logfile,"RESPONSE: returning value of %s for metric %s" % (k,v))
                GetMetric.respCount +=1

        except Exception as e:
            GetMetric.errorCount +=1
            print(e)
            loglib(logfile,"ERROR: Error thrown was %s" % e)

        with open(statefile,'w') as f:
            f.write("Reqs: %d\n" % GetMetric.reqsCount)
            f.write("Resp: %d\n" % GetMetric.respCount)
            f.write("Errs: %d\n" % GetMetric.errorCount)


        return(v)


def set_exit_handler(func):
    signal.signal(signal.SIGTERM, func)

def on_exit(sig, func=None):
    print "exit handler triggered"
    loglib(logfile,'WARN: Exiting program')
    sys.exit(1)

def get_Eth0():
    ''' We want to ensure we only listen on internal IP
        which is protected from the outside world '''

    ni.ifaddresses('eth0')
    ip = ni.ifaddresses('eth0')[2][0]['addr']
    return(ip)


if __name__ == "__main__":

    set_exit_handler(on_exit)

    listenIp = get_Eth0()

    gangliarest = GangliaRest(host=listenIp,port=8659)
