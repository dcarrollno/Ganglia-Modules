#!/usr/bin/python

#
# This file part of the gangliaRest package
#

import os
import re
import sys
import redis
from loglib import loglib
import read_config as cfg

cfg.readConfig()

class Check_Redis_GangliaRest(object):
    ''' This class is responsible for handling our Ganglia RRD locations.
        We use a Redis DB instance to cache file system locations to lessen
        walking the filesystem when locating metrics under the rrd tree. ''' 


    rootDir = cfg.rrdDir 
    logfile = cfg.logfile 

    def __init__(self,hostname):
        ''' We are looking for our hostnames in our rrd tree '''

        self.hostname = hostname


    def is_redis_available(self,conn):
        ''' Check if Redis running and available '''

        try:
            conn.get(None)  # getting None returns None or throws an exception

        except (redis.exceptions.ConnectionError, 
            redis.exceptions.BusyLoadingError):
            loglib(self.logfile,"WARN: Redis did not respond. Check to ensure it is running")
            return False

        return True


    def redis_lookup(self):

        r = redis.Redis(
	    host = cfg.redisHost,
  	    port = cfg.redisPort,
            db = cfg.redisDb,
            password = cfg.redisAuth)

        redisStatus = self.is_redis_available(r)

	# Check our cache for host location
        if r.exists(self.hostname):
            self.location = r.get(self.hostname)
            loglib(self.logfile,"CACHE HIT: Redis: returning %s in Check_Redis_GangliaRest:redis_lookup" % self.location)
            return(self.location)

	else:
	    ''' location not found in cache, find in filesystem and load into cache
                to improve lookup performance for API requests '''
	    try:
	        for dirName, subdirList, fileList in os.walk(self.rootDir):
                    for host in subdirList:
			''' We have to account for hosts that were named fqdn
			    or simply by hostname, or we will fail to locate '''
                        if host.startswith(self.hostname):
			    self.hostname = host	# reset the host to the correct name on fs
			    loglib(self.logfile,"INFO: Host being set as %s" % self.hostname)
		            self.location = os.path.abspath(dirName+'/'+self.hostname)

			    ''' Now we need to add to our Redis cache with a TTL of one day
				to account for transitory systems like VM's that spin down '''
			    try:
			        #print("Setting key for %s and val %s" % (self.hostname,self.location))
			        r.setex(self.hostname, self.location, 60)
			        return(self.location)

	                    except:
				loglib(self.logfile,"ERROR: Error writing to Redis under Check_Redis_GangliaRest:redis_lookup")
			        exit(1)

		        else:
			    loglib(self.logfile,"ERROR: Unable to find requested host in rrdtree under Check_Redis_GangliaRest:redis_lookup")
			    continue  # we don't want to log every miss


            except:
	        loglib(self.logfile,"ERROR: Unable to find or write to Redis requested host in rrdtree under Check_Redis_GangliaRest:redis_lookup")


if __name__ == "__main__":

    ''' Test code here ''' 

    handle = Check_Redis_GangliaRest('netwatch')
    handle.redis_lookup()
