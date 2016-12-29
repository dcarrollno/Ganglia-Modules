########################################
#
# This file part of the ganglia-dyngraph package
#
# https://pypi.python.org/pypi/ganglia-dyngraph
#
# https://github.com/dcarrollno/Ganglia-Modules/wiki/Overview:-Ganglia-Dynamic-Metrics%3F 
#
# Dave Carroll - davecarrollno@gmail.com
#
########################################

import os
import sys
import time
import re
import read_config as cfg
from loglib import loglib
from subprocess import Popen,PIPE,STDOUT



class CheckMetricTimeStamp(object):
    ''' We pass in a list of metrics to check with the intent to check last ds on each '''

    def __init__(self,nodepath,metricList):
        ''' This class expects a fully-qualified node path and a list of metrics to process.
            Nodepath would look like /var/lib/ganglia/rrds/<cluster>/<node>/.
            The metricList contains metrics identified per cluster, per node and as defined by
            DynamicGraph.cfg. '''

        self.nodepath = nodepath
        self.metricList = metricList
        self.current_time = time.time()
        self.currentMetricList = []
        self.expiredMetricList = []
        self.summaryMetric = self.nodepath.rsplit('/',1)[0]+'/__SummaryInfo__/'

    def printit(self):
        ''' Print method '''

        print("The nodepath is %s" % self.nodepath)
        print("The list being checked is %s" % self.metricList)
        print("The summaryMetric is %s" % self.summaryMetric)


    def checktime(self):

        if not self.metricList:
            # for some reason no metrics were found matching requirements for this node
            #print("WARN: List was passed in blank")
            return()


        for self.m in self.metricList:
            #print("Checking metric %s" % self.m)

            lastupdate = ' | grep "last_update"'
            checklast = '/usr/bin/rrdtool info '+ self.nodepath+'/'+self.m + lastupdate


            p0 = Popen(checklast, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            output0 = p0.stdout.read()

            try:
                (self.lastvaldef,self.lastval) = output0.split('=')
                self.lastval = float(self.lastval)
                self.diffit = self.current_time - self.lastval

            except:
                loglib(cfg.logfile,'WARN:  Unable to run lastupdate.  Metric may have disappeared')
                #print("WARN: Unable to run lastupdate on metric %s" % self.m)
                continue

            if self.diffit > cfg.expireTime:
                self.expiredMetricList.append(self.nodepath+'/'+self.m)
                # add the __SummaryInfo__ metric path to the list as well
                summaryMetric = self.summaryMetric+self.m
                self.expiredMetricList.append(summaryMetric)
            else:
                self.currentMetricList.append(self.m)  # collect valid metrics to sort


        # We replace our original list of metrics with just the unexpired ones
        self.metricList = self.currentMetricList[:]

        return(self.metricList)
