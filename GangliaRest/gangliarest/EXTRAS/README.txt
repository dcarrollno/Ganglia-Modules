OSX Desktop notifier example for GangliaRest

https://github.com/dcarrollno/Ganglia-Modules/wiki/Ganglia-Rest-API:-Part-V---Notification-Fun


Copy com.gangliarest.plist to: ~/Library/LaunchAgents
Edit the directory path to point to your own home directory.


Copy osx_notifier.py to your home directory.
Run chmod 751 osx_notifier.py 
Edit notifier.py to include nodes, metrics and threasholds you want to monitor.


To enable:
launchctl load com.gangliarest.plist

To disable:
launchctl unload com.gangliarest.plist
