# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from adminbd.models import LicenseRecord,CloundInformation,LicenseType,LicenseParams
from datetime import datetime

# Create your views here.
#主页
class IndexView(View):
    def get(self, request):
        print "in IndexView"
        # username = request.session.get('username')
        # if not username:
        #     return render(request,'lisence_login.html')

        cloud_id = request.GET.get('cloud_id')
        context = {}
        print "cloud_id",cloud_id
        if cloud_id:
            cloudObj = CloundInformation.objects.get(id=cloud_id)
            licenseRecords = cloudObj.licenserecord_set.all()
            print "licenseRecords.count():"
            print licenseRecords.count()
            context['licenses'] = licenseRecords
            context['cloud_id'] = int(cloud_id)
        else:
            LicenseRecords = LicenseRecord.objects.all()
            context['licenses'] = LicenseRecords

        cloudInfos = CloundInformation.objects.all()
        context['cloudInfos'] = cloudInfos

        return render(request, 'index.html',context)
#主页yun
class IndexViewYun(View):
    def get(self, request):
        print "in IndexYunView"
        # username = request.session.get('username')
        # if not username:
        #     return render(request,'lisence_login.html')

        context = {}
        cloudInfos = CloundInformation.objects.all()
        context['cloudInfos'] = cloudInfos
        return render(request, 'license_yun.html',context)

class AddLicenseView(View):
    def get(self,request):
        # username = request.session.get('username')
        # if not username:
        #     return render(request,'lisence_login.html')
        print "in add license get func"

        context = {}
        licenseTypes = LicenseType.objects.all()
        context['licenseTypes'] = licenseTypes

        licenseParams = LicenseParams.objects.all()
        context['licenseParams'] = licenseParams

        cloudInfos = CloundInformation.objects.all()
        context['cloudInfos'] = cloudInfos

        return render(request, 'license_added.html',context)

    def post(self,request):
        print "in add license post func"
        params = request.POST.copy()
        print params
        key_id = params['key_id']
        license_code = params['license_code']
        license_type = params['license_type']
        licensePid = params['licensePID']#get licenseParams id to validate which licenseParamsObj
        cloud_info = params['cloud_info']
        license_time = params['license_time']


        cur_time = datetime.now()
        print cur_time
        cur_year = cur_time.year
        fut_year = cur_year+int(license_time)
        cur_time = cur_time.replace(year=fut_year)
        print cur_time

        uu = {}
        try:
            license = LicenseRecord()
            license.key_id = key_id
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
        # username = request.session.get('username')
        # if not username:
        #     return render(request,'lisence_login.html')
        # context = {}
        # cloudInfos = CloundInformation.objects.all()
        # context['cloudInfos'] = cloudInfos
        return render(request, 'license_addyun.html')

    def post(self,request):
        print "in add cloud post func"
        params = request.POST.copy()
        print params
        cloud_name = params['cloud_name']
        install_add = params['install_add']
        cloud_buyer = params['cloud_buyer']
        contacts = params['contacts']
        phone = params['phone']

        uu = {}
        try:
            cloudinfo = CloundInformation()
            cloudinfo.cloudName = cloud_name
            cloudinfo.installAddress = install_add
            cloudinfo.buyer = cloud_buyer
            cloudinfo.contacts = contacts
            cloudinfo.phone = phone
            cloudinfo.save()

            result = 1
            uu = {'res':result}
            return JsonResponse(uu)
        except Exception,e:
            print e
        result = 0
        uu = {'res':result}
        return JsonResponse(uu)
        # return HttpResponseRedirect('add_cloud')


# 判断是否登录
def is_login(request):
    uName_NoId = request.session.get('username', False)
    user_name = request.session.get('user_name', False)
    shop_id = request.session.get('shop_id', False)
    if user_name and uName_NoId:
        loginUsers=User.objects.filter(username=user_name)
        if loginUsers.count()>0:
            loginUser=loginUsers[0]
        else:
            print("error!loginUser's count is [%d]" % (loginUsers.count()))
            loginUser=User()
    else:
        loginUser=User()
    return (uName_NoId,user_name, shop_id, loginUser )

#lisence 登陆
@csrf_exempt
def license_login(request):
    if request.method == "GET":
        return render(request, 'license_login.html')
    if request.method == "POST":
        user_name = request.POST.get('username')
        password = request.POST.get('password')
        result = {}
        user_pass = authenticate(username=user_name,password=password)
        if user_pass:
            request.session['username'] = user_name
            result['res'] = 1
            return JsonResponse(result)
        else:
            result['res'] = 0
            return JsonResponse(result)


#lisence 注册
@csrf_exempt
def license_register(request):
    if request.method == 'GET':
        return render(request, 'adminbd/license_login.html')
    if request.method == 'POST':
        user_name = request.POST.get('username')
        password = request.POST.get('paw1')
        result = {}
        same_user = User.objects.filter(username=user_name)

        if same_user.count() > 0:
            result['res'] = 0
            return JsonResponse(result)
        else:
            new_user = User()
            new_user.username = user_name
            new_user.password = password
            new_user.save()
            result['res'] = 1
            return JsonResponse(result)

        # res = 0
        # if same_user.count() == 0:
        #         new_user = User.objects.create_user(username=user_name,
        #                                             password=password)
        #         new_user.is_active=1
        # else:
        #     new_user = new_user[0]
        #     new_user.set_password(password)
        #
        # new_user.save()
        # res = 1
        # result['res'] = res
        # return JsonResponse(result)
class ActivateLicenseView(View):
    def get(self,request):
        print "in activate view"
        result = {}
        key_id = request.GET.get('key_id')
        license_code = request.GET.get('license_code')
        try:
            licenseRecord = LicenseRecord.objects.get(key_id=key_id,license_code=license_code)

            if licenseRecord:
                print "have licenseRecord"
                #modify license status
                if licenseRecord.license_status == LicenseRecord.CLOSE:
                    licenseRecord.license_status = LicenseRecord.OPEN
                    licenseRecord.save()
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
                result['license_expire_time'] = expire_time

                result['result'] = True #validate successfully
                return JsonResponse(result)
        except Exception, e:
            print e
        result['result'] = False #validate unsuccessfully
        return JsonResponse(result)

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