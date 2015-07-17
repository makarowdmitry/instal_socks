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
import datetime
import random
import paramiko
import os


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
		PROXY_USER = request.POST.get('login_socks', '')
		PROXY_PASS = request.POST.get('pass_socks', '')
		vps_lst = request.POST.get('data_socks', '').split(',')
		if len(vps_lst[0])<1:
			return HttpResponse('')



		random_file_pre = str(random.randint(19,9414))


		def create_script_install_proxy(ip,pr_user,pr_pass,random_file_pre):
			create_file = open('media/install_socks'+random_file_pre+'.py','w')
			python_file = '''#! /usr/bin/env python
import os

a = os.system("""
	service iptables stop
	service iptables save
	chkconfig iptables off
	cd /usr/local/src
	yum update -y
	yum install -y mc nano gcc make wget
	wget http://3proxy.ru/0.6.1/3proxy-0.6.1.tgz
	tar -xvzf 3proxy-0.6.1.tgz
	cd 3proxy-0.6.1
	make -f Makefile.Linux
	mkdir /usr/local/etc/3proxy
	mkdir /usr/local/etc/3proxy/bin
	mkdir /usr/local/etc/3proxy/logs
	mkdir /usr/local/etc/3proxy/stat
	cp src/3proxy /usr/local/etc/3proxy/bin
	cp ./scripts/rc.d/proxy.sh /etc/init.d/3proxy
	chkconfig 3proxy on
	""")


def create_conf_proxy(ip_serv,login_proxy,pass_proxy):
	os.chdir("/usr/local/etc/3proxy")
	# os.chdir("/home/tp")
	proxy_conf = """daemon
auth strong
users """+login_proxy+":CL:"+pass_proxy+"""
socks -n -a -p3128 -i"""+ip_serv+" -e"+ip_serv+"""
flush
allow """+login_proxy+"""
	"""
	conf_proxy_create = open("3proxy.cfg","w")
	conf_proxy_create.writelines(proxy_conf)
	conf_proxy_create.close()
	return "ok"

create_conf_proxy("'''+str(ip)+'","'+str(pr_user)+'","'+str(pr_pass)+'''")

b = os.system("""
	reboot
	""")
'''
			create_file.writelines(python_file)
			create_file.close()

		def create_script_install_debian_ubuntu(pr_user,pr_pass,random_file_pre):
			create_file = open('media/install_socks_debian_ubuntu'+random_file_pre+'.sh','w')
			sh_file = '''#!/bin/bash

# to start
# ssh userrrrrrrrrr@hostttttttttttttt "sudo -i; wget http://ptraffer.ru/3proxy.sh && chmod +x 3proxy.sh && ./3proxy.sh"

if (( $EUID != 0 )); then
	echo "Run this script only from root! Continue?";
	read
fi

apt-get update
apt-get install nano wget make gcc mc -y

rm -f 3proxy-0.6.1.tgz
rm -rf ./3proxy-0.6.1

wget http://3proxy.ru/0.6.1/3proxy-0.6.1.tgz
tar -xvzf 3proxy-0.6.1.tgz
cd 3proxy-0.6.1

make -f Makefile.Linux

mkdir /usr/local
mkdir /usr/local/etc
mkdir /usr/local/etc/3proxy
mkdir /usr/local/etc/3proxy/bin
mkdir /usr/local/etc/3proxy/logs
mkdir /usr/local/etc/3proxy/stat

rm -f /usr/local/etc/3proxy/3proxy.cfg

cp src/3proxy /usr/local/etc/3proxy/bin

echo "daemon" >> /usr/local/etc/3proxy/3proxy.cfg
echo "auth strong" >> /usr/local/etc/3proxy/3proxy.cfg

echo "users '''+str(pr_user)+''':CL:'''+str(pr_pass)+'''" >> /usr/local/etc/3proxy/3proxy.cfg

echo "socks -n -a -p3128" >> /usr/local/etc/3proxy/3proxy.cfg
echo "flush" >> /usr/local/etc/3proxy/3proxy.cfg
echo "allow *" >> /usr/local/etc/3proxy/3proxy.cfg

line="* * * * * pgrep 3proxy || /usr/local/etc/3proxy/bin/3proxy /usr/local/etc/3proxy/3proxy.cfg"
(crontab -l | grep -v 3proxy; echo "$line" ) | crontab -

line="@reboot pgrep 3proxy || /usr/local/etc/3proxy/bin/3proxy /usr/local/etc/3proxy/3proxy.cfg"
(crontab -l; echo "$line" ) | crontab -

echo "All ok!"
'''
			create_file.writelines(sh_file)
			create_file.close()

		try:			
			host_remote = re.sub("^\s+|\n|\r|\s+$", '', vps_lst[0])
			username_serv = re.sub("^\s+|\n|\r|\s+$", '', vps_lst[1])
			pass_serv = re.sub("^\s+|\n|\r|\s+$", '', vps_lst[2])				


			client = paramiko.SSHClient()
			client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
			client.connect(host_remote, username=username_serv, password=pass_serv,port=22)
			# stdin, stdout, stderr = client.exec_command('yum install -y python')
			stdin, stdout, stderr = client.exec_command('cat /proc/version')
			os_install = ' '.join(stdout)
			client.close()

			if os_install.find('centos')!= -1:
				create_script_install_proxy(vps_lst[0],PROXY_USER,PROXY_PASS,random_file_pre)
				transport = paramiko.Transport((host_remote, 22))
				transport.connect(username=username_serv, password=pass_serv)
				sftp = paramiko.SFTPClient.from_transport(transport) 

				remotepath = '/root/install_socks'+random_file_pre+'.py'
				localpath = 'media/install_socks'+random_file_pre+'.py'
				sftp.put(localpath, remotepath)
				sftp.close()
				transport.close()
				os.remove('media/install_socks'+random_file_pre+'.py')

				client = paramiko.SSHClient()
				client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				client.connect(host_remote, username=username_serv, password=pass_serv,port=22)
				stdin, stdout, stderr = client.exec_command('python install_socks'+random_file_pre+'.py')
				client.close()

			elif os_install.find('ubuntu')!= -1 or os_install.find('debian')!= -1:
				create_script_install_debian_ubuntu(PROXY_USER,PROXY_PASS,random_file_pre)

				transport = paramiko.Transport((host_remote, 22))
				transport.connect(username=username_serv, password=pass_serv)
				sftp = paramiko.SFTPClient.from_transport(transport) 

				remotepath = '/root/install_socks_debian_ubuntu'+random_file_pre+'.sh'
				localpath = 'media/install_socks_debian_ubuntu'+random_file_pre+'.sh'
				sftp.put(localpath, remotepath)
				sftp.close()
				transport.close()
				os.remove('media/install_socks_debian_ubuntu'+random_file_pre+'.sh')

				client = paramiko.SSHClient()
				client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
				client.connect(host_remote, username=username_serv, password=pass_serv,port=22)
				stdin, stdout, stderr = client.exec_command('sudo -i; chmod +x install_socks_debian_ubuntu'+random_file_pre+'.sh && ./install_socks_debian_ubuntu'+random_file_pre+'.sh')

				client.close()

			
			

			

			# return HttpResponse(aaa)
			return HttpResponse(vps_lst[0])

		except:
			return HttpResponse('Error2')

		return HttpResponse('Error')
				

	



def create_file_ams(request):	
	if request.method == 'POST':		
		login_socks = request.POST.get('login_socks', '')
		pass_socks = request.POST.get('pass_socks', '')
		list_socks_ready = request.POST.get('list_socks_ready', '')		
		for_save = list_socks_ready.split('\n')
		now_time = datetime.datetime.now()
		name_file = 'AMS_socks'+str(datetime.date.today())+str(random.randint(13,9133))+'.txt'

		for l in for_save:
			new_l = l.split(',')
			if len(new_l)>1:
				str_socks = new_l[0]+',3128,SOCKS5,'+login_socks+','+pass_socks+'\n'
				file_ready = open('media/'+name_file,'a').write(str_socks)	
	
		return HttpResponse(name_file)

def download(request,namefile):
		# Create the HttpResponse object with the appropriate CSV header.
		response = HttpResponse(content_type='text/csv')
		response['Content-Type'] = 'application/x-download';
		response['Content-Disposition'] = 'attachment; filename="'+namefile+'"'
		file_read = open('media/'+namefile, 'r').read()
		response.write(file_read)		

		return response


# transport = paramiko.Transport((host_remote, 22))
# transport.connect(username=username_serv, password=pass_serv)
# sftp = paramiko.SFTPClient.from_transport(transport) 

# remotepath = '/root/install_socks'+random_file_pre+'.py'
# localpath = 'media/install_socks'+random_file_pre+'.py'
# sftp.put(localpath, remotepath)
# sftp.close()
# transport.close()

# client = paramiko.SSHClient()
# client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# client.connect(host_remote, username=username_serv, password=pass_serv,port=22)
# stdin, stdout, stderr = client.exec_command('python install_socks'+random_file_pre+'.py')
# client.close()
# os.system('python install_socks.py')