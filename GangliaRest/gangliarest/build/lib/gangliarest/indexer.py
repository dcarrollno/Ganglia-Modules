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

import os
import sys
import time
import redis
import read_config as cfg
from loglib import loglib


cfg.readConfig()

rootDir = cfg.rrdDir 


class GangliaIndexer(object):
    ''' Indexer class. This class contains two methods
        which are responsible for indexing operations. Indexing
        the locations of Ganglia node directories into Redis speeds
        up access and response time for API clients requesting metric
        info.  '''

    # Set in /etc/GangliaRest.cfg and defines how often we index
    indexer_frequency = cfg.indexFreq 
    index_adds = 0


    def __init__(self):
        ''' Constructor '''


    def indexer(self):
        ''' The indexer method is responsible for establishing
            a connection to the local Redis DB, walking the Ganglia
            RRD tree and indexing directory locations into Redis. We
            do this so we do not need to walk the entire filesystem 
            looking for metric locations. '''
 
        
        r = redis.Redis(
            host = cfg.redisHost,
            port = cfg.redisPort,
            db = cfg.redisDb,
            password = cfg.redisAuth)
 

        try:
            for dirName, subdirList, fileList in os.walk(rootDir):
                for host in subdirList:
                    location = os.path.abspath(dirName+'/'+host)
                    if host.startswith('__SummaryInfo__'):
                        continue
                    else:
                        try:
                            #print("Adding host %s to Redis" % host) 
                            r.setex(host,location,cfg.redisTtl)
                            self.index_adds +=1
                            stat = True
                        except:
                            print("ERROR: Error inserting host into Redis")
                            loglib(cfg.logfile,"ERROR: Indexer failed to index host %s" % host)
                            stat = False
        except Exception as e:
            #print("Failed to scan filesystem")
            loglib(cfg.logfile,"ERROR: INDEXER failed. Error reported was %s" % e)
            stat = False


        return(stat)  # in case we want a return status


    def indexTimer(self):
        ''' The indexTimer method historically was responsible for managing
            timed runs - whether to run an indexing or not but has been 
            depreciated and now just acts as a calling method. This was when
            this particular class used multithreading but no longer does. ''' 

        try:

            #print("Running indexer on schedule")
            loglib(cfg.logfile,"INFO: INDEXER starting scheduled operations...")
            runner = self.indexer()
            if runner:
                #print("Completed indexing")
                loglib(cfg.logfile,"INFO: INDEXER completed run...Added %s entries to Redis" % self.index_adds)
                return()
            else:
                print("Indexing failed receiving a False from the indexer method.")
                return()

        except Exception as e:
            #print("Indexing failed. Exception thrown was %s" % e)
            loglib(cfg.logfile,"ERROR: INDEXER threw an error of %s" % e)

        return()


if __name__ == "__main__":

    cfg.readConfig()   

    # Debugging
    #myHandle = GangliaIndexer()
    #while True:
    #    last_run = myHandle.indexTimer()
    #    time.sleep(15)

