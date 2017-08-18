# -*- coding:utf-8 -*-

import os
import md5
import bson
import datetime
import struct
import StringIO
import socket
import time
import fcntl
import uuid
from collections import OrderedDict
import urllib, httplib
import urllib2
import json
import ConfigParser



class LicenseLib():
    @staticmethod
    def getUsbKeyContent():
        print "Decoding USB licence file "
        is_license_valid= False
        is_usb_key_present =False
        is_license_file_latest =False


        try:
            statinfo = os.stat("/etc/keyinfo/content")
        except Exception,e:
            print e
            usbFileContent={
            "max_ap_allowed": 512,
            "max_ac_allowed": 128,
            "max_user_allowed":10000,
            "license_expire_time": "2018-10-01",
            "license_valid_mask": "",
            "license_key": "",
            "license_feature_string": "",
            "license_generate_time": "",
            "usb_key_hardwareId":"",
            "is_License_valid": False,
            "is_usb_key_present": False,
            "is_license_file_latest": False,
            "license_file_lastUpdateTime" : 0
            }
            return usbFileContent


        fileLastModifyTime = statinfo.st_ctime

        #get current time
        currentTime = time.time()

        if (currentTime - fileLastModifyTime) <1800:
            is_usb_key_present = True
        else:
            print "USB key file is expired, please insert the USB key"

        f = open("/etc/keyinfo/content", "rb")

        try:
            fileContent = f.read()

            #read the hardwareId first
            hardwareId = fileContent[0:16]
            print hardwareId

            #read timestamp
            timestampInFile = fileContent[17:27]
            print timestampInFile

            if (currentTime - int(timestampInFile) )<1800:
                is_license_file_latest =True
            else:
                print "time stamp in file is expired, please insert USB key to refresh"

            #read bson data
            bsonData = fileContent[27:]

            bsonString = bson.BSON(bsonData)
            decodeString = bson.BSON.decode(bsonString)
            print decodeString

            Max_AP_Allowed = decodeString["a"]
            #print Max_AP_Allowed

            Max_AC_Allowed = decodeString["b"]
            #print Max_AC_Allowed

            Max_User_Allowed = decodeString["c"]
            #print Max_User_Allowed

            License_Expire_Time = decodeString["d"]
           #print License_Expire_Time

            License_Valid_Mask =decodeString["e"]
            #print License_Valid_Mask

            License_Key =decodeString["f"]
            #print License_Key

            License_Feature_String=decodeString["g"]
            #print License_Feature_String

            featureDetail = License_Feature_String["featureDetail"]
            #print featureDetail

            Magic_Number="#0A0C"
            Separate_Key="#B1D1"
            License_Generate_Time= decodeString["h"]
            print License_Generate_Time

            sign = str(Max_AP_Allowed)+Magic_Number+str(Max_AP_Allowed) \
               +str(Max_User_Allowed)+Separate_Key+str(License_Expire_Time) \
               +str(License_Key)+str(License_Feature_String)+Separate_Key+hardwareId

            #print sign

            License_Valid_Mask_InFile = md5.new(sign).hexdigest()
            #print License_Valid_Mask_InFile

            is_license_valid = ( License_Valid_Mask_InFile == License_Valid_Mask)

            license_file_lastUpdateTime = timestampInFile


        except Exception, e:
            print e
            f.close()
            is_license_valid = False
            Max_AP_Allowed = 512
            Max_AC_Allowed = 128
            Max_User_Allowed = 10000
            License_Expire_Time = "2018-10-01"
            License_Valid_Mask =""
            License_Key ="default licence key"
            License_Feature_String=""
            License_Generate_Time=""
            license_file_lastUpdateTime = timestampInFile

        usbFileContent={
            "max_ap_allowed": Max_AP_Allowed,
            "max_ac_allowed": Max_AC_Allowed,
            "max_user_allowed":Max_User_Allowed,
            "license_expire_time": License_Expire_Time,
            "license_valid_mask": License_Valid_Mask,
            "license_key": License_Key,
            "license_feature_string": License_Feature_String,
            "license_generate_time": License_Generate_Time,
            "usb_key_hardwareId":hardwareId,
            "is_License_valid": is_license_valid,
            "is_usb_key_present": is_usb_key_present,
            "is_license_file_latest": is_license_file_latest,
            "license_file_lastUpdateTime" : timestampInFile
        }
        print usbFileContent

        return usbFileContent

    @staticmethod
    def writeUsbKeyContent(params):
        try:
            print "write USB licence file "

            # get the parameters first
            Max_AP_Allowed = params['max_ap_allowed']
            License_Key=     params['license_key']
            Max_AC_Allowed=  params['max_ac_allowed']
            Max_User_Allowed=   params['max_user_allowed']
            License_Expire_Time=   params['license_expire_time']
            HardwareId=  params['usb_key_hardwareId']
            write_path = params['write_path']

            #genenerate the bson string
            print "Generating USB licence file "

            MatchString = {
                "Max_AP_Allowed":"a",
                "Mac_AC_Allowed":"b",
                "Max_User_Allowed":"c",
                "License_Expire_Time":"d",
                "License_Valid_Mask":"e",
                "License_Key":"f",
                "License_Feature_String":"g",
                "License_Generate_Time":"h"
            }


            #License_Valid_Mask =""
            featureDetail = [{u"featureName":u"myFeature1", u"ParameterName":u"myParaName1", u"ParameterValue":u"myParaValue1"},]
            License_Feature_String={u"count":1,u"featureDetail":featureDetail}
            Magic_Number="#0A0C"
            Separate_Key="#B1D1"
            License_Generate_Time= str(datetime.datetime.now())

            sign = str(Max_AP_Allowed)+Magic_Number+str(Max_AP_Allowed)\
                +str(Max_User_Allowed)+Separate_Key+str(License_Expire_Time)\
                +str(License_Key)+str(License_Feature_String)+Separate_Key+str(HardwareId)

            print sign

            License_Valid_Mask = md5.new(sign).hexdigest()

            fileContent = {
                "a":Max_AP_Allowed,
                "b":Max_AC_Allowed,
                "c":Max_User_Allowed,
                "d":License_Expire_Time,
                "e":License_Valid_Mask,
                "f":License_Key,
                "g":License_Feature_String,
                "h":License_Generate_Time
            }

            bsonString = bson.BSON.encode(fileContent)
            print bsonString
            #print decodeString

            #generate the temp file
            tmpFileName ="licence"+HardwareId+str(time.time())+".o"

            f = open(tmpFileName, "w")
            f.write(bsonString)
            f.close()

            #write to usb
            #os.system("./license/dongle/usbwrite "+tmpFileName)
            os.system(write_path + ' ' + tmpFileName)

            #remove the tempFile
            print "removing tmp file"
            os.remove(tmpFileName)
            return True
        except Exception,e:
            print "write USB error:%s" % (e)
            return False

def get_mac_address():
    mac=uuid.UUID(int = uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e+2] for e in range(0,11,2)])

def CPUinfo():
    CPUinfo=OrderedDict()
    procinfo=OrderedDict()
    nprocs = 0
    with open('/proc/cpuinfo') as f:
        for line in f:
            if not line.strip():
                #end of one processor
                CPUinfo['proc%s' % nprocs]=procinfo
                nprocs = nprocs+1
                #Reset
                procinfo=OrderedDict()
            else:
                if len(line.split(':')) == 2:
                    procinfo[line.split(':')[0].strip()] = line.split(':')[1].strip()
                else:
                    procinfo[line.split(':')[0].strip()] = ''
    return CPUinfo['proc0']

def getLicenseInfo(ip, port, key_id, license_code):
    connection_str='http://%s:%s/adminbd/license_activate?'% (ip, port)
    connection_str = connection_str + 'key_id=' + key_id
    connection_str = connection_str + '&license_code=' + license_code

    f = urllib2.urlopen(connection_str)
    response = f.read()

    info_dict = {}
    info_dict = json.JSONDecoder().decode(response)

    return info_dict

def getLicenseUser(s_ip, s_port, user_name, passwd):
    user_url = r'http://%s:%s/adminbd/user_invalid?username=%s&password=%s' % (s_ip,s_port,user_name,passwd)
    f = urllib2.urlopen(user_url)
    response = f.read()

    info_dict = {}
    return json.JSONDecoder().decode(response)

def getLoginUser(BASE_DIR):
    rst = {'host':'', 'port':'', 'user':'','passwd':''}

    try:
        config_file = os.path.join(BASE_DIR, 'config')
        conf = ConfigParser.SafeConfigParser()
        conf.read(config_file)

        rst['host'] = conf.get("config", "host")
        rst['port'] = conf.get("config", "port")
        rst['user'] = conf.get("config", "user")
        rst['passwd'] = conf.get("config", "passwd")
    except:
        print "read config error"

    return rst

def setLoginUser(BASE_DIR, user, host,passwd='', port='8000'):
    try:
        config_file = os.path.join(BASE_DIR, 'config')
        conf = ConfigParser.SafeConfigParser()
        conf.read(config_file)

        conf.set("config", "host", host)
        conf.set("config", "port", port)
        conf.set("config", "user", user)
        conf.set("config", "passwd", passwd)
        conf.write(open(config_file,"w"))
    except:
        print "write config error"



if __name__ == '__main__':
    print "here I am"
