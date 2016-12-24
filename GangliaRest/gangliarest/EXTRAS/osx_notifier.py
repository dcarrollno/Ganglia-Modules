#!/usr/bin/env python

''' Example program to check load via GangliaRest
    and if meets threashold, throw an osx notification alert.
    Tested and working under Sierra 10.12

    see: https://pypi.python.org/pypi/gangliarest
         https://github.com/dcarrollno/Ganglia-Modules/wiki/GangliaRest-API:-Part-V

    Dave Carroll - davecarrollno@gmail.com  '''



from Foundation import NSUserNotification
from Foundation import NSUserNotificationCenter
from Foundation import NSUserNotificationDefaultSoundName
from optparse import OptionParser
from subprocess import Popen,PIPE,STDOUT


def poller(nodeToCheck,metric,threshold):
    ''' We can use the included curl for osx or go get wget and use that.
        Both examples are included here. Uncomment the one you wish to use.
        Change the alert wording as needed '''

    #cmd='/usr/local/bin/wget -qO- http://netwatch.nanigans.com:8653/node/'+nodeToCheck+'/get_metric/'+metric
    cmd='/usr/bin/curl -S -s http://netwatch.nanigans.com:8653/node/'+nodeToCheck+'/get_metric/'+metric
    alert_txt = 'Load Alert'

    try:
        p1 = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        output1 = p1.stdout.read()
    except:
        print("Error: Unable to gather metric for node %s" % nodeToCheck)


    if output1 > threshold:
        msg_prefix=('The current load for %s is ' % nodeToCheck)
        msg = msg_prefix+output1
        alert(alert_txt,msg)


def alert(title,message):
    ''' Send the desktop notification. '''

    notification = NSUserNotification.alloc().init()
    notification.setTitle_(title)
    notification.setInformativeText_(message)
    notification.setSoundName_(NSUserNotificationDefaultSoundName)

    center = NSUserNotificationCenter.defaultUserNotificationCenter()
    center.deliverNotification_(notification)



if __name__ == '__main__':

    ''' Here we set nodes we want to check.  As a simple example
        we can loop through defined nodes and metrics to check.
        One could create a config file to hold this in a more
        friendly format.

    '''

    toMonitor = {
               'web1' : [ { 'load_one'  : '1.0' },
                          { 'load_five' : '1.0' }
                         ],
               'app1' : [ { 'load_one'  : '1.0' },
                          { 'load_five' : '1.0' }
                         ]
               }

    for node,metric_list in toMonitor.items():
        for each in metric_list:
            for metric,threshold in each.items():
	        poller(node,metric,threshold)
