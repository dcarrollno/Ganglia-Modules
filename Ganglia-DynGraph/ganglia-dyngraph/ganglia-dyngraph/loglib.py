########################################
#
# This file part of the ganglia-dyngraph package
#
# https://pypi.python.org/pypi/ganglia-dyngraph
#
# https://github.com/dcarrollno/Ganglia-Modules/wiki/Overview:-Ganglia-Dynamic-Metrics%3F
#
# Dave Carroll - davecarrollno@gmail.com
#
########################################


def loglib(logfile,message):
    ''' Generic logging function for Ganglia metric modules.


    In your program, define a logfile like so:
        logfile = '/var/log/test.log'
        In your program call this function like so:
        loglib(logfile,'INFO:  Starting test app')
    You can also silence by adding to your program:
        logging.disable(logging.DEBUG)
    '''

    import logging
    logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s Thread-%(thread)d - %(message)s", filename=logfile)
    logging.debug(message)
    return()
