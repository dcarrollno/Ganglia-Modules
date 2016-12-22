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
import re
import sys
import redis
from redis import ConnectionError
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

        ''' We have to aquire both hostname and fqdn to test '''

        if self.hostname.endswith(cfg.domain):
            self.non_fqdn = self.hostname.split('.',1)[0]
            self.fqdn = self.hostname
             
        else:
            self.non_fqdn = self.hostname
            self.fqdn = self.hostname+'.'+cfg.domain



    def is_redis_available(self,conn):
        ''' Check if Redis running and available - if not write hint to logfile ''' 

        try:
            conn.get(None)  # getting None returns None or throws an exception

        except (redis.exceptions.ConnectionError, 
            redis.exceptions.BusyLoadingError):
            if os.path.isfile('var/run/redis/redis.pid'):
                loglib(self.logfile,"WARN: Redis pid file exists but problem connecting to Redis")
            else: 
                loglib(self.logfile,"ERROR: Redis is not responding and no pidfile was found. Ensure Redis is running")

        try:
            conn.ping()

        except:
            loglib(self.logfile,"ERROR: Redis is not reachable. Ensure it is configured correctly, and check /etc/GangliaRest.cfg for proper configuration.")
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
        if r.exists(self.fqdn):
            self.location = r.get(self.fqdn)
            loglib(self.logfile,"CACHE HIT: Redis: returning %s in Check_Redis_GangliaRest:redis_lookup" % self.location)
            return(self.location)

        elif r.exists(self.non_fqdn):
            self.location = r.get(self.non_fqdn)
            loglib(self.logfile,"CACHE HIT: Redis: returning %s in Check_Redis_GangliaRest:redis_lookup" % self.location)
            return(self.location)   
 
	else:
	    ''' location not found in cache, find in filesystem and load into cache
                to improve lookup performance for API requests. Because we may have been
                passed either a hostname or fqdn to search for, we'll have to look for both '''

	    try:
	        for dirName, subdirList, fileList in os.walk(self.rootDir):
                    for host in subdirList:
			''' We have to account for hosts that were named fqdn
			    or simply by hostname, or we will fail to locate '''
                        m = re.match(self.non_fqdn, host)
                        if m:
			    self.hostname = host	# reset the host to the correct name on fs
			    #loglib(self.logfile,"INFO: Host being set as %s" % self.hostname)
		            self.location = os.path.abspath(dirName+'/'+self.hostname)

			    ''' Now we need to add to our Redis cache with a TTL of one day
				to account for transitory systems like VM's that spin down '''
			    try:
			        #print("Setting key for %s and val %s" % (self.hostname,self.location))
			        r.setex(self.hostname, self.location, cfg.redisTtl)
			        return(self.location)

	                    except:
				loglib(self.logfile,"ERROR: Error writing to Redis under Check_Redis_GangliaRest:redis_lookup")
			        exit(1)

		        else:
			    #loglib(self.logfile,"ERROR: Unable to match requested host %s using match %s in rrdtree under Check_Redis_GangliaRest:redis_lookup" % (host,self.non_fqdn))
			    continue  # we don't want to log every miss


            except:
	        loglib(self.logfile,"ERROR: Unable to find host %s or write to Redis requested host in rrdtree under Check_Redis_GangliaRest:redis_lookup" % host)


if __name__ == "__main__":

    ''' Test code here ''' 

    handle = Check_Redis_GangliaRest(host_here)
    handle.redis_lookup()
