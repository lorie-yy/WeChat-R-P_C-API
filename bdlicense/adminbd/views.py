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
        context = {}
        print "cloud_id",cloud_id
        if cloud_id:
            cloudObj = CloudInformation.objects.get(id=cloud_id)
            licenseRecords = cloudObj.licenserecord_set.all()
            context['licenses'] = licenseRecords
            context['cloud_id'] = int(cloud_id)
        else:
            LicenseRecords = LicenseRecord.objects.all()
            context['licenses'] = LicenseRecords

        cloudInfos = CloudInformation.objects.all()
        context['cloudInfos'] = cloudInfos
        context['username'] = username

        return render(request, 'index.html',context)
#主页yun
class IndexViewYun(View):
    def get(self, request):
        print "in IndexYunView"
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')

        context = {}
        cloudInfos = CloudInformation.objects.all()
        context['cloudInfos'] = cloudInfos
        context['username'] = username
        return render(request, 'license_yun.html',context)

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
        username = request.session.get('username')
        if not username:
            return render(request,'license_login.html')
        context = {}
        # cloudInfos = CloudInformation.objects.all()
        # context['cloudInfos'] = cloudInfos
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

            result = 1
            uu = {'res':result}
            return JsonResponse(uu)
        except Exception,e:
            print e
        result = 0
        uu = {'res':result}
        return JsonResponse(uu)
        # return HttpResponseRedirect('add_cloud')

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
        user_pass = authenticate(username=user_name,password=password)
        print "user is passed or not"
        print user_pass
        if user_pass:
            request.session['username'] = user_name
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

        user=User.objects.get(username=username)
        user.save()
        request.session.flush()
        return HttpResponseRedirect('license_login')

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
                #expire_time format string
                str_expire_time = expire_time.strftime('%Y-%m-%d')
                result['license_expire_time'] = str_expire_time
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