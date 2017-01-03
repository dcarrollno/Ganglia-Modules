GangliaRest
===========

|PyPI version|

Overview
--------

HTTP API frontend for Ganglia Web - Expose your Ganglia metrics via HTTP.

GangliaRest is a 100% open-source package layered on top of your Ganglia Web host.
We use it to expose metrics collected from nodes to our Nagios monitoring station 
or from various scripts for whatever purpose.  I am aware of the project to expose
Ganglia metrics to Nagios but that didn't fit our needs, especially given we have
such a large Ganglia implementation. I chose instead to write this front end so we 
could pick our metrics and develop Nagios monitoring around those.

Our Nagios server simply makes properly formatted API requests to GangliaRest and acts
upon the result. I initially returned formatted json responses and had Nagios use a 
custom API client but over time we decided keeping things straightforward was best.

I use Redis to cache the locations for nodes in the RRDtree so metric lookups
are more efficient. (we have hundreds of nodes we trend) A configurable threaded
Indexer will prime and keep the Redis cache healthy.

With GangliaRest, one can expose metrics without reading the XML stream, create
on-demand monitoring integrate something like Nagios, or create cluster manager 
software that uses Ganglia metrics for various purposes. 


Core Requirements
-----------------
- Python 2.6 or Python 2.7 (as tested)
- Python webpy
- Python Redis client
- gns3_netifaces-0.10.4.1
- Redis Server > 2.8 (available from Atomic CentOS) 
- Ganglia Gmetad Web hosting your rrdtree


Installation
------------
This package is currently running on CentOS 6.8 with Python 2.6. You may need to groupinstall
the "Development tools" as well as the python-devel package.  Once you are ready to install
GangliaRest you can run pip install gangliarest as root. 

The module will be installed into /usr/lib/python2.x/site-packages/gangliarest. 
The configuration file will be installed as /etc/GangliaRest.cfg
The init script will be installed as /etc/init.d/GangliaRest

You will want to adjust /etc/init.d/GangliaRest if you run Redis on a different port
You will want to chkconfig add GangliaRest to start at run level 3.
You will want to adjust your iptables accordingly.
You will want to visit /etc/GangliaRest.cfg and adjust your config file.

You will want to install a local Redis server. You can add the atomic repo
by running: wget -O - http://www.atomicorp.com/installers/atomic |sh
followed by: yum install redis which should net you a version better than 2.8.

Edit your /etc/redis.conf file and set the requirepass to a password you prefer.

Run service redis start and chkconfig that accordingly.   

Run service GangliaRest start when you are ready.  A pid file will be dropped in as
/var/run/GangliaRest.pid. You will receive a warning if a valid Redis pidfile was not
detected in /var/run/redis/redis.pid. If you run multiple Redis instances, adjust 
accordingly.  

GangliaRest should now be listening on port 8653 or whatever you selected in 
/etc/GangliaRest.cfg.   

Upgrading
---------
GangliaRest will check on startup and once per day for any available upgrades.
These may include important bug fixes or enhancements so please consider upgrading
when you see a message in the logfile informing you of an upgrade. 

To upgrade run the following commands:
system# service GangliaRest stop
system# pip install gangliarest --upgrade 

The upgrader will copy your /etc/GangliaRest.cfg file as GangliaRest.cfg.save so you 
will not lose your changes. You can then merge those changes into the newly created 
GangliaRest.cfg file.


Usage
-----
Once running, you can send HTTP requests against GangliaRest using a URL formatted
as: http://<your_gmeta_web_host>:8653/node/<one of your nodes>/get_metric/<metric>

For example, if my Gmeta Web Host is named gweb.example.com and I wanted to view the 
load_one metric for my node named web1.example.com I would format my request as:
http://gweb.example.com:8653/node/web1.example.com/get_metric/load_one 

GangliaRest will search your RRDtree for the node web1, locate the metric rrd for load_one,
and return the current metric value. For each request, the location on the filesystem for
that node will be cached in Redis for faster future lookups to save filesystem scanning. 

Indexer
-------
The indexer will run scanning your RRDtree for the purpose of caching filesystem locations
on a configurable basis. If it has not been run, it will prime the cache by running at start up 
and you will see logged entries such as:

2016-12-22 10:36:32,999 - root - DEBUG Thread-140068063868672 - INFO: INDEXER: Running Indexer for first time
2016-12-22 10:36:33,000 - root - DEBUG Thread-140068063868672 - INFO: INDEXER starting scheduled operations...
2016-12-22 10:36:33,017 - root - DEBUG Thread-140068063868672 - INFO: INDEXER completed run...Added 14 entries to Redis

The above indicates the indexer ran and added 14 nodes to the cache.  


Redis
-----
Once you have redis installed and have set the password both in /etc/GangliaRest and in
/etc/redis.conf, you can connect to Redis to examine the cached nodes that were indexed. 
To do this:

root@gweb# redis-cli -a <your_password>
127.0.0.1:6379> select 1    # select DB instance 1 
OK
127.0.0.1:6379> keys *      # list all nodes by key
1) "web1"
2) "app1.example.com"


GangliaRest.cfg - Configuration
-------------------------------
Located in /etc, the GangliaRest.cfg file offers some options to control the behavior of
GangliaRest to suit your needs. The following options are included:

- restHost: This option defines where GangliaRest will listen. You can leave the default
of 0.0.0.0 to listen on all interfaces, or specify perhaps just your internal IP.

- restPort: This option defines the port GangliaRest will listen on. The default is 8653. 
Remember to adjust your iptables accordingly.  

- logfile: This defines where you want GangliaRest activity logged to. There are many
useful log messages so it is recommended you review this. 

- logLevel: This is a future option on the TODO list to control the level of logging.

- statsFile: This option controls where you want stats printed out to. I send mine to
/tmp/gangliaRest.state and have a Ganglia Python DSO that reads those metrics, graphing
the number of requests/responses and errors per minute. 

- domain: You must adjust this to your domain. GangliaRest uses the defined domain to
process information it needs. Many times nodes may be created by Ganglia Gmetad using
either a hostname alone or fqdn, depending upon your setup. In cases where both are used
GangliaRest needs to search the filesystem for node matches to service API requests. 

- rrdDir: Set this to where your rrd files are. The default is /var/lib/ganglia/rrds.

- redisHost: This defines where your Redis server is. Localhost is the default.

- redisPort: This defines the port your Redis server is listening on. 6379 is the default.

- redisDb: This defines a DB instance. Some folks run multiple DBs per Redis instance while 
others run multiple Redis servers with one db each. 

- redisTtl: This option controls the expiration in Redis of your node locations. The recommended
setting is one day or 86400. This means nodes will be indexed by the indexer and held in cache
for one day. This is probably good for most orgs and allows expiring out nodes no longer in use
after one day.

- redisAuth: This defines your Redis requireauth option as defined in /etc/redis.conf. 

- indexFreq: This option controls how often in seconds the GangliaRest Indexer will run. The Indexer
scans your RRDtree and catalogs node locations into Redis for fast lookups. The default is 3600 
seconds, or hourly. If you do not add new nodes to Ganglia often, you can set this higher but one
hour is recommended. If you add dynamic nodes often, you migth even set this to 300 seconds to 
be more aggressive. 

Logging
-------
GangliaRest will log output on certain operations to /var/log/GangliaRest.log. You should add this
to your logrotate jobs accordingly. The log will show API requests, responses and errors. These are
incremented by a counter and sent to a file defined in GangliaRest.cfg in a simple format. From there,
you can create a Ganglia DSO or script job to pick those stats up and have them graphed. This will show
how busy your GangliaRest server is. You can also parse the logfile for information if that meets 
your needs better.

The logfile will show errors and failures. When a request is received for a non-existent node or 
the API request is misconfigured, a simple NOT FOUND error will be displayed (easy for scripts 
or Nagios checks to parse) and an incident will be logged. 

The Indexer will also log its operations. The indexer checks every 60 seconds to see whether
it needs to run an indexing operation, as configured by your indexFreq setting. The Indexer will
log whether it needs to run or go back to sleep. 

Upon start of GangliaRest a software update check is performed and notiifcation is logged if there
is a more recent update available. One may upgrade using: pip install gangliarest --upgrade. A 
logged message during the check appears as:

2016-12-22 10:36:32,996 - root - DEBUG Thread-140068300097280 - Notice: The installed version of gangliarest is 0.1.6

When an update has been detected at Pypi, a logged message will appear as:

2016-12-22 10:33:00,582 - root - DEBUG Thread-140338108651264 - NOTICE: gangliarest-0.18 is available. Run 'pip install gangliarest --upgrade' to get the latest.





