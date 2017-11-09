# -*- coding: UTF-8 -*-
import json
import datetime
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
import requests
from wechatfans.models import TwechatOffline



class TAuthdata(View):
    '''
    跳转到吸粉页面
    '''
    def get(self,request):

        cloudid = request.GET.get('cloudid','')
        shopid = request.GET.get('shopid','')
        mac = request.GET.get('mac','')
        bmac = request.GET.get('bmac','')
        wlanacport = request.GET.get('wlanacport','')
        portocol = request.GET.get('portocol','')
        authUrl = request.GET.get('authUrl','')
        context={}

        context['mac'] = mac
        context['bmac'] = bmac
        context['wlanacport'] = wlanacport
        context['portocol'] = portocol
        context['authUrl'] = authUrl

        return render(request,'wechatfans/transition.html',context)

class Getfansnumber(View):
    '''
    接收私有云的查询请求，并调用bigwifi的接口，获取用户关注与否的信息并返回给私有云
    '''
    def get(self,request):
        result = {}
        result['error']='1'
        cloudid = request.GET.get('cloudid','')
        shopid = request.GET.get('shopid','')
        usermac = request.GET.get('usermac','')
        type = request.GET.get('type','')
        oid = request.GET.get('oid','')
        openid = request.GET.get('openid','')

        userlist = TwechatOffline.objects.filter(orderid=oid,openid=openid)
        if userlist.count() == 0:
            userlist = TwechatOffline(orderid=oid,
                                      openid=openid,
                                      shopid=shopid,
                                      usermac=usermac,
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
        apis = self.md5('yft_6l4twiir4jms87w4'+'_'+str(t))

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
    def  md5(self,str):
        import hashlib
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()

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