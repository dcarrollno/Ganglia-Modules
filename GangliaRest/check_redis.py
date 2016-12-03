#
# This file is part of ganglia_tools
#
# Dave C. 2013
#

import os
import re
import sys
import redis
import read_config as cfg
import db_lookup
from loglib import loglib


''' <snipped this class, Check_Redis_GangliaRest out of my check_redis module > '''


class Check_Redis_GangliaRest(object):
    ''' This class is responsible for handling our Ganglia RRD locations '''

    rootDir = '/var/lib/ganglia/rrds/'
    logfile = '/var/log/GangliaRest.log'

    def __init__(self,hostname):
        ''' We are looking for hostnames in our rrd tree '''

        self.hostname = hostname


    def redis_lookup(self):

        print("Looking up %s" % self.hostname)

        r = redis.Redis(
	    host = 'localhost',
  	    port = 6379,
            db = 1,
            password = '############')

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
			    #loglib(self.logfile,"INFO: Host being set as %s" % self.hostname)
		            self.location = os.path.abspath(dirName+'/'+self.hostname)

			    ''' Now we need to add to our Redis cache with a TTL of one day
				to account for transitory systems like VM's that spin down '''
			    try:
			        #print("Setting key for %s and val %s" % (self.hostname,self.location))
			        r.setex(self.hostname, self.location, 86400)
			        return(self.location)

	                    except:
				loglib(self.logfile,"ERROR: Error writing to Redis under Check_Redis_GangliaRest:redis_lookup")
			        exit(1)

		        else:
			    #loglib(self.logfile,"ERROR: Unable to find requested host in rrdtree under Check_Redis_GangliaRest:redis_lookup")
			    continue  # we don't want to log every miss


            except:
	        loglib(self.logfile,"ERROR: Unable to find or write to Redis requested host in rrdtree under Check_Redis_GangliaRest:redis_lookup")
