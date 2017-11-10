# -*- coding: UTF-8 -*-
import hashlib
import json
import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
import requests
from wechatfans.models import TwechatOffline
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
        shopid = request.GET.get('shopid','')
        wechatsign = request.GET.get('wechatsign','')
        timestamp = request.GET.get('timestamp','')
        extend = request.GET.get('extend','')
        type = request.GET.get('wechatAuthvalue','')
        mac = request.GET.get('mac','')
        bmac = request.GET.get('bmac','')
        wlanacport = request.GET.get('wlanacport','')
        portocol = request.GET.get('portocol','')
        authUrl = request.GET.get('authUrl','')
        newwechatsign = md5('df2424efb7548eaa'+extend+timestamp+authUrl+mac+type+bmac+wlanacport+portocol)
        print newwechatsign,wechatsign
        if wechatsign == newwechatsign:#核对签名
            newtimestamp = (int(time.time() * 1000))
            timestamp = int(timestamp)
            print newtimestamp,timestamp,(newtimestamp - timestamp)/300000
            if (newtimestamp - timestamp)/60000 < 5:#五分钟内有效
                context={}
                print '[INFO]type & extend:',type,extend
                if type == '2':#bigwifi
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
    def post(self,request):
        _keys = request.POST.keys()
        result = {}
        result['error']='1'
        cloudid = request.POST.get('cloudid','')
        shopid = request.POST.get('shopid',0)
        usermac = request.POST.get('usermac','')
        type = request.POST.get('type','')
        oid = request.POST.get('oid','')
        openid = request.POST.get('openid','')

        ssid = request.POST.get('ssid','')
        nasid = request.POST.get('nasid','')
        wlanuserip = request.POST.get('wlanuserip','')
        wlanacip = request.POST.get('wlanacip','')
        wlanapmac = request.POST.get('wlanapmac','')
        timestamp = request.POST.get('timestamp','')
        stringparm=[]
        for key in _keys:
            if key != 'sign':
                stringparm.append(key+'='+unicode(request.POST[key]))
        newsign = self.direct_sign_md5(stringparm)
        sign = request.GET.get('sign','')
        print newsign,sign
        if newsign == sign:

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