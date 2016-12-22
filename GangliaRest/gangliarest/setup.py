from setuptools import setup, find_packages
from setuptools.command.install import install
from codecs import open
from os import path
import os
import sys

here = path.abspath(path.dirname(__file__))

class PostInstall(install):
    """Customized setuptools install command - prints a friendly greeting."""

    def run(self):
        print "Running custom install script"
        ver = sys.version_info[:2]
        if ver == (2, 6):
            version = '2.6'
        if ver == (2, 7):
            version = '2.7'
        pkg='/usr/lib/python'+version+'/site-packages/gangliarest' 
 
        mode = 0751
        src = '/usr/lib/python'+version+'/site-packages/gangliarest/gangliaRest.py'
        dst = '/usr/local/sbin/GangliaRest'
        install.run(self)
        os.symlink(src,dst) 
        for dirpath, dirnames, filenames in os.walk(pkg):
            for filename in filenames:
                path = os.path.join(dirpath, filename)
                os.chmod(path, 0751)
        


setup(
    name='gangliarest',
    version='0.1.4',
    author="Dave Carroll",
    author_email="davecarrollno@gmail.com",
    description=("A ReSTFUL frontend to Ganglia exposing metrics via HTTP."),
    keywords = "Ganglia API REST Web frontend metrics", 
    url="https://github.com/dcarrollno/Ganglia-Modules/tree/master/GangliaRest",
    packages=['gangliarest'],
    long_description=open('README.txt').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Monitoring',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7', 
        'Operating System :: POSIX :: Linux',
    ],
    install_requires=["gns3-netifaces","web.py","redis"],
    include_package_data=True,
    data_files=[
        ('/etc/', ['etc/GangliaRest.cfg']),
        ('/etc/init.d/', ['etc/GangliaRest']),
    ],
    cmdclass={'install': PostInstall},
    
)
