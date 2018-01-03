# -*- coding: UTF-8 -*-
import hashlib
import json
import datetime
from django.contrib.auth.models import User
from django.db.models import Sum
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template.context_processors import csrf
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.contrib.auth import authenticate
from django.core.cache import cache
from django_redis import get_redis_connection
import redis
import requests
from rest_framework import mixins,generics
import simplejson
from adminbd.models import SystemConfig
from wechatfans.models import TwechatOffline, ApplyforWithdrawalRecords, shop_discountinfo

from adminbd.models import CloudInformation
from wechatfans.models import TwechatOffline, ThridPartyConfig, CloudConfig, cloudtouser
import time
from wechatfans.serializers import shop_discountinfoSerializer, ThridPartyConfigSerializer, Shop_discountinfoSerializer, \
    CloudConfigSerializer, ApplyforWithdrawalRecordsSerializer


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
        shopid = request.GET.get('shopid','')
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
                if cloudconfig.count() == 0:
                    tpc = ThridPartyConfig.objects.get(type='1')
                    cloudconfig = CloudConfig(cloudid=cloudid,thirdpart=tpc)
                    cloudconfig.save()
                else:
                    cloudconfig=cloudconfig[0]
                context={}
                context['url'] = cloudconfig.thirdpart.url

                if cloudconfig.thirdpart.type == '1':#bigwifi
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
        username = request.GET.get('username','')
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
        newsign = direct_sign_md5(stringparm)
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
                                              settlement='1',
                                              username=username,
                                              cloudid=cloudid)
                else:
                    userlist.update(shopid=int(shopid),username=username,cloudid=cloudid)
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
def direct_sign_md5(parameters):
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
        daterange = request.GET.get('daterange',0)
        url = 'https://api.weifenshi.cn/api/sub_detail'
        now = datetime.datetime.now().strftime('%Y-%m-%d')
        startdate = (datetime.datetime.now() - datetime.timedelta(days = int(daterange))).strftime("%Y-%m-%d")
        # startdate = datetime.datetime.strptime('2017-03-03','%Y-%m-%d')
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
            delobject = TwechatOffline.objects.filter(price='0')
            delobject.delete()
        return HttpResponse("OK")


    def saveinfo(self,infolist):
        for item in infolist:
            orderid = item['oid']
            usermac = item['mac']
            apmac = item['bmac']
            openid = item['openid']
            price = item['price']
            sub_time = item['sub_time']
            gh_name = item['gh_name'].decode('unicode_escape')
            usermac = ':'.join([usermac[i:i + 2] for i in range(0, len(usermac), 2)])
            apmac = ':'.join([apmac[i:i + 2] for i in range(0, len(apmac), 2)])
            userobject = TwechatOffline.objects.filter(openid=openid,
                                          orderid=orderid,
                                          )
            if userobject.count() > 0:
                userobject.update(price=price,bdyunprice=float(price)*0.89,gh_name=gh_name,apmac=apmac,authtime=sub_time)
            else:
                to = TwechatOffline(openid=openid,
                                   orderid=orderid,
                                   usermac=usermac,
                                   apmac=apmac,
                                   price=price,
                                   bdyunprice=float(price)*0.89,
                                   gh_name=gh_name,
                                   authtime=sub_time,
                                   subscribe='1',
                                   settlement='1',
                                   type='1',
                               )
                to.save()

def showfans(request):
    '''
    1.更新TwechatOffline，获取最近两天的收益
    2.计算今日收益与粉丝
    3.计算可提现金额
    4.总金额=可提现金额+已提现+申请中
    :param request:
    :return:
    '''
    # path_url=request.build_absolute_uri('/wechatfans/sub_detail?daterange=0')
    # print 'path_url',path_url
    # requests.get(path_url)
    username,sc_userlevel,user_type,is_superuser=islogin(request)
    if username=='' or user_type==0 or is_superuser==1:
        return render(request,'license_login.html')
    if sc_userlevel ==2:
        return HttpResponseRedirect('showprofit')
    cloudid = request.session.get('sc_cloudid')
    shopid = request.session.get('sc_shopid')
    # 今天开始0点-结束24点
    startdate=datetime.datetime.now().strftime('%Y-%m-%d')
    startDate = datetime.datetime(int(startdate[:4]), int(startdate[5:7]), int(startdate[8:10]), 0, 0,0)
    endDate = datetime.datetime(int(startdate[:4]), int(startdate[5:7]), int(startdate[8:10]), 23, 59,59)
    print startDate
    print endDate
    context ={}
    # 调用函数
    # totalprofit,totalfans=earnings(cloudid,shopid,'','')
    #获取可提现金额
    takemoney,flag,profit=support_takemoney(username)
    #获取今日收益以及粉丝
    todayprofit,todayfans=earnings(username,startDate,endDate)
    if cache.get(username+"takemoney",'')== takemoney and\
        cache.get(username+"todayprofit",'')== todayprofit:
        print "get value in cache",username+"takemoney"
        takemoney = cache.get(username+"takemoney")
        totalprofit = cache.get(username+"totalprofit")
        totalfans = cache.get(username+"totalfans")
        todayprofit = cache.get(username+"todayprofit")
        todayfans = cache.get(username+"todayfans")
    else:
        print "update value "

        #获取粉丝数
        totalfans = TwechatOffline.objects.filter(username=username).count()
        #重新计算可提现金额以及总收入
        totalprofit = saveShopProfit(cloudid,shopid,takemoney)

        cache.set(username+"todayprofit", todayprofit, timeout=None)
        cache.set(username+"todayfans", todayfans, timeout=None)
        cache.set(username+"takemoney", takemoney, timeout=None)
        cache.set(username+"totalprofit", totalprofit, timeout=None)
        cache.set(username+"totalfans", totalfans, timeout=None)
    # x轴日期数据
    today = datetime.date.today()
    oneweekago = today - datetime.timedelta(7)
    begin=request.GET.get('begin',oneweekago.strftime('%Y-%m-%d'))
    end=request.GET.get('end',today.strftime('%Y-%m-%d'))
    # begin=request.GET.get('begin','2017-11-11')
    # end=request.GET.get('end','2017-11-17')
    print 'begin,end',begin,end
    xdata = []
    dt = datetime.datetime.strptime(begin, "%Y-%m-%d")
    date = begin[:]
    while date <= end:
        xdata.append(date)
        # 日期间隔为一天
        dt = dt + datetime.timedelta(1)
        date = dt.strftime("%Y-%m-%d")
    # 转义
    context['xdata']=str(xdata).decode("unicode-escape")
    print 'xdata',str(xdata).decode("unicode-escape")

    # y轴收益数据
    seriesdata=[]
    for item in xdata:
        # 某天开始0点-结束24点
        dayprofit = cache.get(username+item,'')
        if dayprofit =="" or item == end :
            startDate = datetime.datetime(int(item[:4]), int(item[5:7]), int(item[8:10]), 0, 0,0)
            endDate = datetime.datetime(int(item[:4]), int(item[5:7]), int(item[8:10]), 23, 59,59)
            dayprofit,dayfans=earnings(username,startDate,endDate)
            cache.set(username+item, dayprofit, timeout=None)
        seriesdata.append(dayprofit/100.00)
    print 'seriesdata',seriesdata
    context['seriesdata']=seriesdata

    context['cloudid']=cloudid
    context['shopid']=shopid
    context['username']=username
    context['sc_userlevel']=sc_userlevel
    context['todayprofit']=todayprofit/100.000
    context['totalprofit']=totalprofit/100.000
    context['totalfans']=totalfans
    context['todayfans']=todayfans
    context['takemoney']=takemoney/100.000
    # return HttpResponse(json.dumps(context))

    return render(request, 'wechatfans/showfans.html',context)
#保存收益
def saveShopProfit(cloudid,shopid,takemoney):
    shopprofit = shop_discountinfo.objects.filter(cloudid=cloudid,shopid=shopid)
    if shopprofit.count() > 0:
        totalprofit = shopprofit[0].applying + shopprofit[0].cashed + takemoney
        if shopprofit[0].availablecash == takemoney and \
            shopprofit[0].totalincome == totalprofit:
            pass
        else:
            shopprofit.update(totalincome=totalprofit,availablecash=takemoney)
    else:
        totalprofit = takemoney
        cloudtouserobj = cloudtouser.objects.get(cloudid=cloudid,shopid=shopid)
        ad = shop_discountinfo(cloudid=cloudid,
                               totalincome=totalprofit,
                               availablecash=takemoney,
                               cloudtouser=cloudtouserobj,
                               shopid=shopid)
        ad.save()
    return totalprofit

#保存所有shop_discountinfo
def saveShopDiscountInfo():
    #获取所有云平台
    cloudinfo = CloudInformation.objects.all()
    for clouditem in cloudinfo:
        #获取云平台下的商铺id
        if clouditem.cloudNum:
            cloudid = clouditem.id
        else:
            cloudid = clouditem.tmpCloudNum
        resultlist = TwechatOffline.objects.filter(cloudid=cloudid)
        if resultlist.count() > 0:
            shopidSet = resultlist.values('shopid')
            shopidlist = []
            for shopid in shopidSet:
                #保存
                _shopid = shopid['shopid']
                shopidlist.append(_shopid)
            shopidlist =  list(set(shopidlist))
            print shopidlist
            for itemshopid in shopidlist:
                shopinfolist = shop_discountinfo.objects.filter(cloudid=cloudid,shopid=itemshopid)
                cloudtouserob = cloudtouser.objects.filter(cloudid=cloudid,shopid=itemshopid)
                if cloudtouserob.count() > 0:
                    if shopinfolist.count() == 0:
                        sd = shop_discountinfo(cloudid=cloudid,shopid=itemshopid,cloudtouser=cloudtouserob[0])
                        sd.save()
                        takemoney,flag,profit=support_takemoney(cloudtouserob[0].username)
                        saveShopProfit(cloudid,itemshopid,takemoney)

class getCloudProfit(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    serializer_class = shop_discountinfoSerializer

    def get_queryset(self):
        try:
            cloudid = self.request.GET.get('cloudid')
        except Exception,e:
            return HttpResponse(status=404)
        return shop_discountinfo.objects.filter(cloudid=cloudid)

    def get(self, request, *args, **kwargs):

        return self.list(request, args, kwargs)


class getAllProfit(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    saveShopDiscountInfo()

    def get_queryset(self):
        queryset = shop_discountinfo.objects.all()
        return queryset
    serializer_class = shop_discountinfoSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, args, kwargs)



# 计算收益量和粉丝量
def earnings(username,startDate,enddate):
    usernamelist = cloudtouser.objects.filter(username=username)
    if (not startDate) and (not enddate):
        userobject = TwechatOffline.objects.filter(username=username)
    else:
        userobject = TwechatOffline.objects.filter(username=username,
                                        authtime__range=(startDate,enddate)
                                          )
    # 用户权限收益打折扣
    shop_discount=shop_discountinfo.objects.filter(cloudid=usernamelist[0].cloudid,shopid=usernamelist[0].shopid)
    discountlist=SystemConfig.objects.filter(attribute='discount')
    if shop_discount.count()==0:
        if discountlist.count()==0:
            discount=0.8
        else:
            discount=discountlist[0].value
    else:
        discount=shop_discount[0].discount

    profit=0
    for item in userobject:
        # print 'usermac',item.id
        # print 'usermac',item.price
        profit += (float(item.userprice)*100)
    profit_dis=int(profit*float(discount))
    print username,'profit_dis:',profit_dis,profit

    return profit_dis,userobject.count()

# 可提现金额
def support_takemoney(username):
    usernamelist = cloudtouser.objects.filter(username=username)
    userobject = TwechatOffline.objects.filter(username=username,settlement=1).order_by('-id')
    if userobject.count() > 0:
        flag = userobject[0].id
    else:
        flag = 0
    # 用户权限收益打折扣
    shop_discount=shop_discountinfo.objects.filter(cloudid=usernamelist[0].cloudid,shopid=usernamelist[0].shopid)
    discountlist=SystemConfig.objects.filter(attribute='discount')
    if shop_discount.count()==0:
        if discountlist.count()==0:
            discount=0.8
        else:
            discount=discountlist[0].value
        start = 0
        beforediscountincome = 0
    else:
        discount=shop_discount[0].discount
        start = shop_discount[0].start
        beforediscountincome = shop_discount[0].beforediscountincome
    profit=0

    #申请提现的金额
    record = ApplyforWithdrawalRecords.objects.filter(username=username,paymentresult=103)
    if record.count() > 0:
        applyformoney = record[0].getmoney
    else:
        applyformoney = 0
    for item in userobject:
        # print 'usermac',item.id
        # print 'usermac',item.price
        profit += (float(item.userprice)*100)
    profit_dis=int((profit-start)*float(discount))+beforediscountincome-applyformoney
    print '可提现金额',profit_dis
    return profit_dis,flag,profit

def takemoney(request):
    username,sc_userlevel,user_type,is_superuser=islogin(request)
    if username==''or user_type==0 or is_superuser==1:
        return render(request,'license_login.html')
    cloudid = request.session.get('sc_cloudid')
    shopid = request.session.get('sc_shopid')
    takemoney,flag,profit=support_takemoney(username)
    context ={}
    context['cloudid']=cloudid
    context['flag']=flag
    context['shopid']=shopid
    context['username']=username
    context['sc_userlevel']=sc_userlevel
    context['takemoney']=takemoney/100.000

    # 二级商户可提现余额
    #先计算更新
    user = cloudtouser.objects.filter(username=username)
    if user.count() > 0:
        fathernodeid = user[0].fathernode
        updateProfit(user[0].id,fathernodeid)
        sd = shop_discountinfo.objects.filter(cloudtouser_id=user[0].id)
        if sd.count() > 0:
            context["availablecash"] = sd[0].availablecash/100.000
    return render(request, 'wechatfans/takemoney.html',context)

# 创建取款记录
@csrf_exempt
def apply_for_withdrawal(request):
    username,sc_userlevel,user_type,is_superuser=islogin(request)
    if username==''or user_type==0 or is_superuser==1:
        return render(request,'license_login.html')
    cloudid = request.session.get('sc_cloudid')
    shopid = request.session.get('sc_shopid')
    paymentmode = request.POST.get('paymentmode')
    flag = request.POST.get('flag')
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
    history=ApplyforWithdrawalRecords.objects.filter(username=username,paymentresult=103)
    if history.count()>0:
        result=2
    elif getmoney < 10000:
        result=3
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
        applyrecords.flag = flag
        applyrecords.save()

        #更新shop_discountinfo
        sd = shop_discountinfo.objects.filter(cloudid=cloudid,shopid=shopid)
        availablecash = sd[0].availablecash - getmoney
        sd.update(availablecash=availablecash,applying=getmoney)

        result = 1

    context ={}
    context['result']=result
    print result
    return JsonResponse({'result':result})

# 申请提现记录
def applyfor_records(request):
    username,sc_userlevel,user_type,is_superuser=islogin(request)
    if username==''or user_type==0 or is_superuser==1:
        return render(request,'license_login.html')
    cloudid = request.session.get('sc_cloudid')
    shopid = request.session.get('sc_shopid')
    records=ApplyforWithdrawalRecords.objects.filter(username=username)
    context ={}
    context['records']=records
    context['username']=username
    context['sc_userlevel']=sc_userlevel
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
            tempdict['getmoney']=getmoney/100.000
            tempdict['paymentresult']=paymentresult
            recordslist.append(tempdict)

    # 成功提现总计
    totalsuc=0
    suc=ApplyforWithdrawalRecords.objects.filter(username=username,paymentresult=101)
    if suc.count()==0:
        print '成功提现总计为0'
    else:
        for i in suc:
            totalsuc += i.getmoney
        print '成功提现总计为',totalsuc
    context['totalsuc']=totalsuc/100.000
    context['recordslist']=recordslist
    return render(request, 'wechatfans/applyfor_records.html',context)

# 关闭申请
def closerecord(request):
    username,sc_userlevel,user_type,is_superuser=islogin(request)
    if username==''or user_type==0 or is_superuser==1:
        return render(request,'license_login.html')
    result=0
    id = request.GET.get('id')
    record=ApplyforWithdrawalRecords.objects.filter(id=id)
    if record.count()>0:
        record.update(paymentresult=102)

        #更新shop_discountinfo
        userid = cloudtouser.objects.filter(username=username)
        sdc = shop_discountinfo.objects.filter(cloudtouser=userid[0].id)
        availablecash = sdc[0].availablecash + record[0].getmoney
        applying = sdc[0].applying - record[0].getmoney
        sdc.update(applying=applying,availablecash=availablecash)
        result=1
        print result
    return JsonResponse({'result':result})

class getThirdpartInfo(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):

    queryset = ThridPartyConfig.objects.all()
    serializer_class = ThridPartyConfigSerializer
    def get(self, request, *args, **kwargs):
        if request.GET.get('alldata','')=='1':
            print 'get all data'
            queryset = ThridPartyConfig.objects.all()
            serializer = ThridPartyConfigSerializer(queryset, many=True)
            return JsonResponse(serializer.data, safe=False)
        return self.list(request, args, kwargs)

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
        result['msg']=str(e)
    return HttpResponse(json.dumps(result))

def getCloudname(request):
    cloudinfo = CloudInformation.objects.all()
    cloudinfolist = []
    for item in cloudinfo:
        itemdict = {}
        itemdict['cloudname']=item.cloudName
        if item.cloudNum:
            itemdict['cloudid']=item.id
        else:
            itemdict['cloudid']=item.tmpCloudNum
        cloudinfolist.append(itemdict)
    return HttpResponse(json.dumps(cloudinfolist))

def saveCloudconfig(request):
    cloudname = request.GET.get('cloudname','null')
    cloudid = request.GET.get('cloudid')
    thirdpartname = request.GET.get('thirdpart')
    operationtype = request.GET.get('typeThird','')
    result = {}
    result['msg']='操作成功'
    result['error']=0
    cloudinfo = CloudInformation.objects.filter(id=cloudid)
    if cloudinfo.count() > 0:
        cloudname = cloudinfo[0].cloudName
    else:
        cloudinfo = CloudInformation.objects.filter(tmpcloudNum=cloudid)
        if cloudinfo.count() > 0:
            cloudname = cloudinfo[0].cloudName
        else:
            cloudname = ''
    iteminfo = CloudConfig.objects.filter(cloudid=cloudid)
    thirdpart = ThridPartyConfig.objects.filter(thirdpartname = thirdpartname)
    # try:
    if True:
        if operationtype == 'add':
            if iteminfo.count() == 0:
                iteminfo = CloudConfig(cloudname = cloudname,thirdpart=thirdpart[0],cloudid=cloudid)
                iteminfo.save()

            else:
                result['error']=3
                result['msg']='新增失败'
        elif operationtype == 'edit':
            if iteminfo.count() == 0:
                result['error']=4
                result['msg']='编辑失败'
            else:
                iteminfo.update(thirdpart=thirdpart[0])

        elif operationtype == 'del':
            if iteminfo.count() == 0:
                result['error']=5
                result['msg']='删除失败'
            else:
                iteminfo.delete()

    # except Exception,e:
    #     result['error']=2
    #     result['msg']= e
    return HttpResponse(json.dumps(result))

class getCloudConfig(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    serializer_class = CloudConfigSerializer

    queryset = CloudConfig.objects.all()

    def get(self, request, *args, **kwargs):

        return self.list(request, args, kwargs)



class Register(View):
    # @csrf_exempt
    def get(self,request):
        user_name = request.GET.get('username')
        password = request.GET.get('password')
        cloudid = request.GET.get('cloudid','')
        shopid = request.GET.get('shopid','')
        super_user = request.GET.get('super_user',0)

        userSet = User.objects.filter(username=user_name)
        if userSet.count() > 0:
            print "user exists"
            result = 2
            uu = {'res':result}
            return JsonResponse(uu)

        try:


            clouduser = cloudtouser.objects.filter(username=user_name)
            #add cloud admin
            if clouduser.count() == 0:
                # auth_user表
                user = User.objects.create_user(username=user_name,password=password,user_type = 1)
                print "create new user and inital pwd is 123456"
                print user
                if super_user in[1,'1'] :
                    user.is_superuser = 1
                else:
                    user.is_superuser = 0
                user.user_level = super_user

                user.is_staff = 1
                user.is_active = 1
                user.date_joined = datetime.datetime.now().strftime("%Y-%m-%d %H:%I:%S")
                user.save()
                #cloud_user表
                if cloudid == '' or shopid == '':
                    co = cloudtouser(username=user_name,password=password)
                else:
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


def getshopid(request):
    '''
    根据云平台的编号获取这个云平台的商铺id
    :param request:
    :return:shop id list
    '''
    try:
        cloudid = request.GET.get('cloudid','')
        shopdiscountlist = shop_discountinfo.objects.filter(cloudid=cloudid)
        shopiddiscountlist = shopdiscountlist.values('shopid')
        oldshopidlist = []
        for itemid in shopiddiscountlist:
            oldshopidlist.append(itemid['shopid'])

        resultlist = TwechatOffline.objects.filter(cloudid=cloudid)
        shopidSet = resultlist.values('shopid')
        shopidlist = []
        for shopid in shopidSet:
            if shopid['shopid'] in oldshopidlist:
                pass
            else:
                shopidlist.append(shopid['shopid'])
        shopidlist =  list(set(shopidlist))
    except Exception,e:
        shopidlist = []
    return HttpResponse(json.dumps(shopidlist))

def savediscountinfo(request):
    '''
    保存商铺的折扣信息
    :param request:
    :return:
    '''
    cloudid = request.GET.get('cloudid','')
    shopid = request.GET.get('shopid','')
    discount = request.GET.get('bonus','')
    operationtype = request.GET.get('typeThird','')
    print cloudid,shopid,discount
    result = 1
    try:
        shopinfo = shop_discountinfo.objects.filter(cloudid=cloudid,shopid=shopid)
        if operationtype == 'add':
            if shopinfo.count() ==0:
                cloudtouserob = cloudtouser.objects.get(cloudid=cloudid,shopid=shopid)
                sd = shop_discountinfo(cloudid=cloudid,shopid=shopid,discount=discount,cloudtouser=cloudtouserob)
                sd.save()
                result = 0
            else:
                result = 1

        elif operationtype == 'edit':
            if shopinfo.count() ==0:
                result = 2
            else:
                takemoney,flag,profit=support_takemoney(shopinfo[0].cloudtouser.username)
                start = profit
                beforediscountincome = shopinfo[0].totalincome
                shopinfo.update(discount=discount,start=start,beforediscountincome=beforediscountincome)
                result = 0
        elif operationtype == 'del':
            if shopinfo.count() ==0:
                result = 3
            else:
                shopinfo.delete()
                result = 0
    except Exception,e:
        result = 4
    uu = {'res':result}
    return JsonResponse(uu)

class getalldiscountinfo(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    '''
    获取所有商铺的折扣信息
    :param request:
    :return:
    '''

    serializer_class = shop_discountinfoSerializer

    queryset = shop_discountinfo.objects.all()

    def get(self, request, *args, **kwargs):

        return self.list(request, args, kwargs)


class getApplyforWithdrawal(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    '''
    获取可提现记录
    :param request:
    :return:
    '''

    serializer_class = ApplyforWithdrawalRecordsSerializer
    saveShopDiscountInfo()
    def get_queryset(self):
        applyfor = ApplyforWithdrawalRecords.objects.filter(paymentresult=103)
        for applyforitem in applyfor:
            #确认是否可提现
            if isSafe(applyforitem.cloudid,applyforitem.shopid,applyforitem.getmoney):
                pass
            else:
                applyforitem.paymentresult=102
                applyforitem.save()
        pagetype = self.request.GET.get('pagetype')
        if pagetype == 'Apply':
            return ApplyforWithdrawalRecords.objects.filter(paymentresult=103).filter(paymentmode=1)
        elif pagetype == 'Bank':
            return ApplyforWithdrawalRecords.objects.filter(paymentresult=103).filter(paymentmode=2)


    def get(self, request, *args, **kwargs):

        return self.list(request, args, kwargs)


def isSafe(cloudid,shopid,getmoney):
    shopinfo = shop_discountinfo.objects.filter(cloudid=cloudid,shopid=shopid)
    if shopinfo.count() > 0:
        if getmoney <= shopinfo[0].applying:
            return  True
    return False

class getallApplyforWithdrawalRecords(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    '''
    获取所有提现记录
    :param request:
    :return:
    '''
    serializer_class = ApplyforWithdrawalRecordsSerializer

    def get_queryset(self):
        pagetype = self.request.GET.get('pagetype')
        if pagetype == 'Apply':
            return ApplyforWithdrawalRecords.objects.exclude(paymentresult=103).filter(paymentmode=1)
        elif pagetype == 'Bank':
            return ApplyforWithdrawalRecords.objects.exclude(paymentresult=103).filter(paymentmode=2)

    def get(self, request, *args, **kwargs):

        return self.list(request, args, kwargs)



class Transferaccounts(View):
    def get(self,request):
        id = request.GET.get('id')
        typeThird = request.GET.get('typeThird')
        #取出申请记录
        applyfor = ApplyforWithdrawalRecords.objects.filter(id=id)
        result = {}
        if applyfor.count() > 0:
            cloudid = applyfor[0].cloudid
            shopid = applyfor[0].shopid
            usernamelist = cloudtouser.objects.filter(cloudid=cloudid,shopid=shopid)
            getmoney = applyfor[0].getmoney
            if typeThird == 'pass':
                #是否符合提现条件
                if isSafe(cloudid,shopid,getmoney):
                    #判断转账方式，如需实现自动转账，在此码代码
                    #现省略此步

                    #确认转账成功后更新数据库
                    #1.更新TwechatOffline
                    oldflag = applyfor[0].flag
                    twolist = TwechatOffline.objects.filter(id__lte=oldflag,username=usernamelist[0].username,settlement=1)
                    twolist.update(settlement=2)

                    #2.更新ApplyforWithdrawalRecords
                    applyfor.update(paymentresult=101)

                    #3.更新shop_discountinfo
                    sdc = shop_discountinfo.objects.filter(cloudid=cloudid,shopid=shopid)
                    cashed = sdc[0].cashed + getmoney
                    applying = sdc[0].applying - getmoney
                    sdc.update(applying=applying,cashed=cashed)
                    result['res'] = 0
                    result['msg'] = '转账成功'
            elif typeThird == 'no':
                #转账失败
                applyfor.update(paymentresult=102)

                #更新shop_discountinfo
                sdc = shop_discountinfo.objects.filter(cloudid=cloudid,shopid=shopid)
                availablecash = sdc[0].availablecash + getmoney
                applying = sdc[0].applying - getmoney
                sdc.update(applying=applying,availablecash=availablecash)
                result['res'] = 0
                result['msg'] = '转账失败，拒绝转账'
        else:
            result['res'] = 1
            result['msg'] = '转账失败，无申请记录'
        return HttpResponse(json.dumps([result]))



# 退出登录
@csrf_exempt
def logout(request):
    if request.method == "GET":
        username,sc_userlevel,user_type,is_superuser=islogin(request)
        if username==''or user_type==0 or is_superuser==1:
            return render(request,'license_login.html')
        request.session.flush()
        return render(request,'license_login.html')


# 修改密码
@csrf_exempt
def modify_password(request):
    username,sc_userlevel,user_type,is_superuser=islogin(request)
    if username==''or user_type==0 or is_superuser==1:
        return render(request,'license_login.html')
    uu = {'username': username,'sc_userlevel': sc_userlevel}
    if request.method == 'POST':
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
                    user=cloudtouser.objects.filter(username=username)
                    user.update(password=password_new1)
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

def updateAllShopProfit():
    '''
    计算所有商户的收益
    :param :
    :return:
    '''
    alluser = cloudtouser.objects.filter(fathernode=0)
    for fathernode in alluser:
        fathernodeid = fathernode.id
        childid = [item.id for item in cloudtouser.objects.filter(fathernode=fathernodeid)]
        for id in childid:
            updateProfit(id,fathernodeid)


def updateProfit(id,fathernodeid):
    '''
    计算二级商户的总收益，可提现
    :param id:cloudtouser表中二级商户的id
    :param fathernodeid:cloudtouser表中上级商户的id
    :return:
    '''
    sd = shop_discountinfo.objects.filter(cloudtouser_id=id)
    if sd.count() > 0:
        ct = shop_discountinfo.objects.filter(cloudtouser_id=fathernodeid)
        if ct.count() > 0:
            #上级商户可提现金额
            total = ct[0].cashed
            #下级商户总收益
            totalincome = sd[0].beforediscountincome +(total-sd[0].start)*sd[0].discount
            #下级商户可提现
            availablecash = totalincome - sd[0].cashed - sd[0].applying
            if sd[0].totalincome == totalincome and availablecash==sd[0].availablecash:
                pass
            else:
                sd.update(totalincome=totalincome,availablecash=availablecash)
@csrf_exempt
def addchild(request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        discount = request.POST.get('discount')
        fa_username = request.session.get('username','')
        result = 4
        uu = {'res':result}

        userSet = User.objects.filter(username=username)
        if userSet.count() > 0:
            print "user exists"
            result = 2
            uu = {'res':result}
            return JsonResponse(uu)
        else:
            clouduser = cloudtouser.objects.filter(username=fa_username)
            #add cloud admin
            if clouduser.count() > 0:
                father_id=clouduser[0].id
                all_dis=calculate_discount(father_id,discount)
                #总折扣大于1时,不允许新增
                if all_dis > 1:
                    return JsonResponse({'res':5})
                # auth_user表
                user = User.objects.create_user(username=username,password=password,user_type = 1)
                print user

                user.is_staff = 1
                user.is_active = 1
                user.date_joined = datetime.datetime.now().strftime("%Y-%m-%d %H:%I:%S")
                user.save()
                #cloud_user表
                co = cloudtouser(username=username,password=password,fathernode=clouduser[0].id,userlever=2)
                co.save()
                #获取子商户总收益
                fa_dis=shop_discountinfo.objects.filter(cloudtouser_id=clouduser[0].id)
                if fa_dis.count() > 0:
                    total=fa_dis[0].cashed*float(discount)
                    #discount表
                    sd = shop_discountinfo(cloudtouser=co,
                                           discount=discount,
                                           totalincome=total,
                                           beforediscountincome=total,
                                           availablecash=total,
                                           start=fa_dis[0].cashed)
                    sd.save()
                    result = 0
                    uu = {'res':result}
                    return JsonResponse(uu)
            else:
                result = 1
                uu = {'res':result}
                return JsonResponse(uu)
            return JsonResponse(uu)

# 修改子商户discount
def edit_child_dis(request):
    id = request.GET.get('id')
    discount = request.GET.get('discount')
    result=0
    username,sc_userlevel,user_type,is_superuser=islogin(request)
    if username==''or user_type==0 or is_superuser==1:
        return render(request,'license_login.html')
    try:
        clouduser = cloudtouser.objects.filter(username=username)
        if clouduser.count() > 0:
            #获取子商户总收益
            fa_id=clouduser[0].id
            fa_dis=shop_discountinfo.objects.filter(cloudtouser_id=fa_id)
            total=fa_dis[0].cashed
            #更新shop_discountinfo
            sdc = shop_discountinfo.objects.filter(id=id)
            user_id=sdc[0].cloudtouser_id
            beforediscountincome=sdc[0].totalincome
            all_dis=calculate_discount(fa_id,discount,user_id)
            #总折扣小于等于1时,允许修改
            if all_dis <= 1:
                print 'all_dis',all_dis
                sdc.update(discount=discount,start=total,beforediscountincome=beforediscountincome)
                result=1
                print result
            else:
                result=3
    except Exception,e:
        print e
        result=2
    print result
    return JsonResponse({'result':result})

# 计算总折扣
def calculate_discount(father_id,discount,child_id=-100):
    allchild = cloudtouser.objects.filter(fathernode=father_id).exclude(id=child_id)
    allid=[child.id for child in allchild]
    allid_rec=shop_discountinfo.objects.filter(cloudtouser_id__in=allid)
    all_dis=sum([dis.discount for dis in allid_rec])+float(discount)
    return all_dis


def showAllChildshopProfit(request):
    '''
    显示所有子商户的收益情况
    :param request:
    :return:
    '''
    username,sc_userlevel,user_type,is_superuser=islogin(request)
    if username==''or user_type==0 or is_superuser==1:
        return render(request,'license_login.html')
    fathernode = cloudtouser.objects.filter(username=username)
    if fathernode.count() > 0:

        #1.更新所有子商户的收益
        #2.取出所有子商户的收益信息
        context = {}
        context["username"] = username
        context["sc_userlevel"] = sc_userlevel
        data = []
        fathernodeid = fathernode[0].id
        childid = [item.id for item in cloudtouser.objects.filter(fathernode=fathernodeid)]
        for id in childid:
            updateProfit(id,fathernodeid)
            ct = shop_discountinfo.objects.filter(cloudtouser_id=id)
            if ct.count() > 0:
                tmpdict = {}
                tmpdict["id"] = ct[0].id
                tmpdict["totalincome"] = ct[0].totalincome/100.000
                tmpdict["availablecash"] = ct[0].availablecash/100.000
                tmpdict["cashed"] = ct[0].cashed/100.000
                tmpdict["applying"] = ct[0].applying/100.000
                tmpdict["discount"] = ct[0].discount
                tmpdict["ch_username"] = ct[0].cloudtouser.username
                data.append(tmpdict)
        context["data"]=data
        return render(request,'wechatfans/showallchildshopprofit.html',context)

class getChildApply(View):
    def get(self,request):
        username,sc_userlevel,user_type,is_superuser=islogin(request)
        if username==''or user_type==0 or is_superuser==1:
            return render(request,'license_login.html')
        fathernode = cloudtouser.objects.filter(username=username)
        context = {}
        if fathernode.count() > 0:
            fathernodeid = fathernode[0].id
            childname = [item.username for item in cloudtouser.objects.filter(fathernode=fathernodeid)]
            request.session["childname"]=childname
            allapplyrecords = ApplyforWithdrawalRecords.objects.filter(username__in=childname)
            applyrecords103=allapplyrecords.filter(paymentresult=103)
            applyrecords=allapplyrecords.exclude(paymentresult=103)
            context["username"] = username
            context["sc_userlevel"] = sc_userlevel
            context["applyrecords103"] = applyrecords103
            context["applyrecords"] = applyrecords
        return render(request,'wechatfans/showallchildshopapply.html',context)
    @csrf_exempt
    def post(self,request):
        username,sc_userlevel,user_type,is_superuser=islogin(request)
        if username==''or user_type==0 or is_superuser==1:
            return render(request,'license_login.html')
        applyrecordid = request.POST.get('applyrecordid','')
        result = request.POST.get('result','')
        print 'recordid**********',applyrecordid,result
        res = 1
        if result == "pass":
            if self.isSafe(request):
                #1.转账代码可在此添加
                #2.转帐成功后修改数据库
                record = ApplyforWithdrawalRecords.objects.filter(id=applyrecordid)
                applyingmoney = record[0].getmoney
                #ApplyforWithdrawalRecords
                record.update(paymentresult=101)
                #shop_discountinfo
                username=cloudtouser.objects.filter(username=record[0].username)
                userid=username[0].id
                sd = shop_discountinfo.objects.filter(cloudtouser_id=userid)
                cashed = sd[0].cashed + applyingmoney
                applying = sd[0].applying - applyingmoney
                sd.update(cashed=cashed,applying=applying)
                res = 0
        elif result == "refuse":
            #拒绝转账
            record = ApplyforWithdrawalRecords.objects.filter(id=applyrecordid)
            applyingmoney = record[0].getmoney
            #ApplyforWithdrawalRecords
            record.update(paymentresult=102)
            #shop_discountinfo
            username=cloudtouser.objects.filter(username=record[0].username)
            userid=username[0].id
            sd = shop_discountinfo.objects.filter(cloudtouser_id=userid)
            availablecash = sd[0].availablecash + applyingmoney
            applying = sd[0].applying - applyingmoney
            sd.update(availablecash=availablecash,applying=applying)
            res = 2
        print '************res',res
        return JsonResponse({"res":res})

    def isSafe(self,request):
        try:
            childname = request.session.get("childname",[])
            applyrecordid = request.POST.get('applyrecordid',-1)
            name = ApplyforWithdrawalRecords.objects.filter(id=applyrecordid)[0].username
            if name in childname:
                return True
            else:
                return False
        except Exception,e:
            return False

def islogin(request):
    username = request.session.get('username','')
    userlevel = request.session.get('sc_userlevel','')
    user_type = request.session.get('user_type','')
    is_superuser = request.session.get('is_superuser','')
    # if not username or user_type==0 or is_superuser==1:

    return username,userlevel,user_type,is_superuser

def update_everybodyprofit(requset):
    '''
    1.获取所有的用户名
    2.更新每一个用户的今日收益
    :param requset:
    :return:
    '''
    print "[INFO] update everybody profit"
    startdate=datetime.datetime.now().strftime('%Y-%m-%d')
    startDate = datetime.datetime(int(startdate[:4]), int(startdate[5:7]), int(startdate[8:10]), 0, 0,0)
    endDate = datetime.datetime(int(startdate[:4]), int(startdate[5:7]), int(startdate[8:10]), 23, 59,59)
    userlist =[item.username for item in cloudtouser.objects.all()]
    for user in userlist:
        #获取今日收益以及粉丝
        todayprofit,todayfans=earnings(user,startDate,endDate)
        cache.set(user+startdate, todayprofit, timeout=None)
    return HttpResponse('OK')

def update_userprice(request):
    '''
    更新用户价格
    :param request:
    :return:
    '''
    print "[INFO] update userprice"
    needupdatelist = TwechatOffline.objects.filter(userprice=0).exclude(bdyunprice=0).exclude(username="")
    for item in needupdatelist:
        if item.type == "1":
            bdyunprice  = float(item.bdyunprice)
            username = item.username
            #获取折扣
            user = cloudtouser.objects.filter(username=username)
            print username
            print user[0].id
            shop_discount=shop_discountinfo.objects.filter(cloudid=user[0].cloudid,shopid=user[0].shopid)
            discountlist=SystemConfig.objects.filter(attribute='discount')
            if shop_discount.count()==0:
                if discountlist.count()==0:
                    discount=0.8
                else:
                    discount=discountlist[0].value
            else:
                discount=shop_discount[0].discount

            userprice = bdyunprice*float(discount)
            item.userprice = userprice
            item.save()
    return HttpResponse('OK')
#=============子商户页面开始=================
#1.查看收益
def showProfit(request):
    username,sc_userlevel,user_type,is_superuser=islogin(request)
    if username==''or user_type==0 or is_superuser==1:
        return render(request,'license_login.html')
    #先计算更新
    user = cloudtouser.objects.filter(username=username)
    context = {}
    context["username"] = username
    context["sc_userlevel"] = sc_userlevel
    if user.count() > 0:
        fathernodeid = user[0].fathernode
        updateProfit(user[0].id,fathernodeid)
        sd = shop_discountinfo.objects.filter(cloudtouser_id=user[0].id)
        if sd.count() > 0:
            context["totalincome"] = sd[0].totalincome/100.000
            context["availablecash"] = sd[0].availablecash/100.000
            context["cashed"] = sd[0].cashed/100.000
            context["applying"] = sd[0].applying/100.000

            # 提现记录
            records=ApplyforWithdrawalRecords.objects.filter(username=username)
            context['records']=records
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
                    tempdict['username']=username
                    tempdict['applyfortime']=applyfortime
                    tempdict['paymentmode']=paymentmode
                    tempdict['alipaynum']=alipaynum
                    tempdict['banknum']=banknum
                    tempdict['getmoney']=getmoney/100.000
                    tempdict['paymentresult']=paymentresult
                    recordslist.append(tempdict)
            context['recordslist']=recordslist
        return render(request,'wechatfans/showfans.html',context)

#2.提现申请

#3.申请记录

#=============子商户页面结束=================

#校验云平台发送的用户名和密码
def is_valid(request):
    username = request.GET.get('username','')
    password = request.GET.get('password','')
    timestamp = request.GET.get('timestamp','')
    cloudid = request.GET.get('cloudid','')
    shopid = request.GET.get('shopid','')
    oldsign = request.GET.get('sign','')
    context={}
    pc = prpcrypt('thisismykeysqazx')
    username = pc.decrypt(username)
    password = pc.decrypt(password)
    timestamp = pc.decrypt(timestamp)
    shopid = pc.decrypt(shopid)
    cloudid = pc.decrypt(cloudid)
    context['username']=username
    context['password']=password
    context['timestamp']=timestamp
    context['cloudid']=cloudid
    context['shopid']=shopid
    stringparm=[]
    for key,value in context.items():
        stringparm.append(key+'='+unicode(value))
    stringparm.append('key=gyufytdoiu')
    sign = direct_sign_md5(stringparm)
    print oldsign,sign
    if oldsign == sign:
        newtimestamp = (int(time.time() * 1000))
        timestamp = int(timestamp)
        print newtimestamp,timestamp
        if (newtimestamp - timestamp)/60000 < 5:#五分钟内有效
            user_pass = authenticate(username=username,password=password)
            if user_pass:
                user = cloudtouser.objects.filter(username=username)
                if user.count() > 0:
                    if not user[0].cloudid:
                        user.update(cloudid=cloudid,shopid=shopid)
                return JsonResponse({'res':0})
    return JsonResponse({'res':1})

import sys
from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex

class prpcrypt():
    def __init__(self, key):
        self.key = key
        self.mode = AES.MODE_CBC

    #加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        #这里密钥key 长度必须为16（AES-128）、24（AES-192）、或32（AES-256）Bytes 长度.目前AES-128足够用
        length = 16
        count = len(text)
        add = length - (count % length)
        text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(text)
        #因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        #所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    #解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text.rstrip('\0')