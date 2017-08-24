# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from adminbd.models import LicenseRecord,CloudInformation,LicenseType,LicenseParams
from datetime import datetime
import os.path
import logging

# Create your views here.


DOWNLOAD_FILE_PATH = "static/download_file/"
DOWNLOAD_FILE_LICENSE_CLIENT_FILE = "bdls_1.0.tar.gz"
DOWNLOAD_FILE_LICENSE_USAGE_FILE = "shop_shopadmin.sql"

#主页
class IndexView(View):
    def get(self, request):
        print "in IndexView"
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        cloud_id = request.GET.get('cloud_id')
        is_superuser = request.session.get('is_superuser')
        context = {}
        print "cloud_id",cloud_id

        if cloud_id:
            cloudObj = CloudInformation.objects.get(id=cloud_id)
            licenseRecords = cloudObj.licenserecord_set.all()
            if is_superuser:
                context['licenses'] = licenseRecords
            else:
                licenseList = []
                licenseList.append(licenseRecords)
                context['licenses'] = licenseList
            context['cloud_id'] = int(cloud_id)
        else:
            if is_superuser:
                LicenseRecords = LicenseRecord.objects.all()
                context['licenses'] = LicenseRecords
            else:
                user = User.objects.get(username=username)
                # print "user = User.objects.get(username=username)"
                user_clouds = user.cloudinformation_set.all()
                # print "user_clouds = user.cloudinformation.all()"
                licenseList = []
                for cloud in user_clouds:
                    licenses = LicenseRecord.objects.filter(id=cloud.id)
                    licenseList.append(licenses)
                    # print "licenseList.append(licenses)"
                context['licenses'] = licenseList

                for i in licenseList:
                    for j in i:
                        print j.key_id
                # print "finish!!!!!!!!!!!!!!!!!"

        cloudInfos = CloudInformation.objects.all()
        context['cloudInfos'] = cloudInfos
        context['username'] = username
        context['is_superuser'] = is_superuser

        return render(request, 'index.html',context)
#主页yun
class IndexViewYun(View):
    def get(self, request):
        print "in IndexYunView"
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')
        is_superuser = request.session.get('is_superuser')
        context = {}
        if is_superuser:
            cloudInfos = CloudInformation.objects.all()
            context['cloudInfos'] = cloudInfos
        else:
            user = User.objects.get(username=username)
            cloudInfos = user.cloudinformation_set.all()
            context['cloudInfos'] = cloudInfos

        context['username'] = username
        context['is_superuser'] = is_superuser
        return render(request, 'license_yun.html',context)

#用户主页
class UserIndexView(View):
    def get(self, request):
        print "in IndexYunView"
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        is_superuser = request.session.get('is_superuser')
        context = {}
        if is_superuser:
            userSets = User.objects.all()
            # userList = []
            # for userSet in userSets:
            #     userClouds = userSet.cloudinformation_set.all()
            #     userList.append(userClouds)
            # context['userList'] = userList
            context['userSets'] = userSets
        else:
            print "not superuser,no right to display the user list"
            return HttpResponse("No Right")

        # context['userSets'] = userSets
        context['username'] = username
        context['is_superuser'] = is_superuser
        return render(request, 'user_list.html',context)

class AddLicenseView(View):
    def get(self,request):
        username = request.session.get('username')
        is_superuser = request.session.get('is_superuser')
        if not username:
            return render(request,'license_login.html')
        print "in add license get func"

        context = {}
        licenseTypes = LicenseType.objects.all()
        context['licenseTypes'] = licenseTypes

        licenseParams = LicenseParams.objects.all()
        context['licenseParams'] = licenseParams

        cloudInfos = CloudInformation.objects.all()
        context['cloudInfos'] = cloudInfos
        context['username'] = username
        context['is_superuser'] = is_superuser

        return render(request, 'license_added.html',context)

    def post(self,request):
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        print "in add license post func"
        params = request.POST.copy()
        print params
        # key_id = params['key_id']
        license_code = params['license_code']
        license_type = params['license_type']
        licensePid = params['licensePID']#get licenseParams id to validate which licenseParamsObj
        cloud_info = params['cloud_info']
        license_time = params['license_time']

        uu = {}
        #license_code is not unique
        if license_code:
            print "license_code",license_code
            licenseRecordObj = LicenseRecord.objects.filter(license_code=license_code)
            if licenseRecordObj:
                print "license_code is not unique"
                result = 2
                uu = {'res':result}
                return JsonResponse(uu)
            else:
                print "license_code is unique"
                pass
        #format expire time
        cur_time = datetime.now()
        print cur_time
        cur_year = cur_time.year
        fut_year = cur_year+int(license_time)
        cur_time = cur_time.replace(year=fut_year)
        print cur_time

        # add new LicenseRecord
        try:
            license = LicenseRecord()
            # license.key_id = key_id
            license.license_code = license_code
            license.licenseType_id = int(license_type)
            license.cloudInfo_id = cloud_info
            license.expire_time = cur_time
            if licensePid:
                license.licenseParam_id = int(licensePid)
            license.save()
            print "save license"
            result = 1
            uu = {'res':result}
            return JsonResponse(uu)
        except Exception,e:
            print e
        result = 0
        uu = {'res':result}
        return JsonResponse(uu)


class AddCloudView(View):
    def get(self,request):
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        is_superuser = request.session.get('is_superuser')
        context = {}
        # cloudInfos = CloudInformation.objects.all()
        # context['cloudInfos'] = cloudInfos
        cloudUsers = User.objects.all()
        context['cloudUsers'] = cloudUsers
        context['username'] = username
        context['is_superuser'] = is_superuser

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

        uu = {}
        try:
            cloudinfo = CloudInformation()
            cloudinfo.cloudName = cloud_name
            cloudinfo.installAddress = install_add
            cloudinfo.buyer = cloud_buyer
            cloudinfo.contacts = contacts
            cloudinfo.phone = phone
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
        # return HttpResponseRedirect('add_cloud')

class AddUserView(View):
    def get(self,request):
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        is_superuser = request.session.get('is_superuser')
        context = {}
        cloudInfos = CloudInformation.objects.all()
        context['cloudInfos'] = cloudInfos
        # cloudUsers = User.objects.all()
        # context['cloudUsers'] = cloudUsers
        context['username'] = username
        context['is_superuser'] = is_superuser

        return render(request, 'user_added.html',context)

    def post(self,request):
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        params = request.POST.copy()
        print params
        user_name = params['user_name']
        sel_cloud = params['sel_cloud']
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
            if super_user == 0:
                user.is_superuser = 0
            else:
                user.is_superuser = 1
            user.is_staff = 1
            user.is_active = 1
            user.date_joined = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
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
        print "in IndexView"
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        user_id = request.GET.get('id')
        is_superuser = request.session.get('is_superuser')
        context = {}

        if user_id:
            userObj = User.objects.get(id=user_id)
            userCloudSets = userObj.cloudinformation_set.all()
            context['userCloudSets'] = userCloudSets
            context['userObj'] = userObj

        context['username'] = username
        context['is_superuser'] = is_superuser

        return render(request, 'cloud_user.html',context)

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

        # user=User.objects.get(username=username)
        # user.save()
        request.session.flush()
        return HttpResponseRedirect('license_login')

class UpdateKeyIDView(View):
    def get(self,request):
        params = request.GET.copy()
        key_id = params['key_id']
        license_code = params['license_code']
        #update license key_id
        licenses = LicenseRecord.objects.filter(license_code=license_code)
        licenses.update(key_id=key_id)
        print "update license key_id successfully"

        #modify license status
        licenses.update(license_status=LicenseRecord.OPEN)
        print "license status updated successfully"
        return HttpResponse("OK")

class ActivateLicenseView(View):
    def get(self,request):
        print "in activate view"
        result = {}
        key_id = request.GET.get('key_id')
        license_code = request.GET.get('license_code')
        try:
            # licenseRecord = LicenseRecord.objects.get(key_id=key_id,license_code=license_code)
            licenseRecord = LicenseRecord.objects.get(license_code=license_code)

            if licenseRecord:
                print "licenseRecord is exist by this license_code"

                if licenseRecord.key_id and licenseRecord.key_id != key_id:
                    result['result'] = False
                    return JsonResponse(result)

                #prepare response params
                if licenseRecord.licenseType.type == "1":
                    maxAPs = licenseRecord.licenseParam.maxAPs
                    maxACs = licenseRecord.licenseParam.maxACs
                    maxUsers = licenseRecord.licenseParam.maxUsers
                else:
                    maxAPs = 0
                    maxACs = 0
                    maxUsers = 0
                expire_time = licenseRecord.expire_time
                # result['usb_key_hardwareId'] = key_id
                result['license_key'] = license_code
                result['max_ap_allowed'] = maxAPs
                result['max_ac_allowed'] = maxACs
                result['max_user_allowed'] = maxUsers

                #expire_time format string
                str_expire_time = expire_time.strftime('%Y-%m-%d')
                result['license_expire_time'] = str_expire_time

                result['result'] = True #validate successfully
                return JsonResponse(result)
        except Exception, e:
            print e
        result['result'] = False #validate unsuccessfully
        return JsonResponse(result)

class ModifyPasswordView(View):
    def get(self,request):
        username = request.session.get('username')
        is_superuser = request.session.get('is_superuser')
        if not username:
            return render(request,'license_login.html')
        context = {}
        context['username'] = username
        context['is_superuser'] = is_superuser
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
import random
import string
import time
def getRandom16Num():
    timestamp = str(int(time.time()))
    nonce = ''.join(random.sample(string.digits,8))
    return  timestamp+nonce

class RegisterLicenseView(View):
    def get(self,request):
        print "in register view"
        uu = {}
        params = request.GET.copy()
        license_code = params['license_code']
        cloud_id = request.GET.get('cloud_id','')
        licenses = LicenseRecord.objects.filter(license_code=license_code)
        if licenses:
            license_type = licenses[0].licenseType.type
            new_cloud_id = licenses[0].cloudInfo.id
            if cloud_id:
                print "已注册过的云平台"
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
                            uu['license_type'] = license_type
                            uu['cloud_id'] = new_cloud_id
                            uu['result'] = 0
                            random_num = getRandom16Num()
                            licenses.update(random_num=random_num)
                            uu['random_num'] = random_num
                            return JsonResponse(uu)
                        else:
                            if license_type == "1":
                                print "有效license--基本版本---扩容"
                                basic_license = LicenseRecord.objects.filter(
                                    cloudInfo_id = licenses[0].cloudInfo_id,
                                    is_valid=2,
                                    licenseType_id=1,
                                    license_status = 1
                                )
                                if basic_license.count() > 0:
                                    basic_license.update(is_valid=0)

                            elif license_type == "2":
                                print "有效license--计费版本版本"
                                charging_license = LicenseRecord.objects.filter(
                                    cloudInfo_id = licenses[0].cloudInfo_id,
                                    is_valid=2,
                                    licenseType_id=2,
                                    license_status = 1
                                )
                                if charging_license.count() > 0:
                                    return JsonResponse({"result":5})
                            elif license_type == "4":
                                print "有效license--大数据版本"
                                analysis_license = LicenseRecord.objects.filter(
                                    cloudInfo_id = licenses[0].cloudInfo_id,
                                    is_valid=2,
                                    licenseType_id=3,
                                    license_status = 1
                                )
                                if analysis_license.count() > 0:
                                    return JsonResponse({"result":4})
                            uu['license_type'] = license_type
                            uu['cloud_id'] = new_cloud_id
                            uu['result'] = 0
                            random_num = getRandom16Num()
                            licenses.update(random_num=random_num)
                            uu['random_num'] = random_num
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
                licenses.update(is_valid = 2)
                return HttpResponse("0")
        else:
            print "Register failed"
            return HttpResponse("1")

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
            if user_pass.is_superuser:
                print "user passed and is superuser"
                result = 1
                uu['res'] = result
                return JsonResponse(uu)
            else:
                print "user passed but not superuser"
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
                if licenseObj[0].cloudInfo_id != int(cloud_id):
                    uu['result'] = 1
                elif licenseObj[0].is_reset == 0 and licenseObj[0].random_num != random_num:
                    uu['result'] = 2
                else:
                    uu['result'] = 3
                uu['license_key'] = license_code
                uu['cloud_id'] = cloud_id
                uu['license_type'] = license_type
                resultList.append(uu)
                print "license_info:",resultList
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

def download_license_file(request):
    cur_path=os.path.abspath('.')
    print "os.path.abspath('.')",cur_path
    #os.path.abspath('.') /home/Portal/bdlicense/bdlicense
    target_path=os.path.join(cur_path, DOWNLOAD_FILE_PATH)
    ap_tem_data=handle_download_file(target_path,DOWNLOAD_FILE_LICENSE_CLIENT_FILE)
    response = HttpResponse(ap_tem_data, content_type='text/plain;charset=utf-8')
    response["Content-Disposition"]="attachment; filename=%s" %DOWNLOAD_FILE_LICENSE_CLIENT_FILE
    return response

def download_hlep_usage_file(request):
    cur_path=os.path.abspath('.')
    target_path=os.path.join(cur_path, DOWNLOAD_FILE_PATH)
    ap_tem_data=handle_download_file(target_path,DOWNLOAD_FILE_LICENSE_USAGE_FILE)
    response = HttpResponse(ap_tem_data, content_type='application/vnd.ms-excel;charset=utf-8')
    response["Content-Disposition"]="attachment; filename=%s" %DOWNLOAD_FILE_LICENSE_USAGE_FILE
    return response