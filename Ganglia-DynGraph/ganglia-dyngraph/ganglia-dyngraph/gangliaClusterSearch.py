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
from loglib import loglib
import read_config as cfg


METRICS = {}

class GangliaClusterSearch(object):
    ''' This class handles locating nodes and metrics as defined by
        the requested configuration. '''


    # Set a default here in case unspecified by calling program
    # Set an instance attribute to override
    RRDDIR='/var/lib/ganglia/rrds'


    def __init__(self,cluster):
        ''' take a cluster as an object, use methods
            to find values etc.. '''

        self.cluster = cluster


    def __str__(self):
        return str(self.cluster)



    def excludeList(self,nodename):
        ''' Maintain exclusion list of nodes to ignore. In the future we'll
            make this a configurable option '''

        self.nodename = nodename

        excludes = ('__SummaryInfo__','lxphap')

        if self.nodename.startswith(('__SummaryInfo__','lxphap')):
            return(True)

        return(False)



    def findClusterMembers(self):
        ''' Find nodes belonging to clusters, and return a list per object '''


        nodes = [x for x in os.listdir(cfg.RRDDIR+'/'+self.cluster) if self.excludeList(x) == 0]

        return(nodes)



    def findNodeMetrics(self,node,metric_list):
        ''' Find metrics belonging to nodes and return a compound dict '''

        self.node = node
        self.metric_list = metric_list

        METRICS[self.node]={}

        for x in self.metric_list:
            metrics = [i for i in os.listdir(self.node) if i.startswith(x)]
            METRICS[self.node][x]=metrics

        return(METRICS)
