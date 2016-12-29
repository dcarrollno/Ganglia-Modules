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
import read_config as cfg
from loglib import loglib

class PurgeMetrics(object):


    def __init__(self,expiredMetricList):
        ''' This class expects a list of metrics to process'''

        self.expiredMetricList = expiredMetricList


    def purge(self):


        if not self.expiredMetricList:
            #print("WARN: An empty list was sent to PurgeMetrics")
            return()

        for self.met in self.expiredMetricList:

            try:
                os.remove(self.met)	
                loglib(cfg.logfile,'INFO: Metric %s successfully purged' % self.met)
                self.metpurge = 0
            except:
                loglib(cfg.logfile,'WARN: Purge of metric %s encountered an error.' % self.met)
                #print("Error purging metric %s" % self.met)
                self.metpurge = 1

            finally:
                if self.metpurge == 0:
                    cfg.purged +=1
		    #print("Adding to purge. Count is now %s" % cfg.purged)
                else:
                    cfg.purge_errors +=1
