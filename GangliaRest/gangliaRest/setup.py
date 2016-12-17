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
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.txt').read(),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: System Administrators',
        'Topic :: System :: Monitoring',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7', 
        'Operating System :: POSIX :: Linux',
    ],
    install_requires=["netifaces","web.py","redis"],
    include_package_data=True,
    data_files=[
        ('/etc/', ['etc/GangliaRest.cfg']),
        ('/etc/init.d/', ['etc/GangliaRest']),
        ('/usr/local/sbin', ['sbin/GangliaRest']),
    ],
)
