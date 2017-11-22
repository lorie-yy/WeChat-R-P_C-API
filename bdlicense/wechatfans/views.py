# -*- coding: UTF-8 -*-
import hashlib
import json
import datetime
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.contrib.auth import authenticate
import requests
import simplejson
from adminbd.models import SystemConfig
from wechatfans.models import TwechatOffline, ApplyforWithdrawalRecords, shop_discountinfo

from adminbd.models import CloudInformation
from wechatfans.models import TwechatOffline, ThridPartyConfig, CloudConfig, cloudtouser
import time

def md5(str):
    import hashlib
    m = hashlib.md5()
    m.update(str)
    return m.hexdigest()

class TAuthdata(View):
    '''
    跳转到吸粉页面
    '''
    def get(self,request):

        cloudid = request.GET.get('cloudid','')
        # shopid = request.GET.get('shopid','')
        wechatsign = request.GET.get('wechatsign','')
        timestamp = request.GET.get('timestamp','')
        extend = request.GET.get('extend','')
        wechatAuthvalue = request.GET.get('wechatAuthvalue','')
        mac = request.GET.get('mac','')
        bmac = request.GET.get('bmac','')
        wlanacport = request.GET.get('wlanacport','')
        portocol = request.GET.get('portocol','')
        authUrl = request.GET.get('authUrl','')
        newwechatsign = md5('df2424efb7548eaa'+extend+timestamp+authUrl+mac+wechatAuthvalue+bmac+wlanacport+portocol)
        print newwechatsign,wechatsign
        if wechatsign == newwechatsign:#核对签名
            newtimestamp = (int(time.time() * 1000))
            timestamp = int(timestamp)
            if (newtimestamp - timestamp)/60000 < 5:#五分钟内有效
                cloudconfig = CloudConfig.objects.filter(cloudid=cloudid)
                if cloudconfig.count() > 0:
                    context={}
                    context['url'] = cloudconfig[0].thirdpart.url

                    if cloudconfig[0].thirdpart.type == '1':#bigwifi
                        context['mac'] = mac
                        context['bmac'] = bmac
                        context['wlanacport'] = wlanacport
                        context['portocol'] = portocol
                        context['authUrl'] = authUrl

                    return render(request,'wechatfans/transition.html',context)
        return HttpResponse('签名失败')

class Getfansnumber(View):
    '''
    接收私有云的查询请求，并调用bigwifi的接口，获取用户关注与否的信息并返回给私有云
    '''
    def get(self,request):
        _keys = request.GET.keys()
        result = {}
        result['error']='1'
        cloudid = request.GET.get('cloudid','')
        shopid = request.GET.get('shop_id',0)
        usermac = request.GET.get('usermac','')
        type = request.GET.get('type','')
        oid = request.GET.get('oid','')
        openid = request.GET.get('openid','')

        ssid = request.GET.get('ssid','')
        nasid = request.GET.get('nasid','')
        wlanuserip = request.GET.get('wlanuserip','')
        wlanacip = request.GET.get('wlanacip','')
        wlanapmac = request.GET.get('wlanapmac','')
        timestamp = request.GET.get('timestamp','')
        stringparm=[]
        for key in _keys:
            if key != 'sign':
                stringparm.append(key+'='+unicode(request.GET[key]))
        stringparm.append('key=1qazxsw23edcvfr4')
        newsign = self.direct_sign_md5(stringparm)
        sign = request.GET.get('sign','')

        if newsign == sign:
            newtimestamp = (int(time.time() * 1000))
            timestamp = int(timestamp)
            print newtimestamp,timestamp
            if (newtimestamp - timestamp)/60000 < 5:#五分钟内有效
                cloud = CloudConfig.objects.filter(cloudid=cloudid)
                if cloud.count() > 0:
                    type = cloud[0].thirdpart.type
                userlist = TwechatOffline.objects.filter(orderid=oid,openid=openid)
                if userlist.count() == 0:
                    userlist = TwechatOffline(orderid=oid,
                                              openid=openid,
                                              shopid=int(shopid),
                                              usermac=usermac,
                                              apmac=wlanapmac,
                                              type=type,
                                              cloudid=cloudid)
                else:
                    userlist.update(shopid=int(shopid),cloudid=cloudid)
                    userlist = userlist[0]
                url = 'http://api.weifenshi.cn/Channel/whether?channelid=1443&oid='+oid+'&openid='+openid
                response = requests.get(url)
                text = eval(response.text)
                print '[INFO] result:',text
                if text["error"] in [0,'0']:
                    if text['subscribe'] in [0,'0']:
                        userlist.subscribe='0'
                        result['subscribe']='0'
                        result['error']='0'
                    else:
                        userlist.subscribe='1'
                        result['subscribe']='1'
                        result['error']='0'
                    userlist.save()
        return HttpResponse(json.dumps(result))
    def direct_sign_md5(self,parameters):
        s = '&'.join(sorted(parameters))
        m = hashlib.md5()
        m.update(s.encode('utf-8'))
        return "".join("{:02x}".format(ord(c)) for c in m.digest())

class Sub_detail(View):
    '''
    功能：调用bigwifi查询关注数据接口
    '''
    def get(self,request):
        print '[INFO] call Sub_detail'
        import time
        url = 'https://api.weifenshi.cn/api/sub_detail'
        now = datetime.datetime.now().strftime('%Y-%m-%d')
        # date = (datetime.datetime.now() - datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
        startdate = datetime.datetime.strptime('2017-03-03','%Y-%m-%d')
        enddate = now
        page = 1
        page_size = 100
        t =  int(time.time())
        apis = md5('yft_6l4twiir4jms87w4'+'_'+str(t))

        context ={}
        context['sd']=startdate
        context['ed']=enddate
        context['page']=page
        context['page_size']=page_size
        context['bid']=1443
        context['t']=t
        context['apis']=apis
        response = requests.get(url,params=context)
        text = eval(response.text)
        if text['error'] in [0,'0']:
            page_count = text['page_count']       #总页数
            page = text['page']                   #当前页
            page_size = text['page_size']         #每页数量
            cur_page_size = text['cur_page_size'] #当前页面数量
            self.saveinfo(text['list'])
            if int(page_count)>int(page):
                for i in range(2,int(page_count)+1):
                    context['page']=i
                    response_page = requests.get(url,params=context)
                    text_page = eval(response_page.text)
                    if text_page['error'] in [0,'0']:
                        self.saveinfo(text_page['list'])

        return HttpResponse("OK")


    def saveinfo(self,infolist):
        for item in infolist:
            orderid = item['oid']
            usermac = item['mac']
            apmac = item['bmac']
            openid = item['openid']
            price = item['price']
            sub_time = item['sub_time']
            gh_name = item['gh_name']
            usermac = ':'.join([usermac[i:i + 2] for i in range(0, len(usermac), 2)])
            apmac = ':'.join([apmac[i:i + 2] for i in range(0, len(apmac), 2)])
            userobject = TwechatOffline.objects.filter(openid=openid,
                                          orderid=orderid,
                                          )
            if userobject.count() > 0:
                userobject.update(price=price,gh_name=gh_name,settlement='1',apmac=apmac,authtime=sub_time)
            else:
                to = TwechatOffline(openid=openid,
                                   orderid=orderid,
                                   usermac=usermac,
                                   apmac=apmac,
                                   price=price,
                                   gh_name=gh_name,
                                   authtime=sub_time,
                                   subscribe='1',
                                   settlement='1',
                                   type='1',
                               )
                to.save()

def showfans(request):
    path_url=request.build_absolute_uri('/wechatfans/sub_detail')
    print 'path_url',path_url
    requests.get(path_url)
    username = request.session.get('username','')
    user_type = request.session.get('user_type','')
    print 'user_type',user_type
    if not username or user_type==0:
        return render(request,'license_login.html')
    cloudid = request.session.get('sc_cloudid')
    shopid = request.session.get('sc_shopid')
    startdate=datetime.datetime.now().strftime('%Y-%m-%d')
    startDate = datetime.datetime(int(startdate[:4]), int(startdate[5:7]), int(startdate[8:10]), 0, 0,0)
    endDate = datetime.datetime(int(startdate[:4]), int(startdate[5:7]), int(startdate[8:10]), 23, 59,59)
    # endDate = datetime.datetime(int(startDate[:4]), int(startDate[5:7]), int(startDate[8:10]), 23, 59,59)
    print startDate
    print endDate
    context ={}
    # 调用函数
    totalprofit,totalfans=earnings(cloudid,shopid,'','')
    todayprofit,todayfans=earnings(cloudid,shopid,startDate,endDate)
    takemoney=support_takemoney(cloudid,shopid)

    context['cloudid']=cloudid
    context['shopid']=shopid
    context['username']=username
    context['todayprofit']=todayprofit/100.00
    context['totalprofit']=totalprofit/100.00
    context['totalfans']=totalfans
    context['todayfans']=todayfans
    context['takemoney']=takemoney/100.00
    # return HttpResponse(json.dumps(context))
    return render(request, 'wechatfans/showfans.html',context)

# 计算收益量和粉丝量
def earnings(cloudid,shopid,startDate,enddate):
    if (not startDate) and (not enddate):
        userobject = TwechatOffline.objects.filter(cloudid=cloudid,
                                          shopid=shopid
                                          )
    else:
        userobject = TwechatOffline.objects.filter(cloudid=cloudid,
                                          shopid=shopid,
                                        authtime__range=(startDate,enddate)
                                          )
    print userobject
    # 用户权限收益打折扣
    shop_discount=shop_discountinfo.objects.filter(cloudid=cloudid,shopid=shopid)
    discountlist=SystemConfig.objects.filter(attribute='discount')
    if shop_discount.count()==0:
        if discountlist.count()==0:
            discount=0.9
        else:
            discount=discountlist[0].value
    else:
        discount=shop_discount[0].discount

    profit=0
    for item in userobject:
        # print 'usermac',item.id
        # print 'usermac',item.price
        profit += int(float(item.price)*100)
    profit_dis=int(profit*float(discount))
    print 'profit_dis',profit_dis

    return profit_dis,userobject.count()

# 可提现金额
def support_takemoney(cloudid,shopid):
    userobject = TwechatOffline.objects.filter(cloudid=cloudid,shopid=shopid,settlement=1)
    # 用户权限收益打折扣
    discountlist=SystemConfig.objects.filter(attribute='discount')
    if discountlist.count()==0:
        discount=0.9
    else:
        discount=discountlist[0].value
    profit=0
    for item in userobject:
        # print 'usermac',item.id
        # print 'usermac',item.price
        profit += int(float(item.price)*100)
    profit_dis=int(profit*float(discount))
    return profit_dis

def takemoney(request):
    username = request.session.get('username','')
    user_type = request.session.get('user_type','')
    if not username or user_type==0:
        return render(request,'license_login.html')
    cloudid = request.session.get('sc_cloudid')
    shopid = request.session.get('sc_shopid')
    takemoney=support_takemoney(cloudid,shopid)
    context ={}
    context['cloudid']=cloudid
    context['shopid']=shopid
    context['username']=username
    context['takemoney']=takemoney/100.00
    return render(request, 'wechatfans/takemoney.html',context)

# 创建取款记录
@csrf_exempt
def apply_for_withdrawal(request):
    username = request.session.get('username','')
    user_type = request.session.get('user_type','')
    if not username or user_type==0:
        return render(request,'license_login.html')
    cloudid = request.session.get('sc_cloudid')
    shopid = request.session.get('sc_shopid')
    paymentmode = request.POST.get('paymentmode')
    getmoney = (float(request.POST.get('getmoney')))
    getmoney = int(getmoney*100)
    # 支付宝
    alipay_name = request.POST.get('alipay_name')
    alipaynum = request.POST.get('alipaynum')
    # 银行卡
    company = request.POST.get('company')
    bank_name = request.POST.get('bank_name')
    banknum = request.POST.get('banknum')
    # 如果记录中有可转账状态,则不允许再次申请
    history=ApplyforWithdrawalRecords.objects.filter(cloudid=cloudid,shopid=shopid,paymentresult=103)
    if history.count()>0:
        result=2
    else:
        # 创建表的实例对象(取款记录)
        applyrecords = ApplyforWithdrawalRecords(paymentresult=103)
        applyrecords.cloudid = cloudid
        applyrecords.shopid = shopid
        applyrecords.username = username
        applyrecords.paymentmode = paymentmode
        applyrecords.getmoney = getmoney
        applyrecords.alipay_name = alipay_name
        applyrecords.alipaynum = alipaynum
        applyrecords.company = company
        applyrecords.bank_name = bank_name
        applyrecords.banknum = banknum
        applyrecords.save()
        result = 1

    context ={}
    context['result']=result
    print result
    return JsonResponse({'result':result})

# 申请提现记录
def applyfor_records(request):
    username = request.session.get('username','')
    user_type = request.session.get('user_type','')
    if not username or user_type==0:
        return render(request,'license_login.html')
    cloudid = request.session.get('sc_cloudid')
    shopid = request.session.get('sc_shopid')
    records=ApplyforWithdrawalRecords.objects.filter(cloudid=cloudid,shopid=shopid)
    context ={}
    context['records']=records
    context['username']=username
    recordslist=[]

    if records.count()==0:
        print '无记录'
    else:
        for record in records:
            # context['record']=record
            tempdict={}
            id = record.id
            cloudname = record.cloudname
            username = record.username
            paymentmode = record.paymentmode
            applyfortime = record.applyfortime
            alipaynum = record.alipaynum
            banknum = record.banknum
            getmoney = record.getmoney
            paymentresult = record.paymentresult

            tempdict['id']=id
            tempdict['cloudname']=cloudname
            tempdict['username']=username
            tempdict['applyfortime']=applyfortime
            tempdict['paymentmode']=paymentmode
            tempdict['alipaynum']=alipaynum
            tempdict['banknum']=banknum
            tempdict['getmoney']=getmoney/100.00
            tempdict['paymentresult']=paymentresult
            recordslist.append(tempdict)

    # 成功提现总计
    totalsuc=0
    suc=ApplyforWithdrawalRecords.objects.filter(cloudid=cloudid,shopid=shopid,paymentresult=101)
    if suc.count()==0:
        print '成功提现总计为0'
    else:
        for i in suc:
            totalsuc += i.getmoney
            print '成功提现总计为',totalsuc
    context['totalsuc']=totalsuc/100.00
    context['recordslist']=recordslist
    return render(request, 'wechatfans/applyfor_records.html',context)

# 关闭申请
def closerecord(request):
    username = request.session.get('username','')
    user_type = request.session.get('user_type','')
    context ={}
    if not username or user_type==0:
        return render(request,'license_login.html')
    try:
        id = request.GET.get('id')
        record=ApplyforWithdrawalRecords.objects.filter(id=id)
        record.update(paymentresult=102)
        print '***************record',record
        result=1
        context['result']=result
        print result

    except Exception,e:
        result=2
        context['result']=result
    # return JsonResponse({'result':result})
    return render(request, 'wechatfans/applyfor_records.html',context)

def getThirdpartInfo(request):
    Thridpartlist = ThridPartyConfig.objects.all()
    resultlist = []
    for item in Thridpartlist:
        tempdict = {}
        tempdict["id"]=item.id
        tempdict["name"]=item.thirdpartname
        tempdict["url"]=item.url
        tempdict["type"]=item.type
        resultlist.append(tempdict)
    return HttpResponse(json.dumps(resultlist))
def saveThirdpartInfo(request):
    name = request.GET.get('name')
    url = request.GET.get('url')
    type = request.GET.get('type','0')
    id = request.GET.get('id',-1)
    operationtype = request.GET.get('typeThird','')
    print name,url,operationtype
    result = {}
    result['error']=1

    iteminfo = ThridPartyConfig.objects.filter(id = id)
    try:
    # if True:
        if operationtype == 'edit':
            if iteminfo.count() == 0:
                result['error']=1
            else:
                iteminfo.update(thirdpartname = name,url=url,type=type)
                result['error']=0
        elif operationtype == 'add':
            if iteminfo.count() == 0:
                iteminfo = ThridPartyConfig(thirdpartname = name,url=url,type=type)
                iteminfo.save()
                result['error']=0
            else:
                result['error']=3
        elif operationtype == 'del':
            if iteminfo.count() == 0:
                result['error']=4
            else:
                iteminfo.delete()
                result['error']=0

    except Exception,e:
        result['error']=2
    return HttpResponse(json.dumps(result))

def getCloudname(request):
    cloudinfo = CloudInformation.objects.all()
    cloudinfolist = []
    for item in cloudinfo:
        itemdict = {}
        itemdict['cloudname']=item.cloudName
        itemdict['cloudid']=item.cloudNum
        cloudinfolist.append(itemdict)
    return HttpResponse(json.dumps(cloudinfolist))

def saveCloudconfig(request):
    cloudname = request.GET.get('cloudname','null')
    cloudid = request.GET.get('cloudid')
    thirdpartname = request.GET.get('thirdpart')
    result = {}
    result['error']=1
    iteminfo = CloudConfig.objects.filter(cloudid=cloudid)
    thirdpart = ThridPartyConfig.objects.filter(thirdpartname = thirdpartname)
    try:
    # if True:
        if iteminfo.count() == 0:
            iteminfo = CloudConfig(cloudname = cloudname,thirdpart=thirdpart[0],cloudid=cloudid)
            iteminfo.save()
            result['error']=0
        else:
            iteminfo.update(thirdpart=thirdpart[0])
            result['error']=0
    except Exception,e:
        result['error']=2
    return HttpResponse(json.dumps(result))

def getCloudConfig(request):
    cloudconfiginfo = CloudConfig.objects.all()
    cloudinfolist = []
    for item in cloudconfiginfo:
        itemdict = {}
        itemdict['cloudname']=item.cloudname
        itemdict['cloudid']=item.cloudid
        itemdict['thirdpart_name']=item.thirdpart.thirdpartname
        cloudinfolist.append(itemdict)
    return HttpResponse(json.dumps(cloudinfolist))


class Register(View):
    # @csrf_exempt
    def get(self,request):
        user_name = request.GET.get('username')
        password = request.GET.get('password')
        cloudid = request.GET.get('cloudid')
        shopid = request.GET.get('shopid')
        super_user = request.GET.get('super_user',0)

        userSet = User.objects.filter(username=user_name)
        if userSet.count() > 0:
            print "user exists"
            result = 2
            uu = {'res':result}
            return JsonResponse(uu)

        try:
            user = User.objects.create_user(username=user_name,password=password,user_type = 1)
            print "create new user"
            print user
            if super_user == 1:
                user.is_superuser = 1
            else:
                user.is_superuser = 0
            user.user_level = super_user


            clouduser = cloudtouser.objects.filter(cloudid=cloudid,shopid=shopid)
            #add cloud admin
            if clouduser.count() == 0:
                # auth_user表
                user = User.objects.create_user(username=user_name,password=password,user_type = 1)
                print "create new user and inital pwd is 123456"
                print user
                if super_user == 1:
                    user.is_superuser = 1
                else:
                    user.is_superuser = 0
                user.user_level = super_user

                user.is_staff = 1
                user.is_active = 1
                user.date_joined = datetime.datetime.now().strftime("%Y-%m-%d %H:%I:%S")

                #cloud_user表
                co = cloudtouser(username=user_name,password=password,cloudid=cloudid,shopid=shopid)
                co.save()
                result = 0
                uu = {'res':result}
                return JsonResponse(uu)
            else:
                result = 1
                uu = {'res':result}
                return JsonResponse(uu)
        except Exception,e:
            print e
        result = 3
        # uu = {'res':result}
        # return JsonResponse(uu)
        return render(request, 'wechatfans/register.html',{'res':result})



# 退出登录
@csrf_exempt
def logout(request):
    if request.method == "GET":
        username = request.session.get('username','')
        user_type = request.session.get('user_type','')
        if not username or user_type==0:
            return render(request,'license_login.html')
        request.session.flush()
        return render(request,'license_login.html')

# 修改密码
@csrf_exempt
def modify_password(request):
    username = request.session.get('username','')
    user_type = request.session.get('user_type','')
    uu = {'username': username}
    if not username or user_type==0:
        return render(request,'license_login.html')
    if request.method == 'POST':
        username = request.session['username']
        password = request.POST.get('password')
        password_new1 = request.POST.get('password_new1')
        print password,password_new1
        try:

            po = authenticate(username=username,password=password)
            pn = User.objects.get(username=username)
            if(po):
                if(str(password) == str(password_new1)):
                    result = 3
                    uu = {'res': result}
                    return JsonResponse(uu)

                if(pn):
                    result = 1
                    result = simplejson.dumps(result)
                    uu = {'res': result}
                    pn.set_password(password_new1)
                    pn.save()
                    return JsonResponse(uu)
                else:
                    result = 0
                    uu = {'res': result}
                    return JsonResponse(uu)
            else:
                result = 2
                uu = {'res': result}
                return JsonResponse(uu)
        except Exception, e:
            print e
    return render(request, 'wechatfans/modify_password.html',uu)