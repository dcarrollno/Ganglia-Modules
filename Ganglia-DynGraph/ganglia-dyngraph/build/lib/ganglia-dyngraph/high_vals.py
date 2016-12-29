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


def high_vals(numreturns,sorton,mydict):
    import operator

    ''' numreturns = number of results returned back to caller
        sorton = k or v. You can sort keys, or by values
        mydict = dict passed in to sort
        Call this subroutine like: graphs = high_vals(numMetrics,'val',graphs) '''

    if sorton == 'key':
        sortby = 0
    if sorton == 'val':
        sortby = 1

    sorted_mydict = sorted(mydict.items(), key=operator.itemgetter(sortby),reverse=True)
    #print("Printing sorted_mydict %s" % sorted_mydict)
    sorted_mytuple = sorted_mydict[0:numreturns] # list of tuples
    #print(new)
    mydict.clear()

    return(sorted_mytuple)
