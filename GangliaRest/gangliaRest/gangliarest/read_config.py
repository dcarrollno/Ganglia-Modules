#!/usr/bin/python
#
# This file is part of gangliaRest
#
#  Dave Carroll - davecarrollno@gmail.com 2013
#

import ConfigParser
import sys 
import re
from loglib import loglib

def readConfig():
    ''' Here we ingest the /etc/GangliaRest.cfg options. These options are only
        read once at startup of GangliaRest so any change to options requires a restart. '''


    global Config,redisHost,redisAuth,redisPort,redisDb,logfile,rrdDir,restPort,restHost,domain


    Config = ConfigParser.ConfigParser()
    Config.read("/etc/GangliaRest.cfg")

    restHost = Config.get('Globals','restHost')
    restPort = Config.get('Globals','restPort')
    restPort = int(restPort)
    domain = Config.get('Globals','domain')
    logfile = Config.get('Globals','logfile')
    rrdDir = Config.get('Globals','rrdDir')

    redisHost = Config.get('Redis','redisHost')
    redisPort = Config.get('Redis','redisPort')
    redisPort = int(redisPort)
    redisDb = Config.get('Redis','redisDb')
    redisAuth = Config.get('Redis','redisAuth')

    loglib(logfile,"INFO: Reading /etc/GangliaRest.cfg")


if __name__ == "__main__":

    readConfig()
    print restHost
    print restPort
    print domain
    print logfile
    print rrdDir
    print redisHost
    print redisPort
    print redisDb
    print redisAuth
