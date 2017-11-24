#!/usr/bin/python
#coding:utf-8

import os
import re
import sys
import subprocess
import commands

def get_process_id(pro_name): 
    cmd = "ps -ef | grep %s | grep -v '$0' | grep -v 'grep' | grep -v 'portalbd'| awk '{print $2}'" % (pro_name)
    #aa=subprocess.Popen(cmd, shell=True)
    aa = commands.getoutput(cmd) 
    return str(aa).split()
   
def kill_process(pid):
    cmd = "kill -9 %s" % (str(pid))
    os.system(cmd)

def restart_process():
    base_path = r'/home/Portal'
    portalbd_path = os.path.join(base_path, r'bdlicense/bdlicense')

    services=['/home/Portal/bdlicense/bdlicense/uwsgi','wechattimedtask.py']
    for name in services:
        pids = get_process_id(name)
        for pid in pids:
            if int(pid) > 100:
                kill_process(pid)

    uwsgicmd = 'uwsgi --ini ' + os.path.join(portalbd_path, 'uwsgi.ini')
    rst = os.system(uwsgicmd)
    if str(rst) == '0':
        print "[INFO]: restart uwsgi successfull..."
    else:
        print "[ERROR]: restart uwsgi failure ..."


    full_service_command = {}


    wechattimed_task_path = os.path.join(portalbd_path, 'wechatfans/wechattimedtask.py')
    if os.path.exists(wechattimed_task_path):
        cmd = 'nohup python ' + wechattimed_task_path + ' &'
        full_service_command['wechattimed_task_path'] = cmd

    for each_service in full_service_command.keys():
        p = subprocess.Popen(full_service_command[each_service], shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            
        if p.stderr is None:
            print "[INFO]: restart service %s successful..." % (each_service)
        else:
            print '[ERROR]: ', p.stderr

if __name__ == '__main__':
    if os.geteuid() != 0:
        print 'No authority, use sudo'
        sys.exit(1)

    restart_process()
