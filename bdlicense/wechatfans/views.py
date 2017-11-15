# -*- coding: UTF-8 -*-
import hashlib
import json
import datetime
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import View
import requests
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
    cloudid = request.GET.get('cloudid')
    thirdpartid = request.GET.get('thirdpart')
    result = {}
    result['error']=1
    iteminfo = CloudConfig.objects.filter(cloudname = cloudname)
    thirdpart = ThridPartyConfig.objects.filter(id = int(thirdpartid))
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

            user.is_staff = 1
            user.is_active = 1
            user.date_joined = datetime.datetime.now().strftime("%Y-%m-%d %H:%I:%S")

            clouduser = cloudtouser.objects.filter(cloudid=cloudid,shopid=shopid)
            #add cloud admin
            if clouduser.count() == 0:
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
        uu = {'res':result}
        return JsonResponse(uu)