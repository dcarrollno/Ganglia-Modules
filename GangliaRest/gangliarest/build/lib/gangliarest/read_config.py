########################################
#
# This file part of the gangliarest package
#
# https://pypi.python.org/pypi/gangliarest
#
# https://github.com/dcarrollno/Ganglia-Modules/wiki/GangliaRest-API:-Part-I
#
# Dave Carroll - davecarrollno@gmail.com
#
########################################


import ConfigParser
import sys 
import re


#redisConf = '/etc/redis.conf'

def get_redis_auth():
    with open(redisConf, 'r') as f:
        for line in f:
            if line.startswith('requirepass'):
                (label,pw) = line.split()
                return(pw)
            if line.startswith('#requirepass'):
                return(False)
 

def readConfig():
    ''' Here we ingest the /etc/GangliaRest.cfg options. These options are only
        read once at startup of GangliaRest so any change to options requires a restart. '''


    global Config,redisHost,redisAuth,redisPort,redisDb,logfile,rrdDir,restPort, \
           restHost,domain,indexFreq,redisTtl,logLevel,statsFile,redisConf


    Config = ConfigParser.ConfigParser()
    Config.read("/etc/GangliaRest.cfg")

    redisConf = Config.get('Redis','redisConf')
    restHost = Config.get('Globals','restHost')
    restPort = Config.get('Globals','restPort')
    restPort = int(restPort)
    domain = Config.get('Globals','domain')
    logfile = Config.get('Globals','logfile')
    logLevel = Config.get('Globals','logLevel')
    rrdDir = Config.get('Globals','rrdDir')
    statsFile = Config.get('Globals','statsFile')

    redisHost = Config.get('Redis','redisHost')
    redisPort = Config.get('Redis','redisPort')
    redisPort = int(redisPort)
    redisDb = Config.get('Redis','redisDb')
    redisDb = int(redisDb)
    redisTtl = Config.get('Redis','redisTtl')
    redisTtl = int(redisTtl)
    redisAuth = get_redis_auth()

    indexFreq = Config.get('Indexer','indexFreq')
    indexFreq = int(indexFreq)


if __name__ == "__main__":

    readConfig()
    get_redis_auth()
    print(logLevel)
