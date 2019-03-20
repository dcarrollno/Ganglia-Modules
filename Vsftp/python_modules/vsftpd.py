#!/usr/bin/python

import os
import time

''' Small Ganglia module to watch vsftp logs on our
    ftp server, collecting stats on logins, failed logins
    and downloads.

'''

__author__ = "Dave Carroll"


LOG = '/var/log/vsftpd.log'
curr_time=time.time()             # current time
last_time=0                       # last update
cache=5                	          # metric cache time
METRICS = {}


def check_log(name):
    global curr_time,last_time,cache

    # Set counters
    log_fails = 0
    xfer_fails = 0
    logins = 0
    uploads = 0
    downloads = 0

    if (time.time() - last_time > cache):
        #print "Running - no cache"
        METRICS.clear()		# only clear if cache expired

        with open(LOG,'rb') as f:
            lines = f.readlines()

        for line in lines:
            if "FAIL LOGIN" in line:
                log_fails += 1
                METRICS['ftp_login_fails']=log_fails

            if "FAIL DOWNLOAD" in line:
                xfer_fails += 1
                METRICS['ftp_failed_downloads']=xfer_fails

            if "OK LOGIN: Client" in line:
                logins += 1
                METRICS['ftp_logins']=logins

            if "OK UPLOAD: Client" in line:
                uploads += 1
                METRICS['ftp_uploads']=uploads

            if "OK DOWNLOAD: Client" in line:
                downloads += 1
                METRICS['ftp_downloads']=downloads

        curr_time=time.time()
        last_time=time.time()

        total = count_results(name)
        return int(total)

    else:
        total = count_results(name)
        return int(total)



def count_results(name):
    global METRICS
    for k,v in METRICS.items():
        if name == k:
            return int(v)


def metric_init(params):
    global descriptors, LOGFILE

    LOGFILE = params.get('log_file')

    descriptors = [{'name': 'ftp_logins',
        'call_back': check_log,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Logins',
        'slope': 'both',
        'format': '%u',
        'description': 'Number of FTP Logins during the day.',
        'groups': 'FTP',
        },
        {'name': 'ftp_login_fails',
        'call_back': check_log,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Failed Logins',
        'slope': 'both',
        'format': '%u',
        'description': 'Number of failed login attempts under FTP over the day',
        'groups': 'FTP',
        },
        {'name': 'ftp_downloads',
        'call_back': check_log,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Downloads',
        'slope': 'both',
        'format': '%u',
        'description': 'Number of FTP downloads over the day',
        'groups': 'FTP',
        },
        {'name': 'ftp_failed_downloads',
        'call_back': check_log,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Failed Downloads',
        'slope': 'both',
        'format': '%u',
        'description': 'Number of Failed FTP downloads over the day',
        'groups': 'FTP',
        },
        {'name': 'ftp_uploads',
        'call_back': check_log,
        'time_max': 60,
        'value_type': 'uint',
        'units': 'Uploads',
        'slope': 'both',
        'format': '%u',
        'description': 'Number of FTP uploads over the day',
        'groups': 'FTP',
        }]

    return descriptors

def metric_cleanup():
        '''Clean up the metric module.'''
        pass

if __name__ == '__main__':
    #metric_init({})
    params=0
    metric_init ({
      'stats_file':'/tmp/queue.depth'
    })
    for d in descriptors:
        v = d['call_back'](d['name'])
        print 'value for %s is %u' % (d['name'],  v)
