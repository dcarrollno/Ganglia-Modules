from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

setup(
    name='gangliarest',
    version='0.1',
    author="Dave Carroll",
    author_email="davecarrollno@gmail.com",
    description=("A ReSTFUL frontend to Ganglia exposing metrics via HTTP."),
    keywords = "Ganglia API REST", 
    url="https://github.com/dcarrollno/Ganglia-Modules/tree/master/GangliaRest",
    packages=['gangliarest'],
    long_description=open('README.txt').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: System Administrators',
        'Topic :: System Monitoring :: Monitoring',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7', 
        'Operating System :: POSIX :: Linux',
    ],
    install_requires=["gns3-netifaces","web.py>=0.38","redis"],
    include_package_data=True,
    data_files=[
        ('/etc/', ['etc/GangliaRest.cfg']),
        ('/etc/init.d/', ['etc/GangliaRest']),
        ('/usr/local/sbin', ['sbin/GangliaRest']),
    ],
)
