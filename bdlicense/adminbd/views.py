# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from adminbd.models import LicenseRecord,CloudInformation,LicenseType,LicenseParams
from datetime import datetime

# Create your views here.
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
            license.licenseType_id = license_type
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
        context = {}
        # cloudInfos = CloudInformation.objects.all()
        # context['cloudInfos'] = cloudInfos
        cloudUsers = User.objects.all()
        context['cloudUsers'] = cloudUsers
        context['username'] = username

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

        print "in add user post func"
        params = request.POST.copy()
        print params
        user_name = params['user_name']
        sel_cloud = params['sel_cloud']
        pwd = params['pwd1']
        super_user = params['super_user']
        uu = {}
        userSet = User.objects.filter(username=user_name)
        if userSet.count() > 0 :
            print "user exists"
            result = 2
            uu = {'res':result}
            return JsonResponse(uu)
        try:
            user = User.objects.create_user(username=user_name,password="123456")
            print user
            if super_user == 0:
                user.is_superuser = 0
            else:
                user.is_superuser = 1
            user.is_staff = 1
            user.is_active = 1
            user.date_joined = datetime.now().strftime("%Y-%m-%d %H:%I:%S")
            user.save()

            userObj = User.objects.get(username=user_name)
            cloudObj = CloudInformation.objects.filter(id=int(sel_cloud))
            userObj.cloudinformation_set.add(cloudObj[0])
            userObj.save()

            # userObj = User.objects.get(username=user_name)
            # for cid in sel_cloud:
            #     cloudObj = CloudInformation.objects.filter(id=int(cid))
            #     userObj.cloudinformation_set.add(cloudObj[0])
            #     userObj.save()

            result = 1
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

                #update license key_id
                if key_id:
                    licenseRecord.key_id = key_id
                    licenseRecord.save()
                    print "update license key_id successfully"

                #modify license status
                if licenseRecord.license_status == LicenseRecord.CLOSE:
                    licenseRecord.license_status = LicenseRecord.OPEN
                    licenseRecord.save()
                    print "license status updated successfully"

                #prepare response params
                maxAPs = licenseRecord.licenseParam.maxAPs
                maxACs = licenseRecord.licenseParam.maxACs
                maxUsers = licenseRecord.licenseParam.maxUsers
                expire_time = licenseRecord.expire_time
                result['usb_key_hardwareId'] = key_id
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
        if not username:
            return render(request,'license_login.html')
        context = {}
        context['username'] = username
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