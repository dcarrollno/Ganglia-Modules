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

import sys
import re
import read_config as cfg
from loglib import loglib


class Create_Json(object):
    ''' Here we create the json graph definitions to submit
            to our web tree using objects '''

    def __init__(self,sname,metric,graphit):

        self.sname = sname
        self.metric = metric
        self.graphit = graphit


        if not self.graphit:
            # no metrics were found meeting requirements
            return(None)

        # Template for top5 graph types
        output = '''
           {
            "report_name" : "AAA_BBB_report",
            "report_type" : "standard",
            "title" : "TITLE",
            "vertical_label" : "TYPEOF",
            "series" : [

        '''
        output = re.sub('AAA',self.sname,output)
        output = re.sub('BBB',self.metric,output)
        output = re.sub('TITLE',self.metric,output)
        output = re.sub('TYPEOF',self.metric,output)


        # open graph for writing
        self.outfile = cfg.GraphDir+'/'+self.sname+'_'+self.metric+'_report.json'
        #self.outfile = '/tmp/'+self.sname+'_'+self.metric+'_report.json'	# debug
	with open(self.outfile,'w') as fo:

            graph_colors = ["0000FF","dd0000","c334cb","02FD6F","FFD501"]

            for self.color, self.dmet in zip(graph_colors,graphit):
                self.dmet = re.sub('.rrd','',self.dmet)
                self.outstr = '{ "metric": "'+self.dmet+'", "color": "'+self.color+'", "label": "'+self.dmet+'", "type": "line" },\n'
                output+=self.outstr

            output = output[:-2]   # strip off trailing comma in last metric which will break json

            closing = '''
                ]
              }
            '''
            output+=closing

            fo.write(output)	##### uncomment when ready to write files out
        del graphit[:]
