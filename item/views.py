# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponse, HttpResponseRedirect
from item.models import *
from django.core.urlresolvers import reverse
from operator import itemgetter
import datetime
from django.db.models import Count, Min, Sum
from django.db import connection
from django.core.mail import send_mail
import json
import re


def index(request):
	return render_to_response('index.html')
	
def preparevps(request):
	if request.method == 'POST':
		raw_list_vps = request.POST.get('raw_list_vps', '')
		pass_pattern = request.POST.get('pass_pattern', '')

		STR_PASS = str(pass_pattern)
		STR_USER = 'root'	
		ip4_re = r'[0-9]+(?:\.[0-9]+){3}'
		pass_re = STR_PASS+r'\s+(?P<pass>\S+)'

		list_ip_search = re.findall(ip4_re, raw_list_vps)
		list_pass_search = re.findall(pass_re, raw_list_vps)

		index_ip4 = raw_list_vps.index(list_ip_search[0])
		index_pass = raw_list_vps.index(list_pass_search[0])


		if len(list_ip_search) != len(list_pass_search):
			print 'К каждому ip должен быть пароль'
		else:
			list_vps = []
			for ip in list_ip_search:
				dict_this = {'ip':ip}
				list_vps.append(dict_this)
			for i,l in enumerate(list_vps):
				l['pass'] = list_pass_search[i]

		return HttpResponse(json.dumps(list_vps), content_type='application/json')

def install_socks(request):
	if request.method == 'POST':
		login_socks = request.POST.get('login_socks', '')
		pass_socks = request.POST.get('pass_socks', '')
		data_socks = request.POST.get('data_socks', '').split(',')[0]
		if len(data_socks)<1:
			return HttpResponse('')

	

	return HttpResponse(data_socks)

def create_file_ams(request):
	if request.method == 'POST':
		login_socks = request.POST.get('login_socks', '')
		pass_socks = request.POST.get('pass_socks', '')
		list_socks_ready = request.POST.get('list_socks_ready', '')
		re.sub("^\s+|\n|\r|\s+$", '', list_socks_ready)

		for_save = list_socks_ready.split('\n')
		name_file = 'data_vps.txt'
		file_ready = open(name_file,'w').writelines(for_save)

	
	return HttpResponse(list_socks_ready)