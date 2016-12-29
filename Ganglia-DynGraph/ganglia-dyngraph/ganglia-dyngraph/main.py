#!/usr/bin/env python
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
import re
import time
import read_config as cfg
import signal
from gangliaClusterSearch import GangliaClusterSearch
from checkMetricTimeStamp import CheckMetricTimeStamp
from purge_metrics import PurgeMetrics
from get_metric_value import GetMetricValue
import high_vals
from loglib import loglib
from create_json import Create_Json



def set_exit_handler(func):
    signal.signal(signal.SIGTERM, func)

def on_exit(sig, func=None):
    print "exit handler triggered"
    sys.exit(1)



if __name__ == '__main__':


    set_exit_handler(on_exit)
    metric_pkgs = cfg.readConfig()


    loglib(cfg.logfile,'INFO: Starting DynamicGraph...')

    while True:

        cfg.purged = 0
        cfg.purge_errors = 0


        # Create a new object per cluster
        for cluster,metric_list in metric_pkgs.items():
            fqmn = cfg.RRDDIR+'/'+cluster+'/'
            cluster = GangliaClusterSearch(cluster)
            cluster.RRDDIR=cfg.RRDDIR
            nodes = cluster.findClusterMembers()

            # We next build a data asset containing all metrics grouped by node and metric type
            for shortName in nodes:
                METRICS = cluster.findNodeMetrics(fqmn+shortName,metric_list)


        # Now we loop through data asset to process metrics
        for node,outerv in METRICS.items():     # gives us each Node
            for metric,metricList in outerv.items():  #gives us metric type and actual list of rrds found
                nodeinstance = node+'_'+metric	# instance will be node_metric
                sname = node.rsplit('/',1)[1]	# just nodename
                summaryDir = node.rsplit('/',1)[0]	#
                summaryDir = summaryDir+'/'+'__SummaryInfo__'
                #print("nodeinstance is %s" % nodeinstance)	# fqmn
                #print("SummaryDir is %s" % summaryDir)	# SummaryDir is the Summary location
                #print("Sname is %s" % sname)

                nodeinstance = CheckMetricTimeStamp(node,metricList)    # create instance based upon node and metric type - should be 4 instances then per node
                #nodeinstance.printit()						# print vars passed in
                activeList = nodeinstance.checktime()
                #print(activeList)						# print only active list
                #print nodeinstance.__dict__					# debug - look at state
                #print("ExpiredMetricList is %s" % nodeinstance.expiredMetricList)	# print only expiredmetriclist

                # Now we have activeList and expiredMetricList saved in state so time to purge old metrics

                nodeinstance = PurgeMetrics(nodeinstance.expiredMetricList)
	        nodeinstance.purge()
                nodeinstance = GetMetricValue(node,activeList)
                nodeinstance.logfile = cfg.logfile
                clean_to_sort = {}
                for k,v in nodeinstance.to_sort.items():
                    k = re.sub(node+'/','',k)       # We need to strip away the fqmn now
                    clean_to_sort[k]=v  # Add back metric without fqmn
                    #print("Node is: %s and k is %s and v is %s" % (node, k, v))
                # Send dict of metrics to high_vals for ranking
                sortedlist = high_vals.high_vals(cfg.numMetrics,'val',clean_to_sort)
                graphit = list()

            for x in sortedlist:
                graphit.append(x[0])
                #print("Adding %s to graphit" % x[0])
            nodeinstance = Create_Json(sname,metric,graphit)


        # We record stats on each run to be graphed by Ganglia
        with open(cfg.purged_metric_count,'w') as fp:
            fp.write("Purged: %s" % cfg.purged)
            #print("Purged is: %s" % cfg.purged)

        with open(cfg.purged_error_count,'w') as ec:
            ec.write("Errors on purging: %s" % cfg.purge_errors)
            #print("Purge errors: %s" % cfg.purge_errors)


        #print("Purged: %s" % cfg.purged)
        #print("Purge Errors: %s" % cfg.purge_errors)

        time.sleep(float(cfg.runTime))
