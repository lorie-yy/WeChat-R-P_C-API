#
# Regular cron jobs for the bdlicense package
#
0 4	* * *	root	[ -x /usr/bin/bdlicense_maintenance ] && /usr/bin/bdlicense_maintenance
