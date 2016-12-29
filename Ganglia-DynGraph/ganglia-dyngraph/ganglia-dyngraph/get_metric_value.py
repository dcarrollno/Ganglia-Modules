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

import os,sys,re
from subprocess import Popen,PIPE,STDOUT
import read_config as cfg
from loglib import loglib


class GetMetricValue(object):
    ''' Here we look up the value of the metric that passed the expiration test. '''


    def __init__(self,nodepath,activeList):
        ''' '''

        self.nodepath = nodepath
        self.activeList = activeList
        logfile = 'None' # override with instance attribute


        # Store metric values in a dict so we can sort next by top5
        self.to_sort = {}


        for self.metric in self.activeList:
            #print("Checking metric %s located at path %s" % (self.metric,self.nodepath))
            cmd3 = ' | grep "last_ds"'
            newcmd = '/usr/bin/rrdtool info '+ self.nodepath+'/'+self.metric + cmd3
            # Get last_ds and file name from rrdtool for each api_https metric
            p1 = Popen(newcmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
            output1 = p1.stdout.read()

            try:
                self.lastds,self.val = output1.split('=')
                self.val = self.val.replace('"','').strip()

                if isinstance(self.val, int):
                    self.val = int(self.val)
                if isinstance(self.val, float):
                    self.val = float(self.val)

                self.to_sort[self.metric]=self.val
                #print("Metric %s has a value of %s" % (self.metric,self.val))
                #loglib(logfile,'INFO: LastDS for %s on node %s is %s' % (self.metric,self.sname,val))

            except Exception as e:
                loglib(logfile,'ERROR: Unable to get last ds for metric %s. Error thrown was %s' % (self.metric,e))
                #print e
                #print("Unable to get last ds for metric %s" % self.metric)
	        continue


if __name__ == "__main__":


    pass
    '''
    nodepath = '/var/lib/ganglia/rrds/<cluster>/<node>'
    metric = ['diskstat_sda_io_time.rrd']

    res = GetMetricValue(nodepath,metric)
    '''
