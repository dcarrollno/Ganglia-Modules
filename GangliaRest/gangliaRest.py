#!/usr/bin/python

''' Ganglia API FrontEnd to Ganglia Metrics. 
    Dave Carroll 
    
    Use this at your own risk, but it should work great.
    This is a simple web server to expose Ganglia metrics
    from one's RRD database files. '''

import os
import sys
import web
import signal
import netifaces as ni
import get_metric_value as gmv	# my class that pulls metric data from rrd files
from loglib import loglib	# proprietary logging lib of mine - you will need your own

''' /* This module requires:
       easy_install web.py
       pip install netifaces
   */
'''

logfile = '/var/log/GangliaRest.log'	# debugging
web.config.debug = False		# disable debugging returned to web clients

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



class GetMetric(object):
    ''' Responsible for getting the requested Ganglia
        metric last val '''

    def locate_file(self,node,file):
        ''' Here we need to find where the metric lives in the Ganglia
            tree. We also need to account for nodes that are named
            fully-qualified vs. not. '''

        rootDir = '/var/lib/ganglia/rrds/'

        for dirName, subdirList, fileList in os.walk(rootDir):

            if node in subdirList or node+'.nanigans.com' in subdirList:
		#loglib(logfile,"Node %s found in dirName %s" % (node,dirName))
                metric = [i for i in os.listdir(dirName+'/'+node) if i == file]
                #loglib(logfile,"Metric match %s" % metric)
                location = os.path.abspath(dirName+'/'+node+'/')
                #loglib(logfile,'Path is %s' % location)

        return(location)


    def GET(self,node='None',req='None'):
        ''' pass metric req list to get_metric_value '''

        self.metric_list = []

        self.node = node
        self.req = req+'.rrd'

        self.fullPath = self.locate_file(self.node,self.req)
        loglib(logfile,'REQUEST: request for metric %s on node %s' % (self.req,self.node))

        self.metric_list.append(self.req)

        #loglib(logfile,'Appending %s to metric_list' % self.req)
        #loglib(logfile,'Sending %s and %s to gmv' % (self.fullPath,self.metric_list))

        ans = gmv.GetMetricValue(self.fullPath,self.metric_list)

        try:
            for k,v in ans.to_sort.items():
                #print k,v
                loglib(logfile,"RESPONSE: returning value of %s for metric %s" % (k,v))
        except Exception as e:
            print(e)
            loglib(logfile,"ERROR: Error thrown was %s" % e)
            return("No Data Returned")

        return(v)


def set_exit_handler(func):
    signal.signal(signal.SIGTERM, func)

def on_exit(sig, func=None):
    print "exit handler triggered"
    loglib(logfile,'WARN: Exiting program')
    sys.exit(1)

def get_Eth0():
    ''' We want to ensure we only listen on internal IP
        Can be set to any interface you desire '''

    ni.ifaddresses('eth0')
    ip = ni.ifaddresses('eth0')[2][0]['addr']
    return(ip)


if __name__ == "__main__":

    set_exit_handler(on_exit)

    listenIp = get_Eth0()

    gangliarest = GangliaRest(host=listenIp,port=8659)
