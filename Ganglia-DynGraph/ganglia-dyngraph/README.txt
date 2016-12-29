Ganglia-DynGraph
================

Overview
--------


Dynamic graph sweeper for Ganglia. 

Ganglia is a great trending platform but like any project it is fun to make modifications 
to suit the needs of any team or org. I had one such need a couple of years ago and that was 
to have sets of dynamic graphs that were more "top like" and would show me short-term metric
results rather than long term trending. For example, I had farms of API servers that handled
hundreds of millions of requests per day and I wanted to know from each API server which 
of our clients were the top 5 users of those API endpoints. In this example, I needed to tally
requests, extract the top 5 requests by client id and graph them. Easy enough, but what if I 
wanted to know the top 5 requests every 60 seconds and those top 5 clients changed by volume? 
I needed a way to record the top 5 metrics per API node and 60 seconds later if any of those 
changed position, tear down the metric graph, re-publish it, and expire out the metric files 
to keep the system from filling up.  Another example where I used this was to show short-term
swapping metrics. I wanted to see what was swapped out on any given system at any given time.
This can be highly dynamic in nature. 

Ganglia-DynGraph is a daemon started from rc script. It reads a configurable file where you
set options and acts upon those accordingly to produce dynamic metrics. Behind the scenes it 
sweeps your RRDtree for configured metrics and expires (deletes) them off your system at a 
configurable expiration period. It also searches for configured metrics where you want the top
n results, gathers last metric value information, ranks that and creates Ganglia report graphs
in .json format under your Ganglia Gweb tree. 

I have removed some custom functions and classes that are unique to my work environment but
have reworked the core modules into this package so others can use them or improve upon them.


Core Requirements:
------------------
- Python 2.6 or Python 2.7 (as tested)
- Ganglia Gweb - where you store your rrds and expose them via Ganglia web

Installation
------------
This package can be easily installed by using 'pip install ganglia-dyngraph' and upgraded
using pip install --upgrade ganglia-dyngraph accordingly.  I use CentOS 6.x as a standard
so the included init file is specific to that and will be installed into /etc/init.d. Files
installed:

- /etc/init.d/DynamicGraph - the init script to start and background DynamicGraph. 
- /etc/DynamicGraph.cfg - the configuration file you must configure for your needs
- /var/run/DynamicGraph.pid - pid file 
- /var/log/DynamicGraph.log - operations logging with helpful info

Usage
-----
After installation, edit /etc/DynamicGraph.cfg.  That file has some instructions included. You
will want to verify your rrd tree and Ganglia graphs locations are set correctly.  You will want
to set various global options and finally configure any metrics you wish to have dynamically managed.

Once done, as root, chkconfig --level 3 DynamicGraph on and run service DynamicGraph start to fire 
up DynamicGraph.  You will find that in your ps listing and can check logging output in 
/var/log/DynamicGraph.log for any issues. You may also want to include DynamicGraph.log in any
logrotate configuration you manage. 

DynamicGraph.cfg
----------------
Currently the following configuration options exist:

- GraphDir - This is where you have Ganglia configured to hold your metric .json graph files. This 
  is also where DynamicGraph will produce dynamically created reports. You will want to edit your 
  hosts or cluster configuration preferences typically under /var/lib/ganglia-web/conf to include 
  these as needed. 

- RRDIDR - This is the location of your rrd files. This is typically /var/lib/ganglia/rrds

- logfile - You may specifiy a custom location for your DynamicGraph log file. 

- runTime - This numeric option controls how often the dynamic metric sweeper will run, purging any
  metrics that have expired and creating new dynamic graphs. The default is 60 seconds. 

- expireTime - This is the time in seconds we consider our metrics stale. For example, if you are 
  trending swap metrics per process, set this to 60 and when then sweeper runs it will remove these
  metrics that are older than 60 seconds. 

- purged_metric_count - We trend how many metrics are expired out and purged and write those to state
  files. You can then create a Ganglia module that reads these and reports them accordingly to watch
  for abnormal purge numbers.  

- purged_error_count - Like the purged metric count, this trends any errors incurred in purging metrics.
  Metrics may error out for a number of reasons. 

- numMetrics - This option sets the number of metrics to sort and rank. I am typically interested in the 
  top 5 of any metric. For example, only graph the top 5 processes swapped out by a specific system or
  the top 5 requests to a web server or api server etc.. 

- Cluster Section - This section is where you configure clusters and metrics to work with. Each section
  is titled with a [Cluster_<name of your Ganglia cluster>] section. So if you had a cluster named
  "WebServers" you would configure this section header as [Cluster_WebServers].  DynamicGraph will 
  pick this up and search for the WebServer cluster in your rrd tree. 

  The next line is prefixed "metrics=" and that prefix is required. You then enter a comma-separated
  list of metrics you wish to include as dynamic.  You do not include the .rrd suffix. For example, 
  say I created a Ganglia metric module that trended processes currently swapped out and that metric
  was named swapping_ such that if I had processes mysql-server and data-daemon currently swapping, it
  would produce swapping_mysql-server.rrd and swapping_data-daemon.rrd in my rrdtree. I would configure 
  this section then as metric=swapping_ since "swapping_" is unique. DynamicGraph will find the metrics
  swapping_* under your node and cluster as configured.  


Logging
-------
Logging is sent to /var/log/DynamicGraph.log by default. There you will find interesting status 
messages such as:

2016-12-22 17:21:45,679 - root - DEBUG Thread-140212695631616 - INFO: Metric /var/lib/ganglia/rrds/db_cluster/db1/swapping_mysql-server.rrd successfully purged

2016-12-22 17:21:45,679 - root - DEBUG Thread-140212695631616 - INFO: Metric /var/lib/ganglia/rrds/db_cluster/__SummaryInfo__/swapping_mysql-server.rrd successfully purged

which show the metric swapping_mysql-server was purged successfully from your system for the node db1. 


Additional
----------
As I mentioned earlier, I use dynamic metrics for trending the current top 5 users of a very busy API
farm, every 60 seconds across tens and tens of nodes and farms, globally. With this I am able to quickly spot
who the top consumers of our resources are at any given time. How I differentiate these clients is by a id
that a Ganglia module I wrote obtains on each API node. The id is unique and is how I rank the top clients. 

To find the customer name that I include in the graphs vs. graphing by an id, I do a lookup in either sqlite
or in Redis where I maintain a mapping of id to customer name. This allows me to show customer names right in 
my dynamic graphs.  To accomplish this, I utilize several other modules and classes to handle the lookups by
cluster type. You can really come up with many possibilities and customize this as needed. 





