# -*- coding:utf-8 -*-

import os
import sys
import datetime
import json
import time

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
import commands
import ConfigParser

from Tkinter import *
import tkMessageBox

if os.geteuid() != 0:
    print 'No authority, use sudo'
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(BASE_DIR))
#
# from bdlslib import *

MSG={'1':u"请填写用户名和密码",
     '2':u"用户没有写权限",
     '3':u"用户名或密码错误",
     '4':u"请先登录"}

class LicenseManager:
    def __init__(self, master):
        self.key_id = ""
        self.license_code = ""
        self.max_ap = 0
        self.max_ac = 0
        self.max_user = 0
        self.expire_time = ""
        self.user_valid = False
        self.license_valid = False
        self.master = master

        login_info =  getLoginUser(os.path.join(BASE_DIR,'file'))
        self.login_user = login_info.get('user', '')
        self.login_passwd = login_info.get('passwd', '')
        self.license_server = login_info.get('host', '')
        self.user_passwd = ''
        self.port = login_info.get('port', '8000')

        self.RemoveContent()
        self.InitSystem()

        self.setframe = None
        self.frame2 = None
        self.frame3 = None

        self.frame = Frame(self.master)
        #self.frame.grid(row=0, column=0)
        self.frame.pack(fill="both",padx=200)
        self.titleLabel = Label(self.frame)
        self.titleLabel['text'] =u'Bdyun License 激活工具'
        self.titleLabel["font"] = ("Arial", 20)
        self.titleLabel.grid(row=1, column=0, sticky=SW)

        self.SetupMenu()



    def InitSystem(self):
        try:
            cmd = "ps -ef | grep %s | grep -v '$0' | grep -v 'grep' | awk '{print $2}'" % ('usbdetection')
            aa = commands.getoutput(cmd)
            usb_ids =  str(aa).split()

            if len(usb_ids) == 1:
                return
            elif len(usb_ids) > 1:
                for pid in usb_ids:
                    if int(pid) > 100:
                        cmd = "kill -9 %s" % (str(pid))
                        os.system(cmd)
        except:
            print "usbdetection error"

        PRO_DIR = os.path.join(BASE_DIR, 'script/usbdetection &')
        os.system(PRO_DIR)

    def RemoveContent(self):
        key_dir = "/etc/keyinfo/content"

        if os.path.exists(key_dir):
            print os.system("rm %s" % (key_dir))

    def SetupMenu(self):
        self.CleanPlan()

        self.setframe = LabelFrame(self.master, text=u"配置信息", height=300)
        #self.setframe.grid(row=3, column=0,  columnspan=3, padx=10, pady=10,ipadx=50)
        self.setframe.pack(fill="both",padx=20,pady=40,ipady=10)

        self.userLable = Label(self.setframe, text=u"用户名: ", width=30, anchor="e")
        self.userLable.grid(row=0, column=0,ipady=25)
        self.userEntry = Entry(self.setframe,width=30)
        self.userEntry.insert(END, self.login_user)
        self.userEntry.grid(row=0, column=1, columnspan=2)

        self.passwdLable = Label(self.setframe, text=u"密码: ", width=30, anchor="e")
        self.passwdLable.grid(row=2, column=0)
        self.passwdEntry = Entry(self.setframe,width=30)
        self.passwdEntry.insert(END, self.user_passwd)
        self.passwdEntry['show']='*'
        self.passwdEntry.grid(row=2, column=1)

        self.serverLable = Label(self.setframe, text=u"License 服务器地址: ",  width=30, anchor="e")
        self.serverLable.grid(row=5, column=0,pady=25)
        self.serverEntry = Entry(self.setframe,  width=30)
        self.serverEntry.insert(END, self.license_server)
        self.serverEntry.grid(row=5, column=1)

        self.getButton = Button(self.setframe)
        self.getButton["text"] = u"用户登录"
        self.getButton["command"] = self.confirm
        self.getButton.grid(row=9, column=1, padx=30,pady=5, sticky=SW)
        self.submitButton = Button(self.setframe)

    def CleanPlan(self):
        if self.setframe is not None:
            self.setframe.pack_forget()
        if self.frame2 is not None:
            self.frame2.pack_forget()
        if self.frame3 is not None:
            self.frame3.pack_forget()

    def LicenseMenu(self):
        if self.user_valid != 1:
            tkMessageBox.showinfo(u"告警", MSG['4'])
            return

        #self.setframe.grid_forget()
        self.CleanPlan()
        self.frame2 = LabelFrame(self.master, text=u"License 信息", height=300)
        # self.frame2.grid(row=2, column=6, padx=10, pady=5,ipadx=50)
        self.frame2.pack(fill="both",padx=20,pady=20)

        if self.login_user == 'root':
            self.oneLable = Label(self.frame2, text=u"License Code: ", width=30, anchor="e")
            self.oneLable.grid(row=3, column=0)
            self.oneEntry = Entry(self.frame2,width=30)
            self.oneEntry.insert(END, self.license_code)
            self.oneEntry.grid(row=3, column=1)
        else:
            self.workNoLable = Label(self.frame2, text=u"工单号: ", width=30, anchor="e")
            self.workNoLable.grid(row=0, column=0)
            self.workNoEntry = Entry(self.frame2,width=30)
            self.workNoEntry.insert(END, self.license_code)
            self.workNoEntry.grid(row=0, column=1)

            self.oneLable = Label(self.frame2, text=u"License Code: ", width=30, anchor="e")
            self.oneLable.grid(row=3, column=0)
            self.oneEntry = Entry(self.frame2,width=30)
            self.oneEntry.grid(row=3, column=1)
            self.oneEntry.configure(state=DISABLED)

        self.keyLable = Label(self.frame2, text=u"KEY ID: ", width=30, anchor="e")
        self.keyLable.grid(row=4, column=0)
        self.keyEntry = Entry(self.frame2,width=30)
        self.keyEntry.grid(row=4, column=1)
        self.keyEntry.configure(state=DISABLED)

        self.apLable = Label(self.frame2, text=u"最大AP数: ",  width=30, anchor="e")
        self.apLable.grid(row=5, column=0,pady=5)
        self.apEntry = Entry(self.frame2,  width=30)
        self.apEntry.grid(row=5, column=1)
        self.apEntry.configure(state=DISABLED)

        self.acLable = Label(self.frame2, text=u"最大AC数: ",   width=30, anchor="e")
        self.acLable.grid(row=6, column=0)
        self.acEntry = Entry(self.frame2,   width=30)
        self.acEntry.grid(row=6, column=1)
        self.acEntry.configure(state=DISABLED)

        self.userLable = Label(self.frame2, text=u"最大用户数: ",   width=30, anchor="e")
        self.userLable.grid(row=7, column=0,pady=5)
        self.userEntry = Entry(self.frame2,   width=30)
        self.userEntry.grid(row=7, column=1)
        self.userEntry.configure(state=DISABLED)

        self.expireTimeLable = Label(self.frame2, text=u"到期时间: ",   width=30, anchor="e")
        self.expireTimeLable.grid(row=8, column=0)
        self.expireTimeEntry = Entry(self.frame2,   width=30)
        self.expireTimeEntry.grid(row=8, column=1)
        self.expireTimeEntry.configure(state=DISABLED)

        self.readButton = Button(self.frame2)
        self.readButton["text"] = u"读取ukey信息"
        self.readButton["command"] = self.readUkeyInfo
        self.readButton.grid(row=9, column=0, padx=30,pady=5, sticky=SW)

        self.getButton = Button(self.frame2)
        self.getButton["text"] = u"查询信息"
        # self.getButton["command"] = self.getVersionINfo
        self.getButton["command"] = self.checkWorkOrderInfo
        self.getButton.grid(row=9, column=1, padx=30,pady=5, sticky=SW)
        self.submitButton = Button(self.frame2)
        self.submitButton["text"] = u"写入"
        self.submitButton["command"] = self.writeToKey
        self.submitButton.grid(row=9, column=1,pady=5, sticky=N)

        self.TextFrame()

    def TextFrame(self):
        self.frame3 = LabelFrame(self.master, text=u"日志信息",width=800, height=50)
        #self.frame3.grid(row=10, column=6,padx=10, pady=5,ipadx=0)
        self.frame3.pack(fill="both",padx=20,pady=20)
        self.text = Text(self.frame3,width=126,height=10)
        scr=Scrollbar(self.frame3,orient =VERTICAL,command=self.text.yview)
        scr.grid(row=11, column=6, sticky=NS)
        self.text.grid(row=11, column=0)
        self.text.config(yscrollcommand=scr.set,font=('Arial', 8, 'bold', 'italic'))
        self.text.configure(state=DISABLED)

    def getUserInfo(self):
        info_dict = getLicenseUser(self.license_server, self.port, self.login_user,self.user_passwd)
        print info_dict

        return info_dict.get('res', 10)

    def confirm(self):
        self.login_user = self.userEntry.get()
        self.user_passwd = self.passwdEntry.get()
        self.license_server = self.serverEntry.get()

        if self.login_user == '' or self.user_passwd == '':
            tkMessageBox.showinfo(u"告警", MSG['1'])
            return

        self.user_valid = self.getUserInfo()

        if self.user_valid == 1:
            setLoginUser(os.path.join(BASE_DIR,'file'), self.login_user,self.license_server)
            self.LicenseMenu()
            return
        elif self.user_valid == 2:
            msg = MSG['2']
        else:
            msg = MSG['3']

        tkMessageBox.showinfo(u"告警", msg)
        return

    def show_info(self, msg):
        """show the software info"""
        tkMessageBox.showinfo(u"告警", msg)

    def writeMessage(self,msgString):
        cur_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = "[%s] %s\n" % (cur_time, msgString)

        self.text.configure(state=NORMAL)
        self.text.insert(END, msg)
        self.text.configure(state=DISABLED)

    def readUkeyInfo(self):
        KEY_INFO = self.getDataFromKey()
        self.key_id = KEY_INFO.get('usb_key_hardwareId', "")
        if self.key_id == "":
            time.sleep(3)
            KEY_INFO = LicenseLib.getUsbKeyContent()
            self.key_id = KEY_INFO.get('usb_key_hardwareId', "")
            if self.key_id == "":
                self.writeMessage(u'[错误] 没有读取到USB Key信息，请检查USB Key是否插好')
                return

    def checkWorkOrderInfo(self):
        self.work_no =  self.workNoEntry.get()

        work_info = getWorkOrderInfo(self.license_server, self.port, self.work_no)
        print work_info

        os_info_list = work_info['os_info']
        license_info_list = work_info['license_info']


        if len(os_info_list) > 1:
            msg = u"非法的OS工单"

        msg = u"\nOS: %s   %s\n" % (os_info_list[0].get('productType',""), os_info_list[0].get('sumNo', ""))

        for each in license_info_list:
            msg = msg + "%s\t%s" % (each.get('productType',""), each.get('sumNo', ""))

        self.writeMessage(msg)




    def getVersionINfo(self):
        self.license_code =  self.oneEntry.get()


        if self.login_user == 'root':
            if self.license_code == '':
                msg = u"请填写License Code再验证"
                self.show_info(msg)
                return
        else:
            if self.work_no == '':
                msg = u"请填写工单号再验证"
                self.show_info(msg)
                return


        self.InitSystem()

        # KEY_INFO = self.getDataFromKey()
        # self.key_id = KEY_INFO.get('usb_key_hardwareId', "")
        # if self.key_id == "":
        #     time.sleep(3)
        #     KEY_INFO = LicenseLib.getUsbKeyContent()
        #     self.key_id = KEY_INFO.get('usb_key_hardwareId', "")
        #     if self.key_id == "":
        #         self.writeMessage(u'[错误] 没有读取到USB Key信息，请检查USB Key是否插好')
        #         return

        self.keyEntry.configure(state=NORMAL)
        self.keyEntry.delete('0', END)
        self.keyEntry.insert(END, self.key_id)
        self.keyEntry.configure(state=DISABLED)

        self.writeMessage('Ukey ID: %s' % (self.key_id))
        self.writeMessage('License Code: %s' % (self.license_code))

        self.getLicenseKeyInfo()

        self.apEntry.configure(state=NORMAL)
        self.apEntry.delete('0', END)
        self.apEntry.insert(END, self.max_ap)
        self.apEntry.configure(state=DISABLED)

        self.acEntry.configure(state=NORMAL)
        self.acEntry.delete('0', END)
        self.acEntry.insert(END, self.max_ac)
        self.acEntry.configure(state=DISABLED)

        self.userEntry.configure(state=NORMAL)
        self.userEntry.delete('0', END)
        self.userEntry.insert(END, self.max_user)
        self.userEntry.configure(state=DISABLED)

        self.expireTimeEntry.configure(state=NORMAL)
        self.expireTimeEntry.delete('0', END)
        self.expireTimeEntry.insert(END, self.expire_time)
        self.expireTimeEntry.configure(state=DISABLED)

    def getLicenseKeyInfo(self):
       try:
           self.writeMessage(u'验证License Code ...')
           info_dict = getLicenseInfo(self.license_server, self.port, self.key_id, self.license_code, self.work_no)
           self.max_ap = info_dict.get('max_ap_allowed', '')
           self.max_ac = info_dict.get('max_ac_allowed', '')
           self.max_user = info_dict.get('max_user_allowed', '')
           self.expire_time = info_dict.get('license_expire_time', '')

           if self.expire_time is None:
               self.expire_time = ""

           result = info_dict.get('result',100)
           if result == 100:
               msg = u"License服务器故障"
               self.writeMessage(msg)
               self.show_info(msg)
               return
           elif result == 1:
               msg = u"无效的License Code"
               self.writeMessage(msg)
               self.show_info(msg)
               return
           elif result == 2:
               msg = u"该USB KEY已经注册"
               self.writeMessage(msg)
               self.show_info(msg)
               return
           elif result == 3:
               msg = u"该License Code已经激活"
               self.writeMessage(msg)
               self.show_info(msg)
               return

           self.writeMessage(u'License Code 验证成功')
           self.license_valid = True

       except Exception, e:
           print e
           msg = u"License 服务器访问错误"
           self.writeMessage(msg)
           self.show_info(msg)



    def writeToKey(self):
        params = {'license_key':"",
                  'max_ap_allowed':0,
                  'max_ac_allowed':0,
                  'max_user_allowed':0,
                  'license_expire_time':0,
                  'usb_key_hardwareId':""}

        params['license_key']= self.license_code
        params['usb_key_hardwareId']= self.key_id
        params['max_ap_allowed']= self.max_ap
        params['max_ac_allowed']= self.max_ac
        params['max_user_allowed']= self.max_user
        params['license_expire_time']=self.expire_time
        params['write_path'] = os.path.join(BASE_DIR, 'script/usbwrite')

        if not self.license_valid or params['license_key'] == '' or params['usb_key_hardwareId'] == '':
            msg = u"请先验证License，再写入"
            self.show_info(msg)
            return
        self.writeMessage(u'开始写入USB Key ...')

        rst = LicenseLib.writeUsbKeyContent(params)
        if rst:
            msg = u"USB Key写入成功"
            writeKeyId(self.license_server, self.port, self.key_id, self.license_code)
        else:
            msg = u"USB Key写入失败"

        self.RemoveContent()
        time.sleep(1)

        self.getDataFromKey(flg=2)

        self.writeMessage(msg)
        self.show_info(msg)

    def getDataFromKey(self,flg=1):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        PRO_DIR = os.path.join(BASE_DIR, 'script/usbread&')
        os.system(PRO_DIR)
        time.sleep(3)

        KEY_INFO = LicenseLib.getUsbKeyContent()
        _usb_key_hardwareId = KEY_INFO.get('usb_key_hardwareId', "")

        if _usb_key_hardwareId != "":

            if flg == 1:
                 msg = u"原始 USB Key 信息:\n\t\t"
            else:
                 msg = u"激活License后 USB Key 信息:\n\t\t"

            space_str = '\t----------\t'
            msg = msg + space_str + "[ID]:\t%s" % (KEY_INFO.get('usb_key_hardwareId', "")) + space_str + '\n\t\t'
            msg = msg + space_str + "[Code]:\t%s" % (KEY_INFO.get('license_key', "")) + space_str + '\n\t\t'
            msg = msg + space_str + "[AC]:\t%s" % (KEY_INFO.get('max_ac_allowed', "")) + space_str + '\n\t\t'
            msg = msg + space_str + "[AP]:\t%s" % (KEY_INFO.get('max_ap_allowed', "")) + space_str + '\n\t\t'
            msg = msg + space_str + "[User]:\t%s" % (KEY_INFO.get('max_user_allowed', "")) + space_str + '\n\t\t'
            msg = msg + space_str + "[ExpireTime]:\t%s" % (KEY_INFO.get('license_expire_time', "")) + space_str + '\n\t\t'

            self.writeMessage(msg)

        return KEY_INFO

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
            "max_ap_allowed": 0,
            "max_ac_allowed": 0,
            "max_user_allowed":0,
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

        hardwareId ="default licence key"

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
            Max_AP_Allowed = 0
            Max_AC_Allowed = 0
            Max_User_Allowed = 0
            License_Expire_Time = "2018-10-01"
            License_Valid_Mask =""
            License_Key ="00000000"
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

def getLicenseInfo(ip, port, key_id, license_code,work_no):
    connection_str='http://%s:%s/adminbd/license_activate?'% (ip, port)
    connection_str = connection_str + 'key_id=' + key_id
    connection_str = connection_str + '&license_code=' + license_code
    connection_str = connection_str + '&work_no=' + work_no

    f = urllib2.urlopen(connection_str)
    response = f.read()

    info_dict = {}
    info_dict = json.JSONDecoder().decode(response)

    return info_dict

def getWorkOrderInfo(ip, port,work_order_id):
    connection_str='http://%s:%s/adminbd/work_order?'% (ip, port)
    connection_str = connection_str + '&work_no=' + work_order_id
    print connection_str

    f = urllib2.urlopen(connection_str)
    response = f.read()

    info_dict = {}
    info_dict = json.JSONDecoder().decode(response)

    return info_dict

def writeKeyId(ip, port, key_id, license_code):
    connection_str='http://%s:%s/adminbd/update_key_id?'% (ip, port)
    connection_str = connection_str + 'key_id=' + key_id
    connection_str = connection_str + '&license_code=' + license_code

    f = urllib2.urlopen(connection_str)
    response = f.read()

    return response


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

root = Tk()


imgicon = PhotoImage(file=os.path.join(BASE_DIR, 'file/license.gif'))
root.tk.call('wm', 'iconphoto', root._w, imgicon)
root.title(u"BDCloud License 激活工具")
root.geometry("820x530")

root.resizable(width=FALSE, height=FALSE)

MENU_ROOT = LicenseManager(root)
menubar = Menu(root)
menubar.add_command(label=u"用户登录", command=MENU_ROOT.SetupMenu)
menubar.add_command(label=u"License激活", command=MENU_ROOT.LicenseMenu)

root.config(menu=menubar)

root.mainloop()

