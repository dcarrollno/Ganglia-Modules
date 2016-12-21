GangliaRest

GangliaRest is a web frontend that is easy to install, easy to
configure and easy to run to front your Ganglia metrics tree. This
was created to expose metrics obtained using Ganglia to Nagios or 
other scripts or needs. 

After installing, chkconfig GangliaRest to start on run level 3. 
Edit the /etc/GangliaRest.cfg file to set your preferences. 
By default GangliaRest will listen on port 8653 and be sure this
is on an inside protected network and not blocked by iptables.

Make sure you chkconfig redis on as well.

Installing:
sudo pip install gangliarest

GangliaRest should be copied to /usr/local/sbin.
/etc/init.d/GangliaRest will be installed.
/etc/GangliaRest.cfg will be installed.

Requirements:
This package should install most things you need to get going 
but you may need to yum groupinstall "Development tools"

You will need web.py, which should be installed by this package.

You will need a local Redis server, and that version should
be > redis-3.6.0.1, available from the atomic repo for CentOS/RHEL.

You will need the Python redis package, which should be included here.


Usage:
service GangliaRest [start|stop|restart)
Monitor from /var/log/GangliaRest.log which will
expose requests, responses and any errors.  

To request a metric value you will pass a URL request as:
http://ganglia_web_server/node/web1/get_metric/load_one

The above request would request the load_one metric from
the node web1 on your Ganglia Gweb server.  The resulting
metric will be returned as either a float or uint.

Troubleshooting:
First, ensure GangliaRest is running by either running
service GangliaRest status or checking for a process. If
the process is gone but there is a stale pid file in 
/var/run/ named GangliaRest.pid, remove that, and restart.

Check /var/log/GangliaRest.log for any errors or warnings. 

Verify you have a redis server running. 
