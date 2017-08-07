# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect,JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from adminbd.models import LicenseRecord,CloudInfo,LicenseType


# Create your views here.
#主页
class IndexView(View):
    def get(self, request):
        print "in IndexView"
        # username = request.session.get('username')
        # if not username:
        #     return render(request,'lisence_login.html')

        context = {}
        LicenseRecords = LicenseRecord.objects.all()
        context['licenses'] = LicenseRecords
        return render(request, 'index.html',context)
#主页yun
class IndexViewYun(View):
    def get(self, request):
        print "in IndexViewYun"
        # username = request.session.get('username')
        # if not username:
        #     return render(request,'lisence_login.html')

        context = {}
        LicenseRecords = LicenseRecord.objects.all()
        context['licenses'] = LicenseRecords
        return render(request, 'license_yun.html',context)

class AddLicenseView(View):
    def get(self,request):
        # username = request.session.get('username')
        # if not username:
        #     return render(request,'lisence_login.html')
        context = {}
        licenseTypes = LicenseType.objects.all()
        context['licenseTypes'] = licenseTypes
        return render(request, 'license_added.html',context)

    def post(self,request):
        key_id = request.POST.get("key_id",'')
        license_code = request.POST.get("license_code",'')
        license_type = request.POST.get("license_type",'1')
        max_ap = request.POST.get("max_aps")
        max_ac = request.POST.get("max_acs")
        max_user = request.POST.get("max_users")
        print "print data from html and js"
        print key_id
        print license_code
        print license_type
        print max_ap
        print max_ac
        print max_user
        uu = {}
        try:
            cloudinfo = CloudInfo()
            cloudinfo.maxACs = max_ac
            cloudinfo.maxAPs = max_ap
            cloudinfo.maxUsers = max_user
            cloudinfo.save()

            license = LicenseRecord()
            license.key_id = key_id
            license.license_code = license_code
            license.licensetype.type = license_type
            license.cloudInfo = cloudinfo
            #default 0,try not the underline
            # license.license_status = license.CLOSE
            license.save()

            result = 1
            uu = {'res',result}
            return HttpResponse(uu)
        except Exception,e:
            print e
        return HttpResponseRedirect('add_license')

class AddLicenseYunView(View):
    def get(self,request):
        # username = request.session.get('username')
        # if not username:
        #     return render(request,'lisence_login.html')
        context = {}
        licenseTypes = LicenseType.objects.all()
        context['licenseTypes'] = licenseTypes
        return render(request, 'license_addyun.html',context)

    def post(self,request):
        key_id = request.POST.get("key_id",'')
        license_code = request.POST.get("license_code",'')
        license_type = request.POST.get("license_type",'1')
        max_ap = request.POST.get("max_aps")
        max_ac = request.POST.get("max_acs")
        max_user = request.POST.get("max_users")
        print "print data from html and js"
        print key_id
        print license_code
        print license_type
        print max_ap
        print max_ac
        print max_user
        uu = {}
        try:
            cloudinfo = CloudInfo()
            cloudinfo.maxACs = max_ac
            cloudinfo.maxAPs = max_ap
            cloudinfo.maxUsers = max_user
            cloudinfo.save()

            license = LicenseRecord()
            license.key_id = key_id
            license.license_code = license_code
            license.licensetype.type = license_type
            license.cloudInfo = cloudinfo
            #default 0,try not the underline
            # license.license_status = license.CLOSE
            license.save()

            result = 1
            uu = {'res',result}
            return HttpResponse(uu)
        except Exception,e:
            print e
        return HttpResponseRedirect('add_license_yun')

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
                #modify license status
                if licenseRecord.license_status == LicenseRecord.CLOSE:
                    licenseRecord.license_status = LicenseRecord.OPEN
                    licenseRecord.save()
                #prepare response params
                maxAPs = licenseRecord.cloudInfo.maxAPs
                maxACs = licenseRecord.cloudInfo.maxACs
                maxUsers = licenseRecord.cloudInfo.maxUsers
                expire_time = licenseRecord.expire_time
                result['maxAPs'] = maxAPs
                result['maxACs'] = maxACs
                result['maxUsers'] = maxUsers
                result['expire_time'] = expire_time

                result['res'] = True #validate successfully
                return JsonResponse(result)
        except Exception, e:
            print e
        result['res'] = False #validate unsuccessfully
        return JsonResponse(result)

        # licenseRecord = LicenseRecord.objects.filter(key_id=key_id,license_code=license_code)
        # if licenseRecord.count() > 0:
        #     print "license record exits based on key_id and license_code given"
        #     licenseObj = licenseRecord[0]
        #     if licenseObj.license_status == LicenseRecord.CLOSE:
        #         licenseObj.license_status = LicenseRecord.OPEN
        #         licenseObj.save()
        #     maxAPs = licenseObj.cloudInfo.maxAPs
        #     maxACs = licenseObj.cloudInfo.maxACs
        #     maxUsers = licenseObj.cloudInfo.maxUsers
        #     expire_time = licenseObj.expire_time
        #     result['maxAPs'] = maxAPs
        #     result['maxACs'] = maxACs
        #     result['maxUsers'] = maxUsers
        #     result['expire_time'] = expire_time
        #     result['key_id'] = key_id
        #     result['license_code'] = license_code
        #     result['res'] = True
        #     return JsonResponse(result)
        # else:
        #     print "the key_id or license_code not exits"
        #     result['res'] = False
        #     return JsonResponse(result)

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