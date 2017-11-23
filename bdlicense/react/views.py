# -*- coding: UTF-8 -*-
from django.shortcuts import render


def Login(request):
    username = request.session.get('username','')
    user_type = request.session.get('user_type','')
    is_superuser = request.session.get('is_superuser','')
    if not username or user_type==0 or is_superuser in[0,'0']:
        return render(request,'license_login.html')
    return render(request,'react/index.html')