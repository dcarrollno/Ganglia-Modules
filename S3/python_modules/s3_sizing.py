#!/usr/bin/env python

''' Trend the sizing of our S3 buckets under specific accounts.
    This requires setting root aws creds

    This progam will poll multiple regions for S3 metrics.  You should
    add the following to /etc/sysconfig/gmond:

    # Gmond defaults
    export AWS_ACCESS_KEY_ID=<your key here>
    export AWS_SECRET_ACCESS_KEY=<your key here>
    export AWS_DEFAULT_REGION=us-west-2
    export AWS_DEFAULT_PROFILE=IT

    Then in /etc/init.d/gmond, source it with
    ./etc/sysconfig/gmond
    '''

import os
import datetime
import time
import boto3


descriptors = []
last_time = 0
metrics = {}
initial_metrics = {}
cache = 60


class S3Sizes(object):

    buckets = {}

    def __init__(self, session):

        # // Set AWS ENV vars in /etc/sysconfig/gmond

        self.session = session
        boto3.setup_default_session(profile_name=self.session)
        self.cw = boto3.client('cloudwatch')
        self.s3client = boto3.client('s3')
        self.now = datetime.datetime.now()

    def s3Sizes(self):
        # Get a list of all buckets
        try:
            self.allbuckets = self.s3client.list_buckets()
        except Exception,e:
            print("Error, exception thrown was %s" % e)


        # Iterate through each bucket
        for bucket in self.allbuckets['Buckets']:
        # For each bucket item, look up the cooresponding metrics from CloudWatch
            response = self.cw.get_metric_statistics(Namespace='AWS/S3',
                                        MetricName='BucketSizeBytes',
                                        Dimensions=[
                                            {'Name': 'BucketName', 'Value': bucket['Name']},
                                            {'Name': 'StorageType', 'Value': 'StandardStorage'}
                                        ],
                                        Statistics=['Average'],
                                        Period=3600,
                                        StartTime=(self.now-datetime.timedelta(days=2)).isoformat(),
                                        EndTime=self.now.isoformat()
                                        )
            for item in response["Datapoints"]:
                self.buckets[bucket["Name"]]=item["Average"]


def get_values(name):
    ''' wrapper to run values '''

    global last_time, metrics

    regions = []

    name = name.replace('aws_S3_','')

    if time.time() - last_time > cache:
        itwest=S3Sizes("IT-west")
        iteast=S3Sizes("IT-east")
        regions.extend([itwest,iteast])

        for region in regions:
            inst = region.s3Sizes()
            metrics.update(S3Sizes.buckets)

        last_time = time.time()

    try:
        for k,v in metrics.items():
            if name == k:
                if isinstance(v, float):
                    return float(v)
                if isinstance(v, int):
                    return int(v)
    except Exception,e:
        print("Error under get_values. Exception thrown was %s" %  e)


def metric_init(params):

    global descriptors,metric_group,aws_profile,initial_metrics,last_time

    regions = []

    try:
        metric_group = params.pop('metric_group')
        aws_profile = params.pop('aws_profile')
    except:
        print("WARN: Incorrect parameters in nan_s3sizing")

    # Dynamically build descriptors based upon first run
    time_max = 60

    # Run once to prime dynamic descriptors
    itwest = S3Sizes("IT-west")
    iteast = S3Sizes("IT-east")
    regions.extend([itwest,iteast])

    for region in regions:
        inst = region.s3Sizes()
        initial_metrics.update(S3Sizes.buckets)

    for k,v in initial_metrics.items():
        d = {
            'name': 'aws_S3_'+k,
            'call_back': get_values,
            'time_max': time_max,
            'value_type': 'float',
            'units': 'Bytes',
            'format': '%.4f',
            'slope': 'both',
            'description': k,
            'dmax': 3600,
            'groups': metric_group
         }

        #print d
        # Apply metric customizations from descriptions
        #d.update(descriptions[label])
        if d not in descriptors:
            descriptors.append(d)

    #last_time = time.time()


    return descriptors


def metric_cleanup():
    pass


if __name__ == '__main__':

    params = {}
    params['name']='nan_s3sizing'
    params['metric_group']='AWS_S3'
    params['aws_profile']='IT'
    metric_init(params)

    for d in descriptors:
        v = d['call_back'](d['name'])
        #print' %s: %s %s [%s]' % (d['name'], d['format'] % v, d['units'], d['description'])
        print 'value for %s is %s' % (d['name'], v)
