# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.views.generic import View
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect

# Create your views here.
#主页
class IndexView(View):
    def get(self, request):
        print "in IndexView"

        return HttpResponse('IndexView')
