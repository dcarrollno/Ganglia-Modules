########################################
#
# This file part of the ganglia-dyngraph package
#
# https://pypi.python.org/pypi/ganglia-dyngraph
#
# https://github.com/dcarrollno/Ganglia-Modules/wiki/GangliaRest-API:-Part-I
#
# Dave Carroll - davecarrollno@gmail.com
#
########################################


def readConfig():
    ''' Here we ingest the /etc/DynamicGraph.cfg options. These options are only
        read once at startup of DynamicGraph so any change to options requires a restart. '''

    import ConfigParser
    import re,sys
    import loglib

    global GraphDir,RRDDIR,logfile,runTime,expireTime,purged_metric_count,purged_error_count,numMetrics,metric_pkgs


    metric_pkgs = {}
    purged = 0
    purge_errors = 0

    Config = ConfigParser.ConfigParser()
    Config.read("/etc/DynamicGraph.cfg")

    purged_metric_count = Config.get('Globals','purged_metric_count')
    purged_error_count = Config.get('Globals','purged_error_count')
    logfile = Config.get('Globals','logfile')
    GraphDir = Config.get('Globals','GraphDir')
    RRDDIR = Config.get('Globals','RRDDIR')
    runTime = Config.get('Globals','runTime')
    runTime = int(runTime)
    expireTime = Config.get('Globals','expireTime')
    expireTime = int(expireTime)
    numMetrics = Config.get('Globals','numMetrics')
    numMetrics = int(numMetrics)

    for section_name in Config.sections():
        if section_name.startswith('Cluster_'):
            for name, value in Config.items(section_name):
                section_name = re.sub('Cluster_','',section_name)
                metric_pkgs[section_name]=value
                #print '  %s %s = %s' % (section_name,name, value)              # list of metrics
                values = value.split(',')
                metric_pkgs[section_name]=values                # now we have a dict of lists of metrics to include as dynamic
                # looks like metric_pkgs['API_DAL01']=('api_top5_http_events','api_top5_https_events','api_top5_mobile_http_events','api_top5_mobile_https_events')


    return(metric_pkgs)

if __name__ == '__main__':

    readConfig()
