# -*- coding: UTF-8 -*-
import sys
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from adminbd.models import LicenseRecord,CloudInformation,LicenseType,LicenseParams,WorkOrderNum,WorkOrderInformation
from datetime import datetime
import os.path
import logging
import random
import string
import time
from django.utils import timezone
import pytz
import json
from adminbd.models import SystemConfig
# Create your views here.


DOWNLOAD_FILE_PATH = "static/download_file/"
DOWNLOAD_FILE_LICENSE_CLIENT_FILE = "bdls_1.0.tar.gz"
DOWNLOAD_FILE_LICENSE_USAGE_FILE = "私有云License管理手册.docx"


def local2utc(local_st):
    time_struct = time.mktime(local_st.timetuple())
    utc_st = datetime.utcfromtimestamp(time_struct)
    return utc_st

#主页
class IndexView(View):
    def get(self, request):
        print "in IndexView"
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        cloud_id = request.GET.get('cloud_id')
        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        all_files = request.session.get('all_files')
        context = {}
        print "cloud_id",cloud_id

        if cloud_id:
            cloudObj = CloudInformation.objects.get(id=cloud_id)

            if is_superuser:
                licenseRecords = cloudObj.licenserecord_set.exclude(license_code__istartswith = "TEMP")
                context['licenses'] = licenseRecords
            else:
                licenseRecords = cloudObj.licenserecord_set.all()
                licenseList = []
                licenseList.append(licenseRecords)
                context['licenses'] = licenseList
            context['cloud_id'] = int(cloud_id)
        else:
            if is_superuser:
                LicenseRecords = LicenseRecord.objects.exclude(license_code__istartswith = "TEMP")
                context['licenses'] = LicenseRecords
            else:
                user = User.objects.get(username=username)
                user_clouds = user.cloudinformation_set.all()
                licenseList = []
                for cloud in user_clouds:
                    licenses = LicenseRecord.objects.filter(cloudInfo_id=cloud.id)
                    licenseList.append(licenses)
                context['licenses'] = licenseList

        if is_superuser:
            cloudInfos = CloudInformation.objects.exclude(cloudName = "")
        else:
            user = User.objects.get(username=username)
            cloudInfos = user.cloudinformation_set.exclude(cloudName = "")
        context['cloudInfos'] = cloudInfos
        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['all_files'] = all_files
        print "is_superuser=",is_superuser
        print "all_files=",all_files
        return render(request, 'index.html',context)
#主页yun
class IndexViewYun(View):
    def get(self, request):
        print "in IndexYunView"
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')
        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        all_files = request.session.get('all_files')
        context = {}
        if is_superuser:
            # cloudInfos = CloudInformation.objects.filter(cloudNum__istartswith = "BUSS")
            cloudInfos = CloudInformation.objects.exclude(cloudName= "")
            context['cloudInfos'] = cloudInfos
        else:
            user = User.objects.get(username=username)
            cloudInfos = user.cloudinformation_set.exclude(cloudName = "")
            context['cloudInfos'] = cloudInfos

        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['all_files'] = all_files
        return render(request, 'license_yun.html',context)

#用户主页
class UserIndexView(View):
    def get(self, request):
        print "in IndexYunView"
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        all_files = request.session.get('all_files')
        context = {}
        if is_superuser:
            userSets = User.objects.all()
            context['userSets'] = userSets
        else:
            print "not superuser,no right to display the user list"
            return HttpResponse("No Right")

        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['all_files'] = all_files
        return render(request, 'user_list.html',context)

#zte code
def genZteCode():
    print "call genZteCode() fun"

    year_context = {"2010":"A","2011":"B","2012":"C","2013":"D","2014":"E","2015":"F","2016":"G",
                    "2017":"H","2018":"J","2019":"K","2020":"L","2021":"M","2022":"N","2023":"P",
                    "2024":"Q","2025":"R","2026":"T","2027":"U","2028":"V","2029":"W","2030":"X",
                    "2031":"Y"}
    month_context = {"1":"1","2":"2","3":"3","4":"4","5":"5","6":"6","7":"7","8":"8","9":"9",
                     "10":"A","11":"B","12":"C"}

    day_context = {"1":"1","2":"2","3":"3","4":"4","5":"5","6":"6","7":"7","8":"8","9":"9",
                     "10":"A","11":"B","12":"C","13":"D","14":"E","15":"F","16":"G","17":"H",
                   "18":"I","19":"J","20":"K","21":"L","22":"M","23":"N","24":"O","25":"P",
                   "26":"Q","27":"R","28":"S","29":"T","30":"U","31":"V"
                   }

    license_coun = SystemConfig.objects.filter(attribute='zte_license_count')
    if license_coun.count() == 0:
        system_license = SystemConfig(attribute='zte_license_count',value="0")
        system_license.save()
    value,res = SystemConfig.getAttrValue('zte_license_count')
    print type(value),res,int(value)
    try:
        d_sn = (str(int(value)+1)).zfill(5)
        print d_sn

        if d_sn.__len__() > 5:
            print "not format name"
            return False
        start_date = datetime.now().strftime("%Y-%m-%d")
        print start_date
        print timezone.now()
        print datetime.now()
        cur_str_time = start_date.split("-")
        y = cur_str_time[0]
        m = cur_str_time[1]
        d = cur_str_time[2]
        print y,m,d,type(y)

        y_value = year_context.get(y)
        m_value = month_context.get(m)
        d_value = day_context.get(d)
        print y_value,m_value,d_value

        if y_value and m_value and d_value:
            print "ZTEKPBY"+str(y_value)+str(m_value)+str(d_value)+d_sn
            return "ZTEKPBY"+str(y_value)+str(m_value)+str(d_value)+d_sn
        else:
            return False
    except Exception,e:
        print e
    return False

#bd code 生成
def genBdCode(code_type):
    license_coun = SystemConfig.objects.filter(attribute='bd_license_count')
    if license_coun.count() == 0:
        system_license = SystemConfig(attribute='bd_license_count',value="0")
        system_license.save()
    value,res = SystemConfig.getAttrValue('bd_license_count')
    print type(value),res,int(value)
    code = "BCPLIC"+str(code_type)+str(int(value)+1)
    print code

    return code

def genLicenseCode(code_type):
    if code_type == 'bdcode':
        return  genBdCode('F')
    elif code_type == 'ztecode':
        return genZteCode()
    else:
        return ""

def genCloudNum(code_type):
    timestamp = str(int(time.time()))
    nonce = ''.join(random.sample(string.digits,6))
    code = code_type+timestamp+nonce
    return code

class AddLicenseView(View):
    def get(self,request):
        username = request.session.get('username')
        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        all_files = request.session.get('all_files')
        if not username:
            return render(request,'license_login.html')
        print "in add license get func"

        context = {}
        code_type = request.GET.get('code_type','0')
        print code_type
        print "00000000"
        # if code_type in [0,"0"]:
        #     licenseParams = LicenseParams.objects.filter(product_type = 2,vesion_type=1)
        #     context['licenseParams'] = licenseParams
        #     print "licenseParams count",licenseParams.count()
        #     for licenseParam in licenseParams:
        #         print licenseParam.cloudRankName
        # elif code_type in [1,"1"]:
        #     licenseParams = LicenseParams.objects.filter(product_type = 2,vesion_type=2)
        #     print "licenseParams count",licenseParams.count()
        #     context['license_Params'] = licenseParams
        #     for licenseParam in licenseParams:
        #         print licenseParam.cloudRankName
        licenseParams = LicenseParams.objects.filter(product_type = 2)
        context['licenseParams'] = licenseParams
        cloudInfos = CloudInformation.objects.exclude(cloudName = "")
        context['cloudInfos'] = cloudInfos
        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['all_files'] = all_files

        #
        # if request.is_ajax():
        #     print "in request.is_ajax() "
        #     code_type = request.GET.get('code_type')
        #     license_code = ""
        #     if code_type == "0":
        #         license_code = genBdCode("D")
        #     elif code_type == "1":
        #         license_code = genZteCode()
        #     else:
        #         return HttpResponse("error!!!!")
        #     #response code
        #     if license_code:
        #         return HttpResponse(license_code)
        #     else:
        #         return HttpResponse("error!!!!")
        return render(request, 'license_added.html',context)

    def post(self,request):
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        print "in add license post func"
        license_time = request.POST.get('license_time')
        cloud_info = request.POST.get('cloud_info')
        lower = request.POST.get('lower',0)
        low = request.POST.get('low',0)
        medium = request.POST.get('medium',0)
        high = request.POST.get('high',0)
        higher = request.POST.get('higher',0)
        data_license = request.POST.get('data_license','')
        charging_license = request.POST.get('charging_license','')
        work_num = request.POST.get('work_num','')
        uu = {}
        wk = WorkOrderNum.objects.filter(workOrderNum = work_num)
        if wk.count() > 0:
            result = 4
            uu = {'res':result}
            return JsonResponse(uu)
        #one cloud has only one valid license
        if cloud_info:
            cloudObj = CloudInformation.objects.get(id=int(cloud_info))
            licenseRecords = cloudObj.licenserecord_set.all()
            if licenseRecords.count() > 0:
                for licenseRecord in licenseRecords:
                    if licenseRecord.is_valid != 0:
                        result = 3
                        uu = {'res':result}
                        return JsonResponse(uu)
        #format expire time
        cur_time = datetime.now()
        print cur_time
        cur_year = cur_time.year
        fut_year = cur_year+int(license_time)
        cur_time = cur_time.replace(year=fut_year)
        print cur_time


        code_type = request.POST.get('code_type','0')

        print "code_type:%s"%str(code_type)
        #根据code的类型自动生成license code
        license_code = ""
        if code_type == "0":
            license_code = genBdCode("D")
        elif code_type == "1":
            license_code = genZteCode()
        print "生成的license CODE",license_code,
        #license_code is not unique
        licenseRecordObj = LicenseRecord.objects.filter(license_code=license_code)
        if licenseRecordObj.count() > 0:
            print "license_code is not unique"
            result = 2
            uu = {'res':result}
            return JsonResponse(uu)

        # add new LicenseRecord
        try:
            # cloud_num_name = genCloudNum("BUSS")
            # cloudInfo = CloudInformation()
            # cloudInfo.cloudName = cloud_num_name
            # cloudInfo.cloudName = cloud_num_name
            # cloudInfo.installAddress = "bd306"
            # cloudInfo.buyer = "bd306"
            # cloudInfo.contacts = "root"
            # cloudInfo.cloudNum = cloud_num_name
            # cloudInfo.save()
            #
            # userObj = User.objects.get(username="root")
            # cloudInfo.cloudUser.add(userObj)
            # print "cloud added user successfully"

            license = LicenseRecord(licenseType="1")
            license.license_code = license_code
            license.cloudInfo_id = int(cloud_info)
            license.expire_time = cur_time
            license.save()
            updateCodeCount(license_code)
            #license 功能
            if data_license:
                value = int(license.licenseType) | int(data_license)
                license.licenseType = value
                license.save()
            if charging_license:
                value = int(license.licenseType) | int(charging_license)
                license.licenseType = value
                license.save()

            workNum = WorkOrderNum(license_id=license.id,workOrderNum = work_num)
            workNum.save()

            params_dic = {
                "BCP8200-Lic-32":lower,
                "BCP8200-Lic-64":low,
                "BCP8200-Lic-128":medium,
                "BCP8200-Lic-512":high,
                "BCP8200-Lic-1024":higher
            }
            basic_dict = {}
            licensePas = LicenseParams.objects.all()
            for licensePa in licensePas:
                basic_dict[licensePa.cloudRankName] = [licensePa.maxAPs,licensePa.maxACs,licensePa.maxUsers]
            print basic_dict
            maxAPs = 0
            maxACs = 0
            maxUsers = 0
            for key,value in params_dic.items():
                if value in [0,'0']:
                    continue
                else:
                    wkInfo = WorkOrderInformation(
                        materiel_name=key,
                        materiel_count=value,
                        workordernum_id=workNum.id)
                    wkInfo.save()
                    if key in basic_dict.keys():
                        maxAPs += int(value)*int(basic_dict[key][0])
                        maxACs += int(value)*int(basic_dict[key][1])
                        maxUsers += int(value)*int(basic_dict[key][2])
                    else:
                        return HttpResponse("illegal license params")
            license.maxAps = maxAPs
            license.maxAcs = maxACs
            license.maxUsers = maxUsers
            license.save()
            print "save license successfully"
            updateCodeCount(str(license_code))
            result = 1
            uu = {'res':result}
            return JsonResponse(uu)
        except Exception,e:
            print e
        result = 0
        uu = {'res':result}
        return JsonResponse(uu)

class EditLicenseView(View):
    def get(self,request):
        username = request.session.get('username')
        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        all_files = request.session.get('all_files')
        if not username:
            return render(request,'license_login.html')
        print "in edit license get func"

        license_id = request.GET.get('id',None)
        print "license_id=",license_id
        context = {}

        try:
            get_dic = {}
            if license_id is not None:
                licenseRecord = LicenseRecord.objects.get(id=int(license_id))
                context['licenseRecord'] = licenseRecord

                if int(licenseRecord.licenseType) & 4:
                    context['data_id'] = 4
                    print "计费版本"
                if int(licenseRecord.licenseType) & 2:
                    context['charging_id'] = 2
                    print "大数据版本"

                wkOrders = WorkOrderNum.objects.filter(license_id=licenseRecord.id).order_by('-id')
                print wkOrders.count()
                print "-id count()"
                if wkOrders.count() >0:
                    wkInfos = WorkOrderInformation.objects.filter(workordernum_id=wkOrders[0].id)
                    for wkInfo in wkInfos:
                        get_dic[wkInfo.materiel_name] = wkInfo.materiel_count

                    # basic_dic = {
                    #         "BCP8200-Lic-32":3,
                    #         "BCP8200-Lic-64":9,
                    #         "BCP8200-Lic-128":"medium",
                    #         "BCP8200-Lic-512":"high",
                    #         "BCP8200-Lic-1024":"higher"
                    #     }
                    if "BCP8200-Lic-32" in get_dic.keys():
                        context['lower'] = get_dic['BCP8200-Lic-32']
                    else:
                        context['lower'] = 0
                    if "BCP8200-Lic-64" in get_dic.keys():
                        context['low'] = get_dic['BCP8200-Lic-64']
                    else:
                        context['low'] = 0
                    if "BCP8200-Lic-128" in get_dic.keys():
                        context['mid'] = get_dic['BCP8200-Lic-128']
                    else:
                        context['mid'] = 0
                    if "BCP8200-Lic-512" in get_dic.keys():
                        context['high'] = get_dic['BCP8200-Lic-512']
                    else:
                        context['high'] = 0
                    if "BCP8200-Lic-1024" in get_dic.keys():
                        context['higher'] = get_dic['BCP8200-Lic-1024']
                    else:
                        context['higher'] = 0
                    print context['higher']
                    print context['high']
                    print context['mid']
                    print context['low']
                    print context['lower']
        except Exception,e:
            print e

        licenseParams = LicenseParams.objects.filter(product_type = 2,vesion_type=1)
        context['licenseParams'] = licenseParams

        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['all_files'] = all_files


        return render(request, 'license_edit.html',context)

    def post(self,request):
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        print "in edit license post func"
        params = request.POST.copy()
        print params
        license_id = params['license_id']
        data_license = request.POST.get('data_license','')
        charging_license = request.POST.get('charging_license','')

        lower = request.POST.get('lower',0)
        low = request.POST.get('low',0)
        medium = request.POST.get('medium',0)
        high = request.POST.get('high',0)
        higher = request.POST.get('higher',0)

        params_dic = {
                "BCP8200-Lic-32":lower,
                "BCP8200-Lic-64":low,
                "BCP8200-Lic-128":medium,
                "BCP8200-Lic-512":high,
                "BCP8200-Lic-1024":higher
            }
        basic_dict = {}
        licensePas = LicenseParams.objects.all()
        for licensePa in licensePas:
            basic_dict[licensePa.cloudRankName] = [licensePa.maxAPs,licensePa.maxACs,licensePa.maxUsers]
        print basic_dict

        maxAPs = 0
        maxACs = 0
        maxUsers = 0
        try:
            workNum = WorkOrderNum(license_id=license_id,workOrderNum = getRandom16Num())
            workNum.save()
            for key,value in params_dic.items():
                if value in [0,'0']:
                    continue
                else:
                    wkInfo = WorkOrderInformation(
                        materiel_name=key,
                        materiel_count=value,
                        workordernum_id=workNum.id)
                    wkInfo.save()
                    if key in basic_dict.keys():
                        print int(value)*int(basic_dict[key][0])
                        maxAPs += int(value)*int(basic_dict[key][0])
                        maxACs += int(value)*int(basic_dict[key][1])
                        maxUsers += int(value)*int(basic_dict[key][2])
                    else:
                        return HttpResponse("illegal license params")


            uu = {}

            licenseObj = LicenseRecord.objects.filter(id=int(license_id))
            if licenseObj.count() > 0:
                licenseObj.update(
                    maxAps=maxAPs,
                    maxAcs=maxACs,
                    maxUsers=maxUsers
                )

                if data_license != "":
                    if charging_license != "":
                        value = 7
                    else:
                        value = 5
                else:
                    if charging_license != "":
                        value = 3
                    else:
                        value = 1
                licenseObj.update(licenseType=value)
                result = 0
                uu = {'res':result}
                return JsonResponse(uu)
        except Exception,e:
            print e
        result = 1
        uu = {'res':result}
        return JsonResponse(uu)

class AddCloudView(View):
    def get(self,request):
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        all_files = request.session.get('all_files')
        context = {}
        cloudUsers = User.objects.all()
        context['cloudUsers'] = cloudUsers
        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['all_files'] = all_files

        return render(request, 'license_addyun.html',context)

    def post(self,request):
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')
        print "in add cloud post func"
        params = request.POST.copy()
        print params
        cloud_name = params['cloud_name']
        cloud_user_id = params['cloud_user']
        install_add = params['install_add']
        cloud_buyer = params['cloud_buyer']
        contacts = params['contacts']
        phone = params['phone']
        clouds = CloudInformation.objects.filter(cloudName=cloud_name)
        if clouds.count() > 0:
            result = 2
            uu = {'res':result}
            return JsonResponse(uu)
        uu = {}
        try:
            cloudinfo = CloudInformation()
            cloudinfo.cloudName = cloud_name
            cloudinfo.installAddress = install_add
            cloudinfo.buyer = cloud_buyer
            cloudinfo.contacts = contacts
            cloudinfo.phone = phone
            cloud_num = genCloudNum("BUSS")
            cloudinfo.cloudNum = cloud_num
            cloudinfo.save()
            if cloud_user_id:
                userObj = User.objects.get(id=int(cloud_user_id))
                cloudinfo.cloudUser.add(userObj)
                print "cloud added user successfully"

            result = 1
            uu = {'res':result}
            return JsonResponse(uu)
        except Exception,e:
            print e
        result = 0
        uu = {'res':result}
        return JsonResponse(uu)

class AddUserView(View):
    def get(self,request):
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        all_files = request.session.get('all_files')
        context = {}
        # cloudInfos = CloudInformation.objects.all()
        # print cloudInfos.count()
        cloudInfos = CloudInformation.objects.exclude(cloudName = "")
        print cloudInfos.count()
        print "cloud counts"
        context['cloudInfos'] = cloudInfos
        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['all_files'] = all_files
        print "is_superuser=",is_superuser
        return render(request, 'user_added.html',context)

    def post(self,request):
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        params = request.POST.copy()
        print params
        user_name = params['user_name']
        sel_cloud = params['sel_cloud']
        contactor = params['first_name']
        phone = params['phone']
        cloud_id_list = sel_cloud.split(',')
        super_user = params['super_user']

        uu = {}
        userSet = User.objects.filter(username=user_name)
        if userSet.count() > 0:
            print "user exists"
            result = 2
            uu = {'res':result}
            return JsonResponse(uu)

        try:
            user = User.objects.create_user(username=user_name,password="123456")
            print "create new user and inital pwd is 123456"
            print user
            if super_user == 1:
                user.is_superuser = 1
            else:
                user.is_superuser = 0
            user.user_level = super_user
            user.is_staff = 1
            user.is_active = 1
            user.date_joined = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
            if contactor:
                user.contacts = contactor
            if phone:
                user.phone_num = phone
            #add cloud admin
            if cloud_id_list:
                for cloud_id in cloud_id_list:
                    cloudObj = CloudInformation.objects.filter(id=int(cloud_id))
                    user.cloudinformation_set.add(cloudObj[0])
                    user.save()

                result = 1
                uu = {'res':result}
                return JsonResponse(uu)
            else:
                result = 0
                uu = {'res':result}
                return JsonResponse(uu)
        except Exception,e:
            print e
        result = 0
        uu = {'res':result}
        return JsonResponse(uu)


class UserCloudView(View):
    def get(self, request):
        print "in UserCloudView "
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        user_id = request.GET.get('id')
        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        all_files = request.session.get('all_files')
        context = {}

        if user_id:
            userObj = User.objects.get(id=user_id)
            userCloudSets = userObj.cloudinformation_set.all()
            context['userCloudSets'] = userCloudSets
            context['userObj'] = userObj

        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['all_files'] = all_files

        return render(request, 'cloud_user.html',context)

class KeyParamsView(View):
    def get(self, request):
        print "in IndexView"
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        key_id = request.GET.get('id',None)
        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        all_files = request.session.get('all_files')
        context = {}
        try:
            if key_id is not None:
                licenseObj = LicenseRecord.objects.get(id=key_id)
                workorders = WorkOrderNum.objects.filter(license_id=licenseObj.id)
                dic_list = []
                for workorder in workorders:
                    wkInfos = WorkOrderInformation.objects.filter(workordernum_id=workorder.id)
                    for wkInfo in wkInfos:
                        dic_tmp = {}
                        dic_tmp['wkNum'] = workorder.workOrderNum
                        dic_tmp['m_name'] = wkInfo.materiel_name
                        dic_tmp['m_count'] = wkInfo.materiel_count
                        dic_list.append(dic_tmp)
                print dic_list
                context['dic_list'] = dic_list
                context['licenseObj'] = licenseObj
        except Exception,e:
            print e
        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['all_files'] = all_files

        return render(request, 'license_params.html',context)

#lisence 登陆
@csrf_exempt
def license_login(request):
    if request.method == "GET":
        return render(request, 'license_login.html')
    if request.method == "POST":
        params = request.POST.copy()
        user_name = params['username']
        password = params['password']
        print "---------"
        print params

        result = {}
        userObj = User.objects.filter(username=user_name)
        if userObj.count() == 0:
            print "username not exists"
            result['res'] = 2
            return JsonResponse(result)

        user_pass = authenticate(username=user_name,password=password)
        if user_pass:
            request.session['username'] = user_name
            request.session['is_superuser'] = user_pass.is_superuser
            request.session['user_level'] = user_pass.user_level
            cur_path=os.path.abspath('.')
            print "os.path.abspath('.')",cur_path
            target_path=os.path.join(cur_path, DOWNLOAD_FILE_PATH)
            print "target_path",target_path
            all_files = os.listdir( target_path )
            request.session['all_files'] = all_files
            result['res'] = 1
            return JsonResponse(result)
        else:
            result['res'] = 0
            return JsonResponse(result)

@csrf_exempt
def license_logout(request):
    if request.method == "GET":
        username = request.session.get('username',False)
        if username is False:
            return render(request, 'license_login.html')

        request.session.flush()
        return HttpResponseRedirect('license_login')

class UpdateKeyIDView(View):
    def get(self,request):
        params = request.GET.copy()
        # key_id = params['key_id']
        # license_code = params['license_code']
        key_id = request.GET.get("key_id",'')
        code_type = request.GET.get("code_type",'')
        license_code = request.GET.get("license_code",'')

        try:
            #update license key_id
            licenses = LicenseRecord.objects.filter(license_code=license_code)
            if licenses.count() > 0:
                licenses.update(key_id=key_id)
                print "update license key_id successfully"

                #modify license status
                licenses.update(license_status=LicenseRecord.OPEN)
                print "license status updated successfully"

            # if license_code.startswith("ZTEKPBY"):
            #
            #     license_coun = SystemConfig.objects.filter(attribute = "zte_license_count")
            #     value = int(license_code[10:])
            #     license_coun.update(value=str(value))
            # elif license_code.startswith("BCPLIC"):
            #     license_coun = SystemConfig.objects.filter(attribute='bd_license_count')
            #     value = license_code.split("F")[1]
            #     license_coun.update(value=value)
            # else:
            #     return HttpResponse("illegal code type")

            return HttpResponse("OK")
        except Exception,e:
            print e

        return HttpResponse("Error")

def updateCodeCount(license_code):
    if license_code.startswith("ZTEKPBY"):
        license_coun = SystemConfig.objects.filter(attribute='zte_license_count')
        value = int(license_code[10:])
        license_coun.update(value=str(value))
        print "save zte_license_count in system config table successfully"
    elif license_code.startswith("BCPLICD"):
        license_coun = SystemConfig.objects.filter(attribute='bd_license_count')
        value = license_code.split("D")[1]
        license_coun.update(value=value)
        print "save bd_license_count D in system config table successfully"
    elif license_code.startswith("BCPLICF"):
        license_coun = SystemConfig.objects.filter(attribute='bd_license_count')
        value = license_code.split("F")[1]
        license_coun.update(value=value)
        print "save bd_license_count F in system config table successfully"

def getWorkNoInfo(work_no,work_lineno, rst_dict={}):
    #新的工单号,获取工单号下的物料信息，提取、保存并返回给客户端进行显示
    from suds import WebFault
    from suds.client import Client

    print "[getWorkNoInfo] starting ......"

    #work_no = 'SC20170928001'
    order_server_ip,server_value = SystemConfig.getAttrValue('server_ip')
    if not server_value:
        order_server_ip = '180.169.230.122'
    order_server_port, port_value = SystemConfig.getAttrValue('server_port')
    if not port_value:
        order_server_port = '8091'

    user_url='http://%s:%s/WebService/OMGR?WSDL' % (order_server_ip, order_server_port)
    client=Client(user_url)
    print "[getWorkNoInfo] get product informations ......"
    lic_info = LicenseParams.objects.all()

    basic_lic_dict = {}
    os_dict = {}
    business_dict = {}

    for each in lic_info:
        if each.product_type == 1:
            os_dict[each.code] = [each.cloudRankName,each.maxAPs]
        elif each.product_type == 2:
            basic_lic_dict[each.code] = [each.cloudRankName,each.maxAPs, each.maxACs,each.maxUsers]
        else:
            business_dict[each.code] = [each.cloudRankName, each.maxAPs]

    license_ids =  basic_lic_dict.keys()
    os_ids = os_dict.keys()
    buss_ids =  business_dict.keys()
    print "[getWorkNoInfo] process work [%s] informations ......" % (work_no)

    try:
        result=client.service.loadOrderInfoByNoiCloud('bdswer03dfd3ssdfedsjhrt', work_no, work_lineno)
        result = json.loads(result)
        print result
    except Exception,e:
        print "get Order Error:%s" % (str(e))
        rst_dict['result'] = 1
        print rst_dict
        return rst_dict

    rst_dict['cloud_name'] = result.get('finalCustomerName', '')
    rst_dict['cloud_buyer'] = result.get('customer', '')
    rst_dict['contacts'] = result['createEmployee'].get('realName', '')
    rst_dict['phone'] = result['createEmployee'].get('workphone', '')
    license_code = result.get('license_code', '')

    for details in result['details']:
        if license_code == '':
            license_code = result.get('license_code', '')

        if details['swVersion'] == u"同博达":
            rst_dict['version_type'] = 'bdcode'
        else:
            rst_dict['version_type'] = 'ztecode'

        tmp_dict = {}
        if details['productNo'] in os_ids:
            tmp_dict['productNo'] = details['productNo']
            tmp_dict['productType'] = details['productType']
            tmp_dict['sumNo'] = details['sumNo']

            rst_dict['os_info'].append(tmp_dict)
        elif details['productNo'] in license_ids:
            tmp_dict['productNo'] = details['productNo']
            tmp_dict['productType'] = details['productType']
            tmp_dict['sumNo'] = details['sumNo']

            rst_dict['license_info'].append(tmp_dict)
        elif details['productNo'] in buss_ids:
            tmp_dict['productNo'] = details['productNo']
            tmp_dict['productType'] = details['productType']
            tmp_dict['sumNo'] = details['sumNo']

            rst_dict['buss_info'].append(tmp_dict)
        else:
            continue

    rst_dict['license_code'] = license_code

    rst_dict['license_type'] =1
    if rst_dict['license_code'] == '' and len(rst_dict['os_info']) == 0:
        print "ERROR:new work OS error: %s" % (str(rst_dict['os_info']))
        rst_dict['result'] = 3

    if len(rst_dict['os_info']) > 1:
        print "ERROR:work OS error: %s" % (str(rst_dict['os_info']))
        rst_dict['result'] = 2
    elif len(rst_dict['os_info']) == 1:
        os_productNo = rst_dict['os_info'][0]['productNo']
        rst_dict['license_type'] = int(rst_dict['license_type']) | os_dict[os_productNo][1]

    if len(rst_dict['buss_info']) >= 1:
        buss_productNo = rst_dict['buss_info'][0]['productNo']
        rst_dict['license_type'] = int(rst_dict['license_type']) | os_dict[buss_productNo][1]

    print "[getWorkNoInfo] get return work informations ......"

    #调试
    # rst_dict['license_type'] = 7
    # rst_dict['license_code'] ='BCPLICF1'

    maxAPs = 0
    maxACs = 0
    maxUser = 0

    for each in rst_dict['license_info']:
        print "[getWorkNoInfo] ", each
        if each['productNo'] in basic_lic_dict.keys():
            maxAPs = maxAPs + int(each['sumNo'])*int(basic_lic_dict[each['productNo']][1])
            maxACs = maxACs + int(each['sumNo'])*int(basic_lic_dict[each['productNo']][2])
            maxUser = maxUser + int(each['sumNo'])*int(basic_lic_dict[each['productNo']][3])

    rst_dict['max_ap_allowed'] = maxAPs
    rst_dict['max_ac_allowed'] = maxACs
    rst_dict['max_user_allowed'] = maxUser

    return rst_dict

def get_work_order_information(work_order_id,license_id,rst_dict = {}):
    print "重复查询工单号"
    wkObjs = WorkOrderNum.objects.filter(id=work_order_id)
    if wkObjs.count() > 0:
        rst_dict['work_type'] = wkObjs[0].product_type

    wkObjs = WorkOrderInformation.objects.filter(workordernum_id=work_order_id)
    for wkObj in wkObjs:
        tmp_dict = {}
        tmp_dict['productType'] = wkObj.materiel_name
        tmp_dict['sumNo'] = wkObj.materiel_count

        if wkObj.materiel_type == 1:
            rst_dict['os_info'].append(tmp_dict)
        elif wkObj.materiel_type == 2:
            rst_dict['license_info'].append(tmp_dict)
        elif wkObj.materiel_type == 3:
            rst_dict['buss_info'].append(tmp_dict)

    print rst_dict
    licenseObj = LicenseRecord.objects.filter(id=license_id)
    rst_dict['max_ap_allowed'] = licenseObj[0].maxAps
    rst_dict['max_ac_allowed'] = licenseObj[0].maxAcs
    rst_dict['max_user_allowed'] = licenseObj[0].maxUsers
    rst_dict['license_code'] = licenseObj[0].license_code
    rst_dict['license_type'] = licenseObj[0].licenseType
    rst_dict['license_status'] = licenseObj[0].license_status
    rst_dict['usbkey_id'] = licenseObj[0].key_id

    if rst_dict['license_code'].find('ZTE') == 0:
        rst_dict['version_type'] = 'ztecode'
    else:
        rst_dict['version_type'] = 'bdcode'

    cloud_info_obj = licenseObj[0].cloudInfo
    rst_dict['cloud_name'] = cloud_info_obj.cloudName
    rst_dict['cloud_buyer'] = cloud_info_obj.buyer
    rst_dict['contacts'] = cloud_info_obj.contacts
    rst_dict['phone'] = cloud_info_obj.phone


    return rst_dict

#
def get_work_order_info(request):
    print "[get_work_order_info] starting ......"
    work_str = request.GET.get('work_no', "123448")
    license_time = '2'                             #license 有效期，比如1,2,3,5单位：年

    cur_time = datetime.now()
    cur_year = cur_time.year
    fut_year = cur_year+int(license_time)
    cur_time = cur_time.replace(year=fut_year)
    cur_time =  cur_time.strftime("%Y-%m-%d")
    print "[get_work_order_info] current time: %s" % (cur_time)

    rst_dict = {'result':0,'os_info':[], 'license_info':[], 'buss_info':[]}
    #result: 0 suc  1 order confirm error 2 os error 3 license error  4 work no error 5 exp no licensecode
    rst_dict['license_expire_time'] = cur_time
    rst_dict['work_type'] = 0
    rst_dict['license_status'] = 0

    work_no_list = work_str.split('-')
    print work_no_list
    if len(work_no_list) != 2:
        rst_dict['result'] = 4
        return JsonResponse(rst_dict)

    work_no = work_no_list[0]
    work_lineno = work_no_list[1]

    licen = WorkOrderNum.objects.filter(workOrderNum = work_no)

    if licen.count() > 0:
        #重复查询工单号
        rst_dict = get_work_order_information(licen[0].id, licen[0].license_id, rst_dict=rst_dict)

        return JsonResponse(rst_dict)
    else:
        rst_dict = getWorkNoInfo(work_no, work_lineno, rst_dict=rst_dict)

        if rst_dict['result'] !=0:
            return JsonResponse(rst_dict)

    print "[get_work_order_info] write work information to DB"
    license_code = rst_dict.get('license_code', "")                               # license_code = 'ZTEKPBYHAL00002'
    license_type = rst_dict.get('license_type', '5')                              # 1：基本版本，4：大数据版本,2：计费版本（3：基本+计费，5：基本+大数据，7：基本+计费+大数据）

    if license_code == '':
        #第一次验证激活
        #1.云平台的管理员（即服务器保存的用户名密码，只有提供用户名，才能登陆，才能查看自己云平台以及license的相关信息）
        #2.云平台的相关信息（云平台管理员必须有，其次云平台编号：暂时自己生成。其他包括名称、购买方、安装地址、联系人、联系电话可有可无）
        #3.license相关信息（工单号、key_id、code、status、valid、reset、random_num、type、params、云平台、过期时,maxaps,maxacs,maxusers ）

        try:
            #username = ''
            # contactor = ''
            # phone = ''
            #管理员添加的相关操作
            # userObj = User.objects.filter(username=username)
            # uId = 0
            # if userObj.count() > 0:
            #     uId = userObj[0].id
            #     print "user exist id is %s"%uId
            # else:
            #     user = User.objects.create_user(username=username,password="123456")
            #     print "create new user and inital pwd is 123456"
            #     print user
            #     # if super_user == 1:
            #     #     user.is_superuser = 1
            #     # else:
            #     user.is_superuser = 0
            #     user.user_level = 0
            #     user.is_staff = 1
            #     user.is_active = 1
            #     user.date_joined = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
            #     if contactor:
            #         user.contacts = contactor
            #     if phone:
            #         user.phone_num = phone
            #     uId = user.id
            # print "uId %s"%uId

            print "[get_work_order_info] new cloud information"
            #云平台的相关操作
            cloud_name = rst_dict.get('cloud_name','')
            install_add = ''
            cloud_buyer = rst_dict.get('cloud_buyer','')
            contacts = rst_dict.get('contacts','')
            contact_phone = rst_dict.get('phone','')
            #以上参数可有可无

            cloudInfo = CloudInformation()
            cloudInfo.cloudName = cloud_name
            cloudInfo.installAddress = install_add
            cloudInfo.buyer = cloud_buyer
            cloudInfo.contacts = contacts
            cloudInfo.phone = contact_phone
            cloud_num = genCloudNum("BUSS")
            cloudInfo.cloudNum = cloud_num
            cloudInfo.save()
            # userObj = User.objects.get(id=int(uId))
            # print "uId get user",userObj
            # cloudInfo.cloudUser.add(userObj)

            #license相关操作,首先生成license code（新的工单号且license code信息没有，新下单的license和云平台）
            code_type = rst_dict.get("version_type", 'bdcode')                      #'bdcode':博达版本   'ztecode':ZTE版本
            license_code = genLicenseCode(code_type)
            print license_code

            licenseObj = LicenseRecord()
            licenseObj.license_code = license_code
            licenseObj.licenseType = int(license_type)                                         #表示该license的功能
            licenseObj.cloudInfo_id = cloudInfo.id
            licenseObj.expire_time = cur_time
            licenseObj.maxAps = rst_dict.get('max_ap_allowed',0)                                #该license支持的最大AP
            licenseObj.maxAcs = rst_dict.get('max_ac_allowed',0)                                #该license支持的最大AC
            licenseObj.maxUsers = rst_dict.get('max_user_allowed',0)                            #该license支持的最大User
            licenseObj.save()

            updateCodeCount(license_code)

            #创建新的工单号
            workNum = WorkOrderNum()
            workNum.license_id = licenseObj.id
            workNum.workOrderNum = work_no
            workNum.save()

            #工单物料信息的相关操作
            for each in rst_dict['license_info'] :
                woObj = WorkOrderInformation()
                woObj.materiel_name = each['productType']
                woObj.materiel_count = each['sumNo']
                woObj.materiel_type = 2
                woObj.workordernum_id = workNum.id
                woObj.save()

            for each in rst_dict['os_info']:
                woObj = WorkOrderInformation()
                woObj.materiel_name = each['productType']
                woObj.materiel_count = each['sumNo']
                woObj.materiel_type = 1
                woObj.workordernum_id = workNum.id
                woObj.save()

            for each in rst_dict['buss_info']:
                woObj = WorkOrderInformation()
                woObj.materiel_name = each['productType']
                woObj.materiel_count = each['sumNo']
                woObj.materiel_type = 3
                woObj.workordernum_id = workNum.id
                woObj.save()

            rst_dict['license_code'] = license_code
        except Exception,e:
            print e
    else:
        #扩容或者增加功能
        print "[get_work_order_info] expansion cloud information"
        rst_dict['work_type'] = 1
        licenseObj = LicenseRecord.objects.filter(license_code=license_code)

        print "license_code:",license_code
        print "license_code:",licenseObj.count()
        if licenseObj.count() >0:
            max_ap_allowed = licenseObj[0].maxAps + int(rst_dict.get('max_ap_allowed',0))
            max_ac_allowed = licenseObj[0].maxAcs + int(rst_dict.get('max_ac_allowed',0))
            max_user_allowed = licenseObj[0].maxUsers + int(rst_dict.get('max_user_allowed',0))
            licenseType = int(licenseObj[0].licenseType) | int(rst_dict.get('license_type',5))
            print rst_dict.get('license_type','9999999999')
            print licenseObj[0].key_id
            licenseObj.update(maxAps = max_ap_allowed,
                              maxAcs=max_ac_allowed,
                              maxUsers=max_user_allowed,
                              licenseType=str(licenseType))

            #工单号增加操作
            workNUm = WorkOrderNum(workOrderNum=work_no,
                                   license_id=licenseObj[0].id,
                                   product_type=rst_dict['work_type'])
            workNUm.save()

            #工单表的相关操作
            for each in rst_dict['license_info']:
                woObj = WorkOrderInformation()
                woObj.materiel_name = each['productType']
                woObj.materiel_count = each['sumNo']
                woObj.materiel_type = 2
                woObj.workordernum_id = workNUm.id
                woObj.save()

            for each in rst_dict['buss_info']:
                woObj = WorkOrderInformation()
                woObj.materiel_name = each['productType']
                woObj.materiel_count = each['sumNo']
                woObj.materiel_type = 3
                woObj.workordernum_id = workNUm.id
                woObj.save()

            rst_dict['license_code'] = license_code
            rst_dict['usbkey_id'] = licenseObj[0].key_id
        else:
            rst_dict['result'] = 5

        # workorders = workNUm.workordernum_set.all()
        # print "改license下有%s个工单"%workorders.count()
        #
        # get_materiel_name = []
        # for each in rst_dict['license_info']:
        #     get_materiel_name.append(each['productType'])
        # print "获取的全部license的物料信息为%s"%get_materiel_name
        #
        #
        # basic_lic_dict = {}
        # for each in rst_dict['license_info']:
        #     basic_lic_dict[each['productType']] = each['sumNo']
        # print "basic_lic_dict%s"%basic_lic_dict

        # for workorder in workorders:
        #     if workorder.materiel_name not in get_materiel_name:
        #         #物料信息减少，无物料license配置时数量值为零
        #         workorder.materiel_count = 0
        #         workorder.save()
        #         print "save 0 successfully"
        #     else:
        #         #物料信息更新
        #         print "原始物料个数%s"%str(workorder.materiel_count)
        #         workorder.materiel_count = basic_lic_dict.get(workorder.materiel_name)
        #         workorder.save()
        #         print "更新后物料个数%s"%str(workorder.materiel_count)
        # #物料信息增加
        # for key,value in basic_lic_dict.items():
        #     workO = WorkOrderInformation.objects.filter(
        #         materiel_name=key,
        #         workorder_id=licenseObj[0].id
        #     )
        #     if workO.count() == 0:
        #         WorkOrderInformation(workorder_id=licenseObj[0].id,
        #                       materiel_name=key,
        #                       materiel_count=value).save()
        #         print "增加一条新的记录%s,%s"%(str(key),str(value))

        #物料信息增加
        # for each in rst_dict['license_info']:
        #     for materiel_name in get_materiel_name:
        #         worO = WorkOrder.objects.filter(workorder_id = licenseObj[0].id,
        #                                         materiel_name=materiel_name)
        #         if worO.count() > 0:
        #             print "获取%s数量为%s，在数据库中有记录，更新为%s"%(str(materiel_name),str(worO[0].materiel_count),str(each['sumNo']))
        #             worO.update(materiel_count=each['sumNo'])
        #         else:
        #             print "获取%s物料信息，在数据库中没有记录，新建,数量%s"%(materiel_name,each['sumNo'])
        #             WorkOrder(workorder_id=licenseObj[0].id,
        #                       materiel_name=materiel_name,
        #                       materiel_count=each['sumNo']).save()


    print rst_dict

    return JsonResponse(rst_dict)

#激活license接口暂时摒弃，激活的接口在get_work_order_info接口中
class ActivateLicenseView(View):
    def get(self,request):
        print "in activate view"
        result = {}
        key_id = request.GET.get('key_id')
        license_code = request.GET.get('license_code')

        licenseRecords = LicenseRecord.objects.filter(license_code=license_code)
        licenseRecordObj = LicenseRecord.objects.filter(key_id=key_id)

        if licenseRecordObj.count() > 0 and licenseRecordObj[0].license_code != license_code:
            print "该key已经被 %s 激活" % str(licenseRecordObj[0].license_code)
            result['result'] = 2
            return JsonResponse(result)

        if licenseRecords.count() >0:
            licenseRecord = licenseRecords[0]
            if licenseRecord.key_id and licenseRecord.key_id != key_id:
                print "该code已经激活license，不能重复使用"
                result['result'] = 3
                return JsonResponse(result)

            #prepare response params
            # maxAPs = licenseRecord.low_counts*32+licenseRecord.mid_counts*128+licenseRecord.high_counts*1024
            # maxACs = licenseRecord.low_counts*1+licenseRecord.mid_counts*1+licenseRecord.high_counts*4
            # maxUsers = licenseRecord.low_counts*640+licenseRecord.mid_counts*2560+licenseRecord.high_counts*20480

            expire_time = licenseRecord.expire_time
            print "激活license接口，返回过期时间：",expire_time
            result['license_key'] = license_code
            result['max_ap_allowed'] = licenseRecord.maxAps
            result['max_ac_allowed'] = licenseRecord.maxAcs
            result['max_user_allowed'] = licenseRecord.maxUsers

            #expire_time format string
            str_expire_time = expire_time.strftime('%Y-%m-%d')
            print "格式化过期时间，返回字符串形式：",str_expire_time
            result['license_expire_time'] = str_expire_time

            result['result'] = 0 #validate successfully
            return JsonResponse(result)
        else:
            print "无效的license code"
            result['result'] = 1
            return JsonResponse(result)

class ModifyPasswordView(View):
    def get(self,request):
        username = request.session.get('username')
        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        all_files = request.session.get('all_files')
        if not username:
            return render(request,'license_login.html')
        context = {}
        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['all_files'] = all_files
        return render(request,'modify_password.html',context)
    def post(self,request):
        param = request.POST.copy()
        username = param['username']
        password = param['pwd1']
        userObj = User.objects.filter(username=username)
        if userObj:
            userObj[0].set_password(password)
            userObj[0].save()
            return JsonResponse({'res':1})
        else:
            print "username is not exist"
            return JsonResponse({'res':0})

class ValidateLicenseView(View):
    def get(self,request):
        print "in validate view"
        result = {}
        key_id = request.GET.get('key_id')
        license_code = request.GET.get('license_code')
        print "usb_key_hardwareId",key_id
        print "license_key",license_code
        licenseRecords = LicenseRecord.objects.filter(key_id=key_id,license_code=license_code)
        if licenseRecords.count() > 0 :
            if licenseRecords[0].license_status == LicenseRecord.CLOSE:
                result['res'] = 1 # not activated license
                return JsonResponse(result)
            else:
                result['res'] = 2 # normal license
                return JsonResponse(result)
        else:
            print "invalid license record"
            result['res'] = 0 # invalid license
            return JsonResponse(result)

# 随机生成16位的随机数

def getRandom16Num():
    timestamp = str(int(time.time()))
    nonce = ''.join(random.sample(string.digits,6))
    return  (timestamp+nonce)

class RegisterLicenseView(View):
    def get(self,request):
        print "in register view"
        uu = {}
        params = request.GET.copy()
        license_code = params['license_code']

        print "get code from cloud ",license_code
        cloud_id = request.GET.get('cloud_id','')
        if cloud_id[:4] == 'TEMP':
            #先体验试用版，现在注册正式版本，将cloud_id置为空
            cloud_id = ''
        licenses = LicenseRecord.objects.filter(license_code=license_code)
        if licenses:
            cur_time = datetime.now()
            # print "本地时间",cur_time
            cur_time = local2utc(cur_time)
            # print "UTC时间",cur_time
            ex_time = licenses[0].expire_time.replace(tzinfo=None)
            # print "数据库时间 tzinfo=None",ex_time
            # print "数据库时间",licenses[0].expire_time
            if cur_time > ex_time:
                licenses.update(is_valid=0)
                print "无效的license---已过期"
                uu['result'] = 2
                return JsonResponse(uu)
            # paramsAll = licenses[0].licenseParam.all()
            # print "params.count()",paramsAll.count()
            # max_aps = 0
            # max_acs = 0
            # max_users = 0
            # for p in paramsAll:
            #     print p
            #     print p.id,type(p.id)
            #     if int(p.id) == 1:
            #         max_aps += licenses[0].low_counts*p.maxAPs
            #         max_acs += licenses[0].low_counts*p.maxACs
            #         max_users += licenses[0].low_counts*p.maxUsers
            #         print max_aps
            #         print max_acs
            #         print max_users
            #     elif (p.id) == 2:
            #         max_aps += licenses[0].mid_counts*p.maxAPs
            #         max_acs += licenses[0].mid_counts*p.maxACs
            #         max_users += licenses[0].mid_counts*p.maxUsers
            #     elif (p.id) == 3:
            #         max_aps += licenses[0].high_counts*p.maxAPs
            #         max_acs += licenses[0].high_counts*p.maxACs
            #         max_users += licenses[0].high_counts*p.maxUsers
            # print "maxAPs=",max_aps
            # print "max_acs=",max_acs
            # print "max_users=",max_users
            license_type = licenses[0].licenseType
            new_cloud_id = licenses[0].cloudInfo.id
            if cloud_id:
                print "已注册过的云平台"
                print licenses[0].cloudInfo_id
                print int(cloud_id)
                if licenses[0].cloudInfo_id != int(cloud_id):
                    print "license的云平台和正在注册的云平台不相符"
                    uu['result'] = 6
                    return JsonResponse(uu)
                else:
                    print "该license属于该云平台"
                    if licenses[0].license_status == 1:
                        print "激活的license"
                        if licenses[0].is_valid == 0:
                            print "无效的license"
                            uu['result'] = 2
                            return JsonResponse(uu)
                        elif licenses[0].is_valid == 2:
                            print "有效license在该云平台再一次注册（包括增值版本）"
                            uu['license_type'] = license_type
                            uu['cloud_id'] = new_cloud_id
                            uu['result'] = 0
                            random_num = getRandom16Num()
                            licenses.update(random_num=random_num)
                            uu['random_num'] = random_num
                            uu['max_aps'] = licenses[0].maxAps
                            uu['max_acs'] = licenses[0].maxAcs
                            uu['max_users'] = licenses[0].maxUsers
                            # uu['max_aps'] = licenses[0].low_counts*32+licenses[0].mid_counts*128+licenses[0].high_counts*1024
                            # uu['max_acs'] = licenses[0].low_counts*1+licenses[0].mid_counts*1+licenses[0].high_counts*4
                            # uu['max_users'] = licenses[0].low_counts*640+licenses[0].mid_counts*2560+licenses[0].high_counts*20480
                            return JsonResponse(uu)
                        else:
                            print "license.is_valid not eq 0 or 2,this is impossible"
                            uu['result'] = 9
                            return JsonResponse(uu)
                    else:
                        print "未激活的license"
                        uu['result'] = 3
                        return JsonResponse(uu)
            else:
                print "未注册过的云平台，新的云平台"
                if licenses[0].license_status == 1:
                    print "激活的license"
                    if licenses[0].is_valid == 0:
                        print "无效的license"
                        uu['result'] = 2
                        return JsonResponse(uu)
                    elif licenses[0].is_valid == 2:
                        print "该license已注册--同一个license在不同的云平台注册"
                        uu['result'] = 6
                        return JsonResponse(uu)
                    else:
                        print "正常注册"
                        uu['license_type'] = license_type
                        uu['cloud_id'] = new_cloud_id
                        uu['result'] = 0
                        random_num = getRandom16Num()
                        licenses.update(random_num=random_num)
                        uu['random_num'] = random_num
                        uu['max_aps'] = licenses[0].maxAps
                        uu['max_acs'] = licenses[0].maxAcs
                        uu['max_users'] = licenses[0].maxUsers
                        # uu['max_aps'] = licenses[0].low_counts*32+licenses[0].mid_counts*128+licenses[0].high_counts*1024
                        # uu['max_acs'] = licenses[0].low_counts*1+licenses[0].mid_counts*1+licenses[0].high_counts*4
                        # uu['max_users'] = licenses[0].low_counts*640+licenses[0].mid_counts*2560+licenses[0].high_counts*20480
                        return JsonResponse(uu)
                else:
                    print "未激活的license"
                    uu['result'] = 3
                    return JsonResponse(uu)
        else:
            print "不存在的license code"
            uu['result'] = 1
            return JsonResponse(uu)

class RegisterResultView(View):
    def get(self,request):
        params = request.GET.copy()
        print params
        # key_id = params['key_id']
        result = params['result']
        license_code = params['license_code']
        if result == "0":
            licenses = LicenseRecord.objects.filter(license_code=license_code)
            print licenses.count()
            if licenses.count() > 0:
                # print type(licenses[0].licenseType.type)
                # if int(licenses[0].licenseType.type) & 1:
                #     lr = LicenseRecord.objects.filter(
                #         cloudInfo_id=licenses[0].cloudInfo_id,
                #         licenseType__type = "1",
                #         is_valid=2
                #     )
                #     if lr.count() > 0:
                #         lr.update(is_valid = 0)
                licenses.update(is_valid=2)
                return HttpResponse("0")
        else:
            print "Register failed"
            return HttpResponse("1")

class TrialRegisterLicenseView(View):
    def get(self,request):
        print "in Trial register view"
        params = request.GET.copy()
        print params,type(params)
        license_expire_time = params['license_expire_time']
        max_ap_allowed = params['max_ap_allowed']
        max_ac_allowed = params['max_ac_allowed']
        license_type = params['license_type']
        max_user_allowed = params['max_user_allowed']
        license_key = params['license_key']
        cloud_num = params['cloud_id']
        print "云平台发送试用版license过期时间为：",license_expire_time
        uu ={}

        repeatCloudObj = CloudInformation.objects.filter(cloudNum=cloud_num)
        if repeatCloudObj.count() > 0 :
            repeatLicenseObj = LicenseRecord.objects.filter(cloudInfo_id=repeatCloudObj[0].id)
            if repeatLicenseObj.count() > 0:
                print "重复试用版"
                result = 1
                uu['result'] = result
                return JsonResponse(uu)
        try:
            # paramsObj = LicenseParams()
            # paramsObj.maxACs = max_ac_allowed
            # paramsObj.maxAPs = max_ap_allowed
            # paramsObj.maxUsers = max_user_allowed
            # print "paramsObj"
            # paramsObj.save()

            # typeObj = LicenseType(type=license_type)
            # print "typeObj"
            # typeObj.save()

            cloudObj = CloudInformation(cloudNum=cloud_num)
            print "cloud num %s"%cloud_num
            cloudObj.save()

            licenseObj = LicenseRecord()
            licenseObj.license_code = license_key
            licenseObj.licenseType = license_type
            licenseObj.expire_time = license_expire_time
            licenseObj.license_status = 1
            licenseObj.is_valid = 2
            licenseObj.maxAcs = max_ap_allowed
            licenseObj.maxAcs = max_ac_allowed
            licenseObj.maxUsers = max_user_allowed

            licenseObj.cloudInfo_id = cloudObj.id
            # licenseObj.licenseParam_id = paramsObj.id
            licenseObj.save()
            result = 0
            uu['result'] = result
            return JsonResponse(uu)
        except Exception,e:
            print e

        result = 1
        uu['result'] = result
        return JsonResponse(uu)

class ValidateUserView(View):
    def get(self,request):
        print "in validate user view"
        params = request.GET.copy()
        uu = {}
        username = params['username']
        pwd = params['password']

        userSet = User.objects.filter(username=username)
        if userSet.count() == 0:
            print "no user"
            result = 0
            uu['res'] = result
            return JsonResponse(uu)

        user_pass = authenticate(username=username,password=pwd)
        if user_pass:
            if user_pass.user_level > 0:
                print "user passed and have active right"
                result = 1
                uu['res'] = result
                return JsonResponse(uu)
            else:
                print "user passed but not have right"
                result = 2
                uu['res'] = result
                return JsonResponse(uu)
        else:
            print "user and password not passed"
            result = 3
            uu['res'] = result
            return JsonResponse(uu)

class LicenseResetView(View):
    def get(self,request):
        print "in license reset"
        params = request.GET.copy()
        license_id = params['license_id']
        licenses = LicenseRecord.objects.filter(id=int(license_id))
        if licenses:
            licenses.update(is_reset=0,is_valid=1)
            return JsonResponse({"result":0})
        else:
            return JsonResponse({"result":1})


#检测license是否有效（云平台一直发请求）
class LicenseResetResultView(View):
    def get(self,request):
        print "in license reset view"
        params = request.GET.copy()
        # print params
        licenses = eval(params['license_info'])

        resultList = []
        for license in licenses:
            uu ={}
            print "in for licenses"
            license_code = license['license_key']
            cloud_id = license['cloud_id']
            license_type = license['license_type']
            random_num = license['random_num']
            print "license_code:",license_code
            licenseObj = LicenseRecord.objects.filter(license_code=license_code)
            if licenseObj:
                if cloud_id[:4] == 'TEMP':
                    #先体验试用版，现在注册正式版本，将cloud_id置为空
                    cur_time = datetime.now()
                    cur_time = local2utc(cur_time)
                    ex_time = licenseObj[0].expire_time.replace(tzinfo=None)
                    if cur_time > ex_time:
                        licenseObj.update(is_valid=0)
                        print "试用版license---已过期"
                        uu['result'] = 2
                    else:
                        uu['result'] = 3

                elif licenseObj[0].cloudInfo_id != int(cloud_id):
                    uu['result'] = 1
                elif licenseObj[0].is_reset == 0 and licenseObj[0].random_num != random_num:#重置判断
                    uu['result'] = 2
                elif licenseObj[0].is_valid == 0:
                    uu['result'] = 4
                else:
                    uu['result'] = 3
                uu['license_key'] = license_code
                uu['cloud_id'] = cloud_id
                uu['license_type'] = license_type
                resultList.append(uu)
                print "license_info:",resultList
            else:
                uu['result'] = 5
                uu['license_key'] = license_code
                uu['cloud_id'] = cloud_id
                uu['license_type'] = license_type
                resultList.append(uu)
                print "非code：license_info:",resultList
        return JsonResponse({"license_info":resultList})

def handle_download_file(path,file_name):
    if not os.path.exists(path):
        os.makedirs(path)
    file=os.path.join(path,file_name)
    down_data=[]
    if os.path.isfile(file):
        f=open(file)
        try:
            down_data=f.read()
        finally:
            f.close()
    return down_data

def download_file(request):
    user_name = request.session.get('username','')
    if not user_name:
            return render(request, 'license_login.html')

    d_file = request.GET.get('file','')
    cur_path=os.path.abspath('.')
    target_path=os.path.join(cur_path, DOWNLOAD_FILE_PATH)
    if d_file:
        try:
            d_file = d_file.encode('utf-8')
            ap_tem_data=handle_download_file(target_path,str(d_file))
            response = HttpResponse(ap_tem_data, content_type='text/plain;charset=utf-8')
            response["Content-Disposition"]="attachment; filename=%s" %d_file
            return response
        except Exception,e:
            print e
    return HttpResponse("download error!!!")

# def download_license_file(request):
#     user_name = request.session.get('username','')
#     if not user_name:
#             return render(request, 'license_login.html')
#     cur_path=os.path.abspath('.')
#     print "os.path.abspath('.')",cur_path
#     #os.path.abspath('.') /home/Portal/bdlicense/bdlicense
#     target_path=os.path.join(cur_path, DOWNLOAD_FILE_PATH)
#     print "os.path.join(cur_path, DOWNLOAD_FILE_PATH)",target_path
#     # /home/Portal/bdlicense/bdlicense/static/download_file/
#     ap_tem_data=handle_download_file(target_path,DOWNLOAD_FILE_LICENSE_CLIENT_FILE)
#     response = HttpResponse(ap_tem_data, content_type='text/plain;charset=utf-8')
#     response["Content-Disposition"]="attachment; filename=%s" %DOWNLOAD_FILE_LICENSE_CLIENT_FILE
#     return response
#
# def download_hlep_usage_file(request):
#     user_name = request.session.get('username','')
#     if not user_name:
#             return render(request, 'license_login.html')
#     cur_path=os.path.abspath('.')
#     target_path=os.path.join(cur_path, DOWNLOAD_FILE_PATH)
#     ap_tem_data=handle_download_file(target_path,DOWNLOAD_FILE_LICENSE_USAGE_FILE)
#     response = HttpResponse(ap_tem_data, content_type='application/vnd.ms-excel;charset=utf-8')
#     response["Content-Disposition"]="attachment; filename=%s" %DOWNLOAD_FILE_LICENSE_USAGE_FILE
#     return response


def genSysConf(sys_type,val):
    syss = SystemConfig.objects.filter(attribute=sys_type)
    if syss.count() > 0:
        syss.update(value=val)
        print "update ip and port sucessfully"
    else:
        sys_conf = SystemConfig(attribute=sys_type)
        sys_conf.value = val
        sys_conf.save()
        print "create ip and port successfully"

class SysConfigView(View):
    def get(self, request):
        print "[in get sys_config]"
        username = request.session.get('username')
        all_files = request.session.get('all_files')
        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')

        if not username:
            return render(request,'license_login.html')
        context = {}
        s_ips = SystemConfig.objects.filter(attribute= "server_ip")
        s_ports = SystemConfig.objects.filter(attribute= "server_port")
        if s_ips.count() > 0:
            context['server_ip'] = s_ips[0].value
        if s_ports.count() > 0:
            context['server_port'] = s_ports[0].value

        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['all_files'] = all_files
        return render(request, 'system_config.html',context)
    def post(self,request):
        print "[in post sys_config]"
        username = request.session.get('username')
        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        all_files = request.session.get('all_files')
        if not username:
            return render(request,'license_login.html')
        context = {}
        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['all_files'] = all_files

        server_ip = request.POST.get('server_ip','')
        server_port = request.POST.get('server_port','')
        try:
            # import re
            # compile_ip = re.compile("^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])"
            #                         "\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])"
            #                         "\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])"
            #                         "\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$")
            if server_ip and server_port:
                # if not compile_ip.match(server_ip):
                #     return HttpResponse("illegal ip")
                genSysConf('server_ip',server_ip)
                genSysConf('server_port',server_port)
                return JsonResponse({"result":0})
            else:
                return HttpResponse("illegal ip and port")

        except Exception,e:
            print e
        return JsonResponse({"result":1})
class or_query(View):
    def get(self, request):
        print "[in or_query]"
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        all_files = request.session.get('all_files')

        context = {}

        if is_superuser:

            work_info = WorkOrderNum.objects.all()
            context['work_info'] = work_info

        else:
            print "not superuser"
            try:
                userObj = User.objects.get(username=username)
                if userObj:
                    cloudInfos = userObj.cloudinformation_set.all()
                    tmp_list = []
                    for cloudInfo in cloudInfos:
                        licenses = LicenseRecord.objects.filter(cloudInfo_id=cloudInfo.id)
                        for license in licenses:
                            tmp_dict = {}
                            work_info = WorkOrderNum.objects.filter(license_id=license.id)
                            tmp_dict['work_num'] = work_info
                            tmp_list.append(work_info)
                    context['work_info'] = tmp_list
            except Exception,e:
                print e
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['username'] = username
        context['all_files'] = all_files

        return render(request, 'order_query.html',context)

class order_details(View):
    def get(self, request):
        print "[order_details]"
        username = request.session.get('username')
        user_level = request.session.get('user_level')
        if not username:
            return render(request,'license_login.html')

        is_superuser = request.session.get('is_superuser')
        all_files = request.session.get('all_files')
        context = {}
        wk_num = request.GET.get('wk_num','')
        print wk_num
        if wk_num:
            try:
                workorders = WorkOrderNum.objects.filter(workOrderNum=wk_num)
                print workorders[0].workOrderNum
                print workorders[0].license_id
                licenseObj = LicenseRecord.objects.filter(id=workorders[0].license_id)
                if workorders:
                    wkInfos = WorkOrderInformation.objects.filter(workordernum_id=workorders[0].id)
                    context['wkInfos'] = wkInfos
                context['licenseObj'] = licenseObj[0]
                print licenseObj[0].license_code
            except Exception,e:
                print e
        else:
            return HttpResponse("no work num, error query!!!")

        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['username'] = username
        context['all_files'] = all_files

        return render(request, 'order_details.html',context)

class TmpCloud(View):
    def get(self,request):
        print "[tmp cloud]"
        username = request.session.get('username')
        user_level = request.session.get('user_level')
        if not username:
            return render(request,'license_login.html')

        is_superuser = request.session.get('is_superuser')
        all_files = request.session.get('all_files')
        context = {}

        if is_superuser:
            licenses = LicenseRecord.objects.filter(license_code__istartswith="TEMP")
            context['licenses'] = licenses
        else:
            user = User.objects.get(username=username)
            cloudInfos = user.cloudinformation_set.filter(cloudNum__istartswith="TEMP:")
            for cloudInfo in cloudInfos:
                licenses = LicenseRecord.objects.filter(cloudInfo_id=cloudInfo.id)
                context['licenses'] = licenses
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        context['username'] = username
        context['all_files'] = all_files


        return render(request,'tmp_cloud.html',context)
