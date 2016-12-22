#
#
# This file is part of ganglia_tools
#
# Dave Carroll - davecarrollno@gmail.com 
#


def loglib(logfile,message):
    ''' Generic logging function for Ganglia metric modules.


    In your program, define a logfile like so:
        logfile = '/var/log/nanigans/test.log'
        In your program call this function like so:
        loglib(logfile,'INFO:  Starting test app')

    You can also silence by adding to your program:
        logging.disable(logging.DEBUG)
    '''

    import logging
    import read_config as cfg

    #readConfig()   # todo: enable options in cfg to control logging

    #logLevel = 'logging.'+cfg.logLevel


    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s Thread-%(thread)d - %(message)s", filename=logfile)

    logging.info(message)

    return()
