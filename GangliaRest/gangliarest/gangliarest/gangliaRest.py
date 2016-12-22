#!/usr/bin/python

import os
import sys
import re
import web
import time
import signal
import threading
import netifaces as ni
import get_metric_value as gmv
import read_config as cfg
from check_redis import Check_Redis_GangliaRest
from loglib import loglib
import indexer
import update_notify


''' /* This module requires:
       easy_install web.py
       pip install netifaces
   */
'''

web.config.debug = False
statefile = cfg.statsFile 



class GangliaRest(object):
    ''' Here we prime the web api to accept specific requests for
        metrics. Requests must match the urls section '''


    def __init__(self,host='0.0.0.0',port=8653):

        self.host = cfg.restHost
        self.port = cfg.restPort


        # Specific requets assigned to class. 

        urls = ( '/node/(.*)/get_metric/(.*)', 'GetMetric',
                 '/test(.*)', 'Test' )

        app = web.application(urls,globals())
        web.httpserver.runsimple(app.wsgifunc(), (self.host,self.port))

        loglib(cfg.logfile,"INFO: Started GangliaRest on IP %s and port %s" % (self.host,self.port))



    def printit(self):

        print("Listening on %s with port %s" % (self.host,self.port))



class Test(object):

    def GET(self,arg):
        resp = "Hello"+arg
        return(resp)



class GangliaRestScheduler(object):
    ''' The GangliaRestScheduler is a background process that
        will run user-defined jobs on an approximate schedule 
        or handle internal operations such as sw update checking
        and cache priming. '''

    primed = False		# default for cache primed
    swupdate_checked = False    # default for sw update status

    def __init__(self, interval=60):
        ''' The interval variable is not user defined ''' 


        self.__interval = interval
        self.__swupdateFreq = 86400 

        thread = threading.Thread(target=self.schedulerDaemon, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution


    def runSwUpdate(self):
        ''' This method checks periodically for new gangliarest releases '''

        self.swupdate_now = time.time()
        
        ''' We want to check for new software releases on GangliaRest start up
            but then, only once per day thereafter. We assume logrotate may
            be configured to rotate daily on most systems so we hope our update
            message appears and is caught in a daily log. '''

        if not self.swupdate_checked: 
            try:
                sw_update = update_notify.CheckforUpdates('gangliarest')
                check = sw_update.compareCheck() 
                self.swupdate_checked = True
                self.swupdate_last_check = time.time()
            except:
                # a sw update check failure is not fatal to operations
                pass

        if self.swupdate_last_check: 
            self.swupdate_diff = self.swupdate_now - self.swupdate_last_check
            if self.swupdate_diff > self.__swupdateFreq:
                try:
                    sw_update = update_notify.CheckforUpdates('gangliarest')
                    check = sw_update.compareCheck()
                    self.swupdate_checked = True
                    self.swupdate_last_check = time.time()
                except:
                    # a sw update check failure is not fatal to operations
                    pass



    def runIndexer(self):
        ''' This method is responsible for running the Indexer at both
            internal and user-defined times. '''

        self.indexer_now = time.time()
       
        # Primer 
        if not self.primed:
            loglib(cfg.logfile,"INFO: INDEXER: Running Indexer for first time to prime cache.")
            try:
                firstrun_indexer = indexer.GangliaIndexer()
                firstrun_indexer.indexTimer()
                self.indexer_last_check = time.time()
                self.primed = True
            except:
                loglib(cfg.logfile,"ERROR: INDEXER failed to prime cache on first run.")
                self.primed = False

        try:
            if self.indexer_last_check:
                self.indexer_diff = self.indexer_now - self.indexer_last_check
                if self.indexer_diff > cfg.indexFreq:
                    loglib(cfg.logfile,"INFO: GangliaRest scheduler running Indexer on schedule. Starting indexing")
                    run_indexer = indexer.GangliaIndexer()
                    run_indexer.indexTimer()
                    self.indexer_last_check = time.time() 
                else:
                    #print("Not time to run indexer")  # debug
                    #loglib(cfg.logfile,"INFO: Timer indicates no need to run indexing. Sleeping for now")
                    pass
        except:
            # Setting first marker
            self.indexer_last_check = self.indexer_now



    def schedulerDaemon(self):
        ''' This method lists the scheduled jobs that need to be run. Add new methods
            under this class and then list the calls here to have them run. By default
            these jobs are checked every 60 secs to see if they meet criteria to run ''' 

        while True:

            # See if time to run the Indexer - This may run to prime the cache 
            # but is otherwise user-configurable in /etc/GangliaRest.cfg
            self.runIndexer()

            # See if time to run software update check
            self.runSwUpdate()
               
 
            # Scheduled jobs are listed above 
            time.sleep(self.__interval)



class GetMetric(object):
    ''' Responsible for getting the requested Ganglia
        metric last val '''

    reqsCount = 0
    respCount = 0
    errorCount = 0

    def __init__(self):
        ''' Here we keep track of requests, responses and errors as we
            like to trend those too in Ganglia using another module  '''


    def printit(self):
        print("Reqs %s" % reqsCount)
        print("Resp %s" % respCount)
        print("Error %s" % errorCount)


    def locate_file(self,node,file):
        ''' Here we need to find where the metric lives in the Ganglia
            tree. We also need to account for nodes that are named
            fully-qualified vs. not or searches will fail to match '''


        for dirName, subdirList, fileList in os.walk(cfg.rrdDir):


            loglib(cfg.logfile,"Node passed in was %s" % node)
            if node in subdirList or node+'.'+cfg.domain in subdirList:

		if os.path.abspath(dirName+'/'+node+'/'):
	            loglib(cfg.logfile,"Node %s found in dirName %s" % (node,dirName))
	            location = os.path.abspath(dirName+'/'+node+'/')
		else:
		    # Likely this is either a fqdn being passed in or needs to be
		    if node.endswith('.'+cfg.domain):
  		        node = re.sub('.'+cfg.domain,'',node)
		    else:
			node = node+'.'+cfg.domain

		    location = os.path.abspath(dirName+'/'+node+'/')
		    loglib(cfg.logfile,'Path is %s' % location)

            else:
		loglib(cfg.logfile,"Node %s NOT found in dirName %s" % (node,dirName))
		pass

        return(location)



    def GET(self,node='None',req='None'):
        ''' pass metric req list to get_metric_value '''

        self.metric_list = []
        self.node = node
        self.req = req+'.rrd'


        loglib(cfg.logfile,'REQUEST: request for metric %s on node %s' % (self.req,self.node))

        try:
	    locateDir = Check_Redis_GangliaRest(self.node)
            self.hostLocation = locateDir.redis_lookup()
        except:
            print("Error: Node not found in Redis cache or on filesystem")
            return('Not Found')

        if self.hostLocation is None:
            loglib(cfg.logfile,"WARN: Request for %s yielded no results. Did you set domain correctly in GangliaRest.cfg? Double-check your API request." % self.node)
            # Return a simple error for scripts to parse
            return('Not_Found') 
 
        self.metric = [i for i in os.listdir(self.hostLocation) if i == self.req]

        #loglib(cfg.logfile,'INFO: Found location as %s' % self.hostLocation)
        #loglib(cfg.logfile,'INFO: Checking metric %s' % self.metric)

        GetMetric.reqsCount +=1

        self.metric_list.append(self.req)

        #loglib(cfg.logfile,'Appending %s to metric_list' % self.metric)
        #loglib(cfg.logfile,'Sending %s and %s to gmv' % (self.hostLocation,self.metric_list))

        ans = gmv.GetMetricValue(self.hostLocation,self.metric_list)

        try:
            for k,v in ans.to_sort.items():
                loglib(cfg.logfile,"RESPONSE: returning value of %s for metric %s" % (k,v))
                GetMetric.respCount +=1
        except Exception as e:
            GetMetric.errorCount +=1
            #print(e)
            loglib(cfg.logfile,"ERROR: Error thrown was %s" % e)

        with open(statefile,'w') as f:
            f.write("Reqs: %d\n" % GetMetric.reqsCount)
            f.write("Resp: %d\n" % GetMetric.respCount)
            f.write("Errs: %d\n" % GetMetric.errorCount)


        return(v)




def set_exit_handler(func):
    signal.signal(signal.SIGTERM, func)

def on_exit(sig, func=None):
    print "exit handler triggered"
    loglib(cfg.logfile,'WARN: Exiting program')
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

    cfg.readConfig()
    jobs_scheduler = GangliaRestScheduler()
    gangliarest = GangliaRest(host=listenIp,port=8653)
