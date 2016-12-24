########################################
#
# This file part of the gangliarest package
#
# https://pypi.python.org/pypi/gangliarest
#
# https://github.com/dcarrollno/Ganglia-Modules/wiki/GangliaRest-API:-Part-I
#
# Dave Carroll - davecarrollno@gmail.com
#
########################################

import requests
import json
from loglib import loglib
import read_config as cfg

cfg.readConfig()


class CheckforUpdates(object):
    ''' Class to check pypi for new updates to gangliarest '''

    repo = 'https://pypi.python.org/pypi/{package}/json'


    def __init__(self,pkg):
        ''' pkg is the pkg we want to check '''

        self.pkg = pkg


    def updateCheck(self):
        ''' Check for update at pypi'''


        try:
            from packaging.version import parse

        except ImportError:
            print("Error importing packaging")
            from pip._vendor.packaging.version import parse


        req = requests.get(self.repo.format(package=self.pkg))

        avail_version = parse('0')
        if req.status_code == requests.codes.ok:
            j = json.loads(req.text.encode(req.encoding))
            if 'releases' in j:
                releases = j['releases']
                for release in releases:
                    ver = parse(release)
                    if not ver.is_prerelease:
                        avail_version = max(avail_version, ver)

        return str(avail_version)


    
    def installedCheck(self):
        ''' Method to check currently installed python
            package version '''

        import pip

        for dist in pip.get_installed_distributions():        
            #print(dist.project_name,dist.version)
            if dist.project_name == self.pkg:
                curr_pkg = dist.project_name
                curr_ver = dist.version

        return str(curr_ver)



    def compareCheck(self):
        ''' This method compares what is available to
            what we have installed as known by pip '''
            

        try:
            avail_version = self.updateCheck()
            installed_version = self.installedCheck() 

            #print("The installed version is: %s" % installed_version)
            #print("The available version is: %s" % avail_version)
            loglib(cfg.logfile,"Notice: The installed version of %s is %s" % (self.pkg,installed_version))

            if installed_version != avail_version:
                #print("New version available")
                loglib(cfg.logfile,"NOTICE: gangliarest-%s is available. Run 'pip install gangliarest --upgrade' to get the latest." % avail_version)
                update_msg = True
                return(avail_version,installed_version,update_msg)

            else:
                update_msg = False
                return(avail_version,installed_version,update_msg)

        except:
            # Software update check failed - not fatal
            pass



if __name__ == '__main__':
    
    # Debug
    myHandle = CheckforUpdates('gangliarest')
    inst = myHandle.compareCheck()


