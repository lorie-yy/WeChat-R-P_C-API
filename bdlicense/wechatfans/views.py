# -*- coding: UTF-8 -*-
import json
from django.http import HttpResponse
from django.shortcuts import render
from django.views.generic import View
import requests
from wechatfans.models import TwechatOffline


class TAuthdata(View):
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