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
import random
import string
import time
from django.utils import timezone
import pytz
# Create your views here.


DOWNLOAD_FILE_PATH = "static/download_file/"
DOWNLOAD_FILE_LICENSE_CLIENT_FILE = "bdls_1.0.tar.gz"
DOWNLOAD_FILE_LICENSE_USAGE_FILE = "私有云License管理手册.docx"

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
                user_clouds = user.cloudinformation_set.all()
                licenseList = []
                for cloud in user_clouds:
                    licenses = LicenseRecord.objects.filter(id=cloud.id)
                    licenseList.append(licenses)
                context['licenses'] = licenseList

        cloudInfos = CloudInformation.objects.exclude(cloudName = "")
        context['cloudInfos'] = cloudInfos
        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
        print "is_superuser=",is_superuser
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
        context = {}
        if is_superuser:
            # cloudInfos = CloudInformation.objects.filter(cloudNum__istartswith = "BUSS")
            cloudInfos = CloudInformation.objects.all()
            context['cloudInfos'] = cloudInfos
        else:
            user = User.objects.get(username=username)
            cloudInfos = user.cloudinformation_set.all()
            context['cloudInfos'] = cloudInfos

        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
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
        return render(request, 'user_list.html',context)

class AddLicenseView(View):
    def get(self,request):
        username = request.session.get('username')
        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        if not username:
            return render(request,'license_login.html')
        print "in add license get func"

        context = {}
        # licenseTypes = LicenseType.objects.all()
        # context['licenseTypes'] = licenseTypes

        licenseParams = LicenseParams.objects.exclude(cloudRankName = "")
        context['licenseParams'] = licenseParams

        cloudInfos = CloudInformation.objects.exclude(cloudName = "")
        context['cloudInfos'] = cloudInfos
        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level

        if request.is_ajax():
            license_code = genLicenseCode("BUSS")
            context['code'] = license_code
            print "pro code=",license_code,context['code']
            return HttpResponse(license_code)
            # return JsonResponse({"code":license_code})
        return render(request, 'license_added.html',context)

    def post(self,request):
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        print "in add license post func"
        params = request.POST.copy()
        print params
        license_code = params['license_code']
        # licensePid = params['licensePID']
        cloud_info = params['cloud_info']
        license_time = params['license_time']
        # counts = params['counts']
        low_count = request.POST.get('low',0)
        mid_count = request.POST.get('medium',0)
        high_count = request.POST.get('high',0)
        # sel_params = request.POST.get('sel_params')
        # sel_params_list = sel_params.split(',')
        data_license = request.POST.get('data_license','')
        charging_license = request.POST.get('charging_license','')
        print "data_license=",data_license
        print "charging_license=",charging_license
        uu = {}
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
        #license_code is not unique
        licenseRecordObj = LicenseRecord.objects.filter(license_code=license_code)
        if licenseRecordObj.count() > 0:
            print "license_code is not unique"
            result = 2
            uu = {'res':result}
            return JsonResponse(uu)

        #format expire time
        cur_time = datetime.now()
        print cur_time
        cur_year = cur_time.year
        fut_year = cur_year+int(license_time)
        cur_time = cur_time.replace(year=fut_year)
        print cur_time

        # add new LicenseRecord
        try:

            licenseType = LicenseType(type="1")
            licenseType.save()
            if data_license:
                value = int(licenseType.type) | int(data_license)
                print "value=",value
                licenseType.type = value
                licenseType.save()
            if charging_license:
                value = int(licenseType.type) | int(charging_license)
                licenseType.type = value
                print "value=",value
                licenseType.save()

            license = LicenseRecord()
            license.license_code = license_code
            license.licenseType_id = licenseType.id
            license.cloudInfo_id = cloud_info
            license.expire_time = cur_time
            # if licensePid:
            #     license.licenseParam_id = int(licensePid)
            #     license.counts = counts

            # if sel_params_list:
            #     for sel_param in sel_params_list:
            #         if sel_param !=0
            #         cloudObj = CloudInformation.objects.filter(id=int(cloud_id))
            #         license.cloudinformation_set.add(cloudObj[0])
            #         license.save()
            # if low_count != 0:
            license.low_counts = low_count
            license.mid_counts = mid_count
            license.high_counts = high_count
            license.save()
            if int(low_count) != 0:
                lP = LicenseParams.objects.get(id=1)
                license.licenseParam.add(lP)
            if int(mid_count) != 0:
                mP = LicenseParams.objects.get(id=2)
                license.licenseParam.add(mP)
            if int(high_count) != 0:
                hP = LicenseParams.objects.get(id=3)
                license.licenseParam.add(hP)

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

class EditLicenseView(View):
    def get(self,request):
        username = request.session.get('username')
        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        if not username:
            return render(request,'license_login.html')
        print "in edit license get func"

        license_id = request.GET.get('id',None)
        print "license_id=",license_id
        context = {}
        if license_id is not None:
            licenseRecord = LicenseRecord.objects.get(id=int(license_id))
            params = licenseRecord.licenseParam.all()
            paramsIdList = []
            for param in params:
                paramsIdList.append(param.id)
            context['paramsIdList'] = paramsIdList
            if int(licenseRecord.licenseType.type) & 4:
                context['data_id'] = 4
                print "计费版本"
            if int(licenseRecord.licenseType.type) & 2:
                context['charging_id'] = 2
                print "大数据版本"
            context['licenseRecord'] = licenseRecord
            # print "expire_time=",licenseRecord.expire_time,type(licenseRecord.expire_time)
            # future_year = licenseRecord.expire_time.year
            # now_year = datetime.now().year
            # valid_year = future_year-now_year
            # context['valid_year'] = int(valid_year)
            # print "valid_year=",int(valid_year)
        licenseParams = LicenseParams.objects.exclude(cloudRankName = "")
        context['licenseParams'] = licenseParams

        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level


        return render(request, 'license_edit.html',context)

    def post(self,request):
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        print "in edit license post func"
        params = request.POST.copy()
        print params
        licensePid = params['licensePID']
        license_id = params['license_id']
        counts = params['counts']
        data_license = request.POST.get('data_license','')
        charging_license = request.POST.get('charging_license','')
        print "data_license=",data_license
        print "charging_license=",charging_license
        # print "license_id=",license_id
        # print "licensePid=",licensePid
        # print "counts=",counts
        uu = {}
        #one cloud has only one valid license
        try:
            licenseObj = LicenseRecord.objects.filter(id=int(license_id))
            if licenseObj.count() > 0:
                licenseObj.update(licenseParam_id=int(licensePid),counts=counts)
                type_id = licenseObj[0].licenseType.id
                typeObj = LicenseType.objects.filter(id=type_id)
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
                typeObj.update(type=value)

                # if data_license != "":
                #     data_value = int(data_license) | int(licenseObj[0].licenseType.type)
                # else:
                #     data_value = int(licenseObj[0].licenseType.type) ^ 4
                # typeObj.update(type=data_value)
                # print "after update data_value=",data_value
                # print "update data license successfully"

                # if charging_license != "":
                #     charging_value = int(charging_license) | int(licenseObj[0].licenseType.type)
                # else:
                #     charging_value = int(licenseObj[0].licenseType.type) ^ 2
                # print "before update charging_value=",charging_value
                # typeObj.update(type=charging_value)
                # print "after update charging_value=",charging_value
                # print "update charging license successfully"

                result = 0
                uu = {'res':result}
                return JsonResponse(uu)
        except Exception,e:
            print e
        result = 1
        uu = {'res':result}
        return JsonResponse(uu)

def editlicense(type_license,licenseObj):
    value = 1
    if type_license != "":
        value = int(type_license) | int(licenseObj[0].licenseType.type)
        print "add fun"
    else:
        if type_license == "data_license":
            value = int(licenseObj[0].licenseType.type) & 4
            print "dec data fun"
        elif type_license == "charging_license":
            value = int(licenseObj[0].licenseType.type) & 2
            print "dec charging fun"
    print "value=",value
    return value

class AddCloudView(View):
    def get(self,request):
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        context = {}
        cloudUsers = User.objects.all()
        context['cloudUsers'] = cloudUsers
        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level

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
            cloud_num = genLicenseCode("BUSS")
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
        print "in IndexView"
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        user_id = request.GET.get('id')
        is_superuser = request.session.get('is_superuser')
        user_level = request.session.get('user_level')
        context = {}

        if user_id:
            userObj = User.objects.get(id=user_id)
            userCloudSets = userObj.cloudinformation_set.all()
            context['userCloudSets'] = userCloudSets
            context['userObj'] = userObj

        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level

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
        context = {}
        if key_id is not None:
            licenseObj = LicenseRecord.objects.get(id=key_id)
            paramsObjs = licenseObj.licenseParam.all()
            print "paramsObjs.counts",paramsObjs.count()
            aps = 0
            acs = 0
            for paramsObj in paramsObjs:
                if paramsObj.id == 1:
                    print licenseObj.low_counts
                    print paramsObj.maxAPs
                    print paramsObj.maxAPs*licenseObj.low_counts
                    aps += paramsObj.maxAPs*licenseObj.low_counts
                    acs += paramsObj.maxACs*licenseObj.low_counts
                    print "aps=",aps
                    print "acs=",acs
                elif paramsObj.id == 2:
                    aps += paramsObj.maxAPs*licenseObj.mid_counts
                    acs += paramsObj.maxACs*licenseObj.mid_counts
                    print "aps=",aps
                    print "acs=",acs
                else:
                    aps += paramsObj.maxAPs*licenseObj.high_counts
                    acs += paramsObj.maxACs*licenseObj.high_counts
            context['aps'] = aps
            context['acs'] = acs
            context['paramsObj'] = paramsObjs
            context['code'] = licenseObj.license_code

        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level

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
            # if int(licenseRecord.licenseType.type) & 1:
            maxAPs = licenseRecord.licenseParam.maxAPs * licenseRecord.counts
            maxACs = licenseRecord.licenseParam.maxACs * licenseRecord.counts
            maxUsers = licenseRecord.licenseParam.maxUsers  * licenseRecord.counts
                # maxAPs = 288
                # maxACs = 4
                # maxUsers = 5760
            # else:
            #     maxAPs = 0
            #     maxACs = 0
            #     maxUsers = 0
            expire_time = licenseRecord.expire_time
            result['license_key'] = license_code
            result['max_ap_allowed'] = maxAPs
            result['max_ac_allowed'] = maxACs
            result['max_user_allowed'] = maxUsers

            #expire_time format string
            str_expire_time = expire_time.strftime('%Y-%m-%d')
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
        if not username:
            return render(request,'license_login.html')
        context = {}
        context['username'] = username
        context['is_superuser'] = is_superuser
        context['user_level'] = user_level
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

#license code 生成
def genLicenseCode(code_type):
    timestamp = str(int(time.time()))
    nonce = ''.join(random.sample(string.digits,6))
    code = code_type+timestamp+nonce
    return code

class RegisterLicenseView111(View):
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
                            # if license_type == "1":
                            #     print "有效license--基本版本---扩容"
                            #     basic_license = LicenseRecord.objects.filter(
                            #         cloudInfo_id = licenses[0].cloudInfo_id,
                            #         is_valid=2,
                            #         licenseType_id=1,
                            #         license_status = 1
                            #     )
                            #     if basic_license.count() > 0:
                            #         basic_license.update(is_valid=0)

                            # elif license_type == "2":
                            if license_type == "2":
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

class RegisterLicenseView(View):
    def get(self,request):
        print "in register view"
        uu = {}
        params = request.GET.copy()
        license_code = params['license_code']
        cloud_id = request.GET.get('cloud_id','')
        if cloud_id[:4] == 'TEMP':
            #先体验试用版，现在注册正式版本，将cloud_id置为空
            cloud_id = ''
        licenses = LicenseRecord.objects.filter(license_code=license_code)
        if licenses:
            cur_time = datetime.now()
            ex_time = licenses[0].expire_time.replace(tzinfo=None)
            if cur_time > ex_time:
                licenses.update(is_valid=0)
                print "无效的license---已过期"
                uu['result'] = 2
                return JsonResponse(uu)

            license_type = licenses[0].licenseType.type
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
                            uu['max_aps'] = licenses[0].licenseParam.maxAPs
                            uu['max_acs'] = licenses[0].licenseParam.maxACs
                            uu['max_users'] = licenses[0].licenseParam.maxUsers
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
                        uu['max_aps'] = licenses[0].licenseParam.maxAPs
                        uu['max_acs'] = licenses[0].licenseParam.maxACs
                        uu['max_users'] = licenses[0].licenseParam.maxUsers
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
        print "license_expire_time",license_expire_time,type(license_expire_time)
        max_ap_allowed = params['max_ap_allowed']
        max_ac_allowed = params['max_ac_allowed']
        license_type = params['license_type']
        max_user_allowed = params['max_user_allowed']
        license_key = params['license_key']
        cloud_num = params['cloud_id']
        # print "max_ap_allowed",max_ap_allowed
        # print "max_ac_allowed",max_ac_allowed
        # print "max_user_allowed",max_user_allowed
        # print "license_expire_time",license_expire_time
        # print "license_key",license_key
        # print "license_type",license_type
        # print "cloud_id",cloud_id
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
            paramsObj = LicenseParams()
            paramsObj.maxACs = max_ac_allowed
            paramsObj.maxAPs = max_ap_allowed
            paramsObj.maxUsers = max_user_allowed
            print "paramsObj"
            paramsObj.save()

            typeObj = LicenseType(type=license_type)
            print "typeObj"
            typeObj.save()

            cloudObj = CloudInformation(cloudNum=cloud_num)
            print "cloudObj"
            cloudObj.save()

            licenseObj = LicenseRecord()
            licenseObj.license_code = license_key
            licenseObj.licenseType_id = typeObj.id
            # expire_time = datetime.strptime(license_expire_time,"%Y-%m-%d %H:%M:%S")
            # print "expire_time",expire_time,type(expire_time)
            # datetime.strftime()
            licenseObj.expire_time = license_expire_time
            # print "license_expire_time",license_expire_time
            licenseObj.license_status = 1
            licenseObj.is_valid = 2
            licenseObj.cloudInfo_id = cloudObj.id
            licenseObj.licenseParam_id = paramsObj.id
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
                    # cloud_id = ''
                    cur_time = datetime.now()
                    ex_time = licenseObj[0].expire_time.replace(tzinfo=None)
                    if cur_time > ex_time:
                        licenseObj.update(is_valid=0)
                        print "试用版license---已过期"
                        uu['result'] = 2
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
    user_name = request.session.get('username','')
    if not user_name:
            return render(request, 'license_login.html')
    cur_path=os.path.abspath('.')
    print "os.path.abspath('.')",cur_path
    #os.path.abspath('.') /home/Portal/bdlicense/bdlicense
    target_path=os.path.join(cur_path, DOWNLOAD_FILE_PATH)
    ap_tem_data=handle_download_file(target_path,DOWNLOAD_FILE_LICENSE_CLIENT_FILE)
    response = HttpResponse(ap_tem_data, content_type='text/plain;charset=utf-8')
    response["Content-Disposition"]="attachment; filename=%s" %DOWNLOAD_FILE_LICENSE_CLIENT_FILE
    return response

def download_hlep_usage_file(request):
    user_name = request.session.get('username','')
    if not user_name:
            return render(request, 'license_login.html')
    cur_path=os.path.abspath('.')
    target_path=os.path.join(cur_path, DOWNLOAD_FILE_PATH)
    ap_tem_data=handle_download_file(target_path,DOWNLOAD_FILE_LICENSE_USAGE_FILE)
    response = HttpResponse(ap_tem_data, content_type='application/vnd.ms-excel;charset=utf-8')
    response["Content-Disposition"]="attachment; filename=%s" %DOWNLOAD_FILE_LICENSE_USAGE_FILE
    return response

#编辑license
class Modify_license(View):
    def get(self,request):
        username = request.GET.get('username')
        pwd = request.GET.get('pwd')
        key_id = request.GET.get('key_id')
        if username == 'bdyun' and pwd == 'bdyun':
            license = LicenseRecord.objects.filter(key_id = key_id)[0]
            return render(request, 'edit_license.html',{'license':license})
    def post(self,request):
        yuncode=request.POST.get("yuncode")
        key_id=request.POST.get("key_id")
        build_time=request.POST.get("build_time")
        is_valid=request.POST.get("is_valid")
        is_reset=request.POST.get("is_reset")
        expire_time=request.POST.get("expire_time")
        license_status=request.POST.get("license_status")
        yunname=request.POST.get("yunname")
        licenseType=request.POST.get("licenseType")
        try:
            license = LicenseRecord.objects.filter(key_id = key_id)
            license.update(
                license_status=license_status,
                is_valid=is_valid,
                is_reset=is_reset
            )
        except Exception,e:
            print e
            return JsonResponse({"result":1})
        else:
            return JsonResponse({"result":0})
