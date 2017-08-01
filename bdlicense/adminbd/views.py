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
        return render(request,'index.html',context)

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
def lisence_login(request):
    if request.method == "GET":
        return render(request, 'adminbd/license_login.html')

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
        # user_name = request.session.get('username')
        # if not user_name:
        #     return render(request,'adminbd/license_login.html')
        print "in activate view"
        result = {}
        license_id = request.GET.get('id')
        print "get license id",license_id
        licenseRecord = LicenseRecord.objects.filter(id=int(license_id))
        if licenseRecord.count() > 0:
            licenseRecord[0].license_status = 1
            licenseRecord[0].save()
            # return HttpResponseRedirect('index')
            return HttpResponseRedirect('license_details?id='+str(licenseRecord[0].id))
        # LicenseRecords = LicenseRecord.objects.all()
        # result['licenses'] = LicenseRecords
        # return render(request,'index.html',result)
        # else:
        #     print "no license"
        #     result['res'] = 0
        #     return JsonResponse(result)