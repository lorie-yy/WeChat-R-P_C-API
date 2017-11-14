# -*- coding: UTF-8 -*-
import hashlib
import json
import datetime
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
import requests
from adminbd.models import SystemConfig
from wechatfans.models import TwechatOffline, ApplyforWithdrawalRecords

from adminbd.models import CloudInformation
from wechatfans.models import TwechatOffline, ThridPartyConfig, CloudConfig
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
                cloudconfig = CloudConfig.objects.filter(cloudname=cloudid)
                if cloudconfig.count() > 0:
                    context={}
                    context['url'] = cloudconfig[0].thirdpart.url

                    if cloudconfig[0].thirdpart.type == '2':#bigwifi
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
        shopid = request.GET.get('shopid',0)
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
        print response.text
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

        return HttpResponse(response.text)


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
    cloudid = request.GET.get('cloudid', 'TEMP:00:0c:29:42:cb:00')
    shopid = request.GET.get('shopid', '2')
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
    context['todayprofit']=todayprofit
    context['totalprofit']=totalprofit
    context['totalfans']=totalfans
    context['todayfans']=todayfans
    context['takemoney']=takemoney
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
    discountlist=SystemConfig.objects.filter(attribute='discount')
    if discountlist.count()==0:
        discount=0.9
    else:
        discount=discountlist[0].value
    profit=0
    for item in userobject:
        print 'usermac',item.id
        print 'usermac',item.price
        profit += float(item.price)
    profit_dis=round(profit*float(discount), 2)

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
        print 'usermac',item.id
        print 'usermac',item.price
        profit += float(item.price)
    profit_dis=round(profit*float(discount), 2)
    return profit_dis

def takemoney(request):
    cloudid = request.GET.get('cloudid', 'TEMP:00:0c:29:42:cb:00')
    shopid = request.GET.get('shopid', '2')
    takemoney=support_takemoney(cloudid,shopid)
    context ={}
    context['cloudid']=cloudid
    context['shopid']=shopid
    context['takemoney']=takemoney
    print takemoney
    # return HttpResponse(json.dumps(context))
    return render(request, 'wechatfans/takemoney.html',context)

# 取款记录
@csrf_exempt
def apply_for_withdrawal(request):
    cloudid = request.POST.get('cloudid', 'TEMP:00:0c:29:42:cb:00')
    shopid = request.POST.get('shopid', '2')
    paymentmode = request.POST.get('paymentmode')
    getmoney = request.POST.get('getmoney', 0.00)
    # 支付宝
    alipay_name = request.POST.get('alipay_name')
    alipaynum = request.POST.get('alipaynum')
    # 银行卡
    company = request.POST.get('company')
    bank_name = request.POST.get('bank_name')
    banknum = request.POST.get('banknum')
    history=ApplyforWithdrawalRecords.objects.filter(cloudid=cloudid,shopid=shopid,paymentresult=102)
    if history.count()>0:
        result=2
    else:
        # 创建表的实例对象(取款记录)
        applyrecords = ApplyforWithdrawalRecords(paymentresult=102)
        applyrecords.cloudid = cloudid
        applyrecords.shopid = shopid
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
    # return render(request, 'wechatfans/takemoney.html',context)


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
    cloudname = request.GET.get('cloudname')
    thirdpartid = request.GET.get('thirdpart')
    type = request.GET.get('type')
    result = {}
    result['error']=1
    iteminfo = CloudConfig.objects.filter(cloudname = cloudname)
    thirdpart = ThridPartyConfig.objects.filter(id = int(thirdpartid))
    try:
    # if True:
        if iteminfo.count() == 0:
            iteminfo = ThridPartyConfig(cloudname = cloudname,thirdpart=thirdpart[0],type=type)
            iteminfo.save()
            result['error']=0
        else:
            iteminfo.update(thirdpart=thirdpart[0],type=type)
            result['error']=0
    except Exception,e:
        result['error']=2
    return HttpResponse(json.dumps(result))

def getCloudConfig(request):
    cloudconfiginfo = CloudConfig.objects.all()
    cloudinfolist = []
    for item in cloudconfiginfo:
        itemdict = {}
        itemdict['cloudname']=item.cloudName
        itemdict['thirdpart_name']=item.thirdpart.thirdpartname
        cloudinfolist.append(itemdict)
    return HttpResponse(json.dumps(cloudinfolist))
